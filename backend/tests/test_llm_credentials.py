"""Assert credential destination isolation at the outgoing HTTP boundary."""
from copy import deepcopy
from unittest.mock import Mock

import httpx
import pytest

from ai import llm


SAVED_BASE = "https://saved.example.invalid/v1"


@pytest.fixture
def endpoint(monkeypatch):
    settings = {"base_url": SAVED_BASE, "model": "test-model"}
    saved_key = Mock(return_value="saved-secret")
    requests = []
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    monkeypatch.setattr(llm, "llm_config", lambda _: settings)
    monkeypatch.setattr(llm, "llm_api_key", saved_key)
    client_class = httpx.Client

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={
            "choices": [{"message": {"content": '{"issues": []}'}}],
        })

    monkeypatch.setattr(llm.httpx, "Client", lambda **kwargs: client_class(
        transport=httpx.MockTransport(respond), **kwargs,
    ))
    return db, settings, saved_key, requests


@pytest.mark.parametrize("override", [
    None, {}, {"model": "other-model"}, {"max_attempts": 1},
    {"base_url": SAVED_BASE}, {"base_url": SAVED_BASE + "/"},
    {"base_url": None}, {"api_key": None},
])
def test_unchanged_endpoint_can_reuse_saved_key(endpoint, override):
    db, settings, saved_key, requests = endpoint
    original = deepcopy(settings)
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {}, override)
    assert error is None and result == {"issues": []}
    assert str(requests[0].url) == SAVED_BASE + "/chat/completions"
    assert requests[0].headers["Authorization"] == "Bearer saved-secret"
    saved_key.assert_called_once_with(db)
    assert settings == original


@pytest.mark.parametrize("base", [
    "https://other.example.invalid/v1",
    "http://saved.example.invalid/v1",
    "https://saved.example.invalid/other-tenant/v1",
    "https://saved.example.invalid:8443/v1",
    "https://saved.example.invalid@other.example.invalid/v1",
])
@pytest.mark.parametrize("key_patch", [{}, {"api_key": None}])
def test_changed_endpoint_without_explicit_key_sends_nothing(endpoint, base, key_patch):
    db, settings, saved_key, requests = endpoint
    original = deepcopy(settings)
    result, error, elapsed = llm.chat_json(
        db, "CONTENT_CHECK", {}, {"base_url": base, **key_patch},
    )
    assert result is None and error and elapsed == 0
    assert "saved-secret" not in error
    assert requests == []
    saved_key.assert_not_called()
    assert settings == original


@pytest.mark.parametrize("base", [SAVED_BASE, "https://other.example.invalid/v1"])
@pytest.mark.parametrize("key", ["replacement-secret", ""])
def test_explicit_key_never_falls_back_to_saved_key(endpoint, base, key):
    db, settings, saved_key, requests = endpoint
    override = {"base_url": base, "api_key": key}
    original = deepcopy(override)
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {}, override)
    assert error is None and result == {"issues": []}
    assert str(requests[0].url) == base + "/chat/completions"
    assert requests[0].headers.get("Authorization") == (f"Bearer {key}" if key else None)
    saved_key.assert_not_called()
    assert override == original
    assert settings["base_url"] == SAVED_BASE


def test_settings_connection_test_reports_changed_endpoint_error(endpoint):
    from services.settings import test_ai

    db, _, saved_key, requests = endpoint
    result = test_ai(db, "llm", {"base_url": "https://other.example.invalid/v1"})
    assert result["ok"] is False
    assert result["message"]
    assert requests == []
    saved_key.assert_not_called()
