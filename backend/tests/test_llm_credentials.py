"""Assert credential destination isolation at the outgoing HTTP boundary."""
from copy import deepcopy
from unittest.mock import Mock

import httpx
import pytest

from ai import llm


SAVED_BASE = "https://saved.example.invalid/v1"


@pytest.fixture
def endpoint(monkeypatch):
    settings = {"base_url": SAVED_BASE, "model": "test-model", "api_key_enc": "synthetic-encrypted-key"}
    saved_key = Mock(return_value="saved-secret")
    requests = []
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    monkeypatch.setattr(llm, "get_setting", lambda *args: settings)
    monkeypatch.setattr(llm, "decrypt_field", saved_key)
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
    saved_key.assert_called_once_with("synthetic-encrypted-key")
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


def test_saved_credential_binding_mismatch_sends_nothing(endpoint):
    db, settings, saved_key, requests = endpoint
    settings["api_key_base_url"] = SAVED_BASE
    settings["base_url"] = "https://changed.example.invalid/v1"
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {})
    assert result is None and error and requests == []
    saved_key.assert_not_called()


@pytest.mark.parametrize("patch", [
    {"base_url": "https://changed.example.invalid/v1"},
    {"base_url": "https://changed.example.invalid/v1", "api_key": None},
])
def test_saving_changed_destination_without_new_key_is_rejected(monkeypatch, patch):
    from types import SimpleNamespace
    from errors import AppError
    from services import settings as service

    row = SimpleNamespace(value={"base_url": SAVED_BASE, "api_key_enc": "old-encrypted"})
    original = deepcopy(row.value)
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    with pytest.raises(AppError, match="重新填写密钥"):
        service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), {"ai": patch})
    assert row.value == original
    db.flush.assert_not_called()


@pytest.mark.parametrize("key", ["new-secret", ""])
def test_saving_changed_destination_rebinds_only_explicit_key(monkeypatch, key):
    from types import SimpleNamespace
    from services import settings as service

    row = SimpleNamespace(value={"base_url": SAVED_BASE, "api_key_enc": "old-encrypted"})
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    monkeypatch.setattr(service, "encrypt_field", lambda raw: "encrypted:" + raw)
    monkeypatch.setattr(service, "public_settings", lambda _: {})
    new_base = "https://changed.example.invalid/v1"
    body = {"ai": {"base_url": new_base, "api_key": key}}
    original = deepcopy(body)
    service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), body)
    assert row.value["api_key_enc"] == ("encrypted:" + key if key else "")
    assert row.value["api_key_base_url"] == (new_base if key else "")
    assert body == original


def test_saving_other_model_options_preserves_credential_destination(monkeypatch):
    from types import SimpleNamespace
    from services import settings as service

    row = SimpleNamespace(value={"base_url": SAVED_BASE, "api_key_enc": "old-encrypted"})
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    monkeypatch.setattr(service, "public_settings", lambda _: {})
    service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), {"ai": {"model": "new-model"}})
    assert row.value["api_key_enc"] == "old-encrypted"
    assert row.value["api_key_base_url"] == SAVED_BASE


def test_concurrent_settings_change_cannot_pair_new_key_with_old_destination(monkeypatch, endpoint):
    db, settings, saved_key, requests = endpoint
    old = {**settings, "api_key_base_url": SAVED_BASE}
    new_base = "https://replacement.example.invalid/v1"
    new = {**old, "base_url": new_base, "api_key_base_url": new_base, "api_key_enc": "new-encrypted-key"}
    # The next settings read sees an administrator's committed update. Request
    # construction must never make that second read to obtain another URL's key.
    read = Mock(side_effect=[old, new])
    monkeypatch.setattr(llm, "get_setting", read)
    saved_key.side_effect = lambda encrypted: "saved-secret" if encrypted == old["api_key_enc"] else "new-secret"
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {})
    assert error is None and result == {"issues": []}
    assert str(requests[0].url) == SAVED_BASE + "/chat/completions"
    assert requests[0].headers["Authorization"] == "Bearer saved-secret"
    read.assert_called_once_with(db, "ai", {})


def test_internal_credential_fields_in_override_cannot_replace_saved_snapshot(endpoint):
    db, _, saved_key, requests = endpoint
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {}, {
        "api_key_enc": "unrelated-encrypted-key", "api_key_base_url": "https://unrelated.invalid",
    })
    assert error is None and result == {"issues": []}
    assert requests[0].headers["Authorization"] == "Bearer saved-secret"
    saved_key.assert_called_once_with("synthetic-encrypted-key")


@pytest.mark.parametrize("binding", [None, "", SAVED_BASE, SAVED_BASE + "/"])
def test_legacy_or_normalized_binding_accepts_original_destination(endpoint, binding):
    db, settings, _, requests = endpoint
    settings["api_key_base_url"] = binding
    assert llm.chat_json(db, "CONTENT_CHECK", {})[:2] == ({"issues": []}, None)
    assert requests[0].headers["Authorization"] == "Bearer saved-secret"


@pytest.mark.parametrize("override", [7, False, [], "invalid"])
def test_nonobject_override_is_rejected_before_reading_or_sending(endpoint, override):
    from errors import AppError

    db, _, saved_key, requests = endpoint
    with pytest.raises(AppError) as exc:
        llm.chat_json(db, "CONTENT_CHECK", {}, override)
    assert exc.value.status_code == 422
    assert requests == []
    saved_key.assert_not_called()


@pytest.mark.parametrize("field", ["base_url", "api_key"])
@pytest.mark.parametrize("value", [7, False, [], {}])
def test_invalid_override_credential_type_is_422_with_no_request(endpoint, field, value):
    from errors import AppError
    from services.settings import test_ai

    db, _, saved_key, requests = endpoint
    with pytest.raises(AppError) as exc:
        test_ai(db, "llm", {field: value})
    assert exc.value.status_code == 422
    assert requests == []
    saved_key.assert_not_called()


@pytest.mark.parametrize("field", ["base_url", "api_key"])
@pytest.mark.parametrize("value", [7, False, [], {}])
def test_invalid_saved_credential_patch_is_422_without_mutating_configuration(monkeypatch, field, value):
    from types import SimpleNamespace
    from errors import AppError
    from services import settings as service

    row = SimpleNamespace(value={"base_url": SAVED_BASE, "api_key_enc": "old-encrypted"})
    original = deepcopy(row.value)
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    encrypt = Mock()
    monkeypatch.setattr(service, "encrypt_field", encrypt)
    with pytest.raises(AppError) as exc:
        service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), {"ai": {field: value}})
    assert exc.value.status_code == 422
    assert row.value == original
    encrypt.assert_not_called()
    db.flush.assert_not_called()


@pytest.mark.parametrize("patch", [None, False, [], "invalid"])
def test_ai_patch_must_be_object(monkeypatch, patch):
    from types import SimpleNamespace
    from errors import AppError
    from services import settings as service

    row = SimpleNamespace(value={"base_url": SAVED_BASE})
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    with pytest.raises(AppError) as exc:
        service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), {"ai": patch})
    assert exc.value.status_code == 422
    assert row.value == {"base_url": SAVED_BASE}
    db.flush.assert_not_called()


def test_none_fields_preserve_legacy_saved_credentials(monkeypatch):
    from types import SimpleNamespace
    from services import settings as service

    row = SimpleNamespace(value={"base_url": SAVED_BASE, "api_key_enc": "old-encrypted"})
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    monkeypatch.setattr(service, "public_settings", lambda _: {})
    service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), {
        "ai": {"base_url": None, "api_key": None, "model": "replacement-model"},
    })
    assert row.value["base_url"] == SAVED_BASE
    assert row.value["api_key_base_url"] == SAVED_BASE
    assert row.value["api_key_enc"] == "old-encrypted"


@pytest.mark.parametrize("key", ["replacement-secret", ""])
def test_saved_destination_change_uses_only_new_explicit_credentials(monkeypatch, endpoint, key):
    from types import SimpleNamespace
    from services import settings as service

    db, config, decrypt, requests = endpoint
    row = SimpleNamespace(value=deepcopy(config))
    db.query.return_value.filter.return_value.first.return_value = row
    monkeypatch.setattr(service, "encrypt_field", lambda raw: "encrypted:" + raw)
    monkeypatch.setattr(service, "public_settings", lambda _: {})
    monkeypatch.setattr(llm, "get_setting", lambda *args: row.value)
    decrypt.return_value = key
    new_base = "https://replacement.example.invalid/v1"
    service.update_settings(db, SimpleNamespace(role="SYS_ADMIN", id=1), {
        "ai": {"base_url": new_base, "api_key": key},
    })
    db.query.return_value.filter.return_value.first.return_value = None
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {})
    assert error is None and result == {"issues": []}
    assert str(requests[0].url) == new_base + "/chat/completions"
    assert requests[0].headers.get("Authorization") == (f"Bearer {key}" if key else None)
    if key:
        decrypt.assert_called_once_with("encrypted:" + key)
    else:
        decrypt.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("base_url", 7), ("api_key_base_url", []), ("api_key_enc", False),
])
def test_malformed_legacy_saved_values_fail_without_request(endpoint, field, value):
    db, settings, saved_key, requests = endpoint
    settings[field] = value
    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {})
    assert result is None and error
    assert requests == []
    saved_key.assert_not_called()


def test_public_settings_hide_credential_ciphertext_and_internal_binding(monkeypatch):
    from services import settings as service

    config = {"base_url": SAVED_BASE, "api_key_enc": "old-encrypted", "api_key_base_url": SAVED_BASE,
              "llm_enabled": True, "model": "test-model"}
    original = deepcopy(config)
    monkeypatch.setattr(service, "get_setting", lambda db, key, default: config if key == "ai" else {})
    monkeypatch.setattr(service, "available_engines", lambda: [])
    result = service.public_settings(Mock())["ai"]
    assert "api_key_enc" not in result and "api_key_base_url" not in result
    assert result["api_key_set"] is True and result["base_url"] == SAVED_BASE
    assert config == original
