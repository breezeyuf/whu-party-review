"""Exercise login responses and lock transitions without touching a live database."""
from datetime import datetime, timedelta, timezone
from ipaddress import ip_network
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from database import get_db
from routers import auth
from security import hash_password, verify_password
import services.client_ip as ip_service


NOW = datetime(2026, 10, 24, tzinfo=timezone.utc)
PASSWORD = "CorrectPassword9!"
FAILURE = {"detail": {"code": 40100, "message": "用户名或密码错误", "data": None}}


@pytest.fixture(scope="module")
def user_hash():
    return hash_password(PASSWORD)


@pytest.fixture
def login_case(monkeypatch, user_hash):
    user = SimpleNamespace(
        id=1, username="alice", password_hash=user_hash, is_active=True,
        failed_login_count=0, locked_until=None, token_version=0, must_change_password=False,
    )
    db = Mock()
    query = db.query.return_value.options.return_value.filter.return_value
    query.first.return_value = user
    settings = {"max_failed_login": 5, "lock_minutes": 15, "access_token_minutes": 120, "refresh_token_days": 7}
    monkeypatch.setattr(auth, "get_setting", lambda *a: settings)
    monkeypatch.setattr(auth, "now", lambda: NOW)
    audit = Mock()
    monkeypatch.setattr(auth, "log", audit)
    tokens = Mock(return_value=("access-token", "refresh-token", 7200))
    monkeypatch.setattr(auth, "_tokens", tokens)
    monkeypatch.setattr(auth, "serialize_user_brief", lambda u: {"id": u.id})
    verify = Mock(wraps=verify_password)
    monkeypatch.setattr(auth, "verify_password", verify)
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", ())
    app = FastAPI()
    app.include_router(auth.router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, client=("10.0.0.2", 12345)) as client:
        yield SimpleNamespace(user=user, db=db, query=query, client=client, audit=audit, tokens=tokens, verify=verify)


def attempt(case, password="wrong-password"):
    return case.client.post("/api/auth/login", json={"username": "alice", "password": password})


@pytest.mark.parametrize("state,password", [
    ("unknown", "wrong-password"), ("wrong", "wrong-password"),
    ("inactive", PASSWORD), ("inactive", "wrong-password"),
    ("locked", PASSWORD), ("locked", "wrong-password"),
    ("threshold", "wrong-password"),
])
def test_all_login_rejections_have_identical_status_and_body(login_case, state, password):
    case = login_case
    if state == "unknown":
        case.query.first.return_value = None
    elif state == "inactive":
        case.user.is_active = False
    elif state == "locked":
        case.user.locked_until = NOW + timedelta(minutes=15)
        case.user.failed_login_count = 5
    elif state == "threshold":
        case.user.failed_login_count = 4
    response = attempt(case, password)
    assert response.status_code == 401
    assert response.json() == FAILURE
    case.tokens.assert_not_called()
    case.verify.assert_called_once()
    expected_hash = case.user.password_hash if state in ("wrong", "threshold") else auth._DUMMY_PASSWORD_HASH
    assert case.verify.call_args.args == (password, expected_hash)
    case.db.commit.assert_called_once()
    assert case.audit.call_args.args[2] == "LOGIN_FAILED"
    if state in ("wrong", "inactive"):
        assert case.user.failed_login_count == 1 and case.user.locked_until is None
    elif state in ("locked", "threshold"):
        assert case.user.failed_login_count == 5 and case.user.locked_until == NOW + timedelta(minutes=15)
    else:
        assert case.user.failed_login_count == 0


def test_failures_lock_account_and_correct_password_cannot_bypass_lock(login_case):
    case = login_case
    for failure_count in range(1, 6):
        response = attempt(case)
        assert response.status_code == 401 and response.json() == FAILURE
        assert case.user.failed_login_count == failure_count
    lock_time = case.user.locked_until
    assert lock_time == NOW + timedelta(minutes=15)
    response = attempt(case, PASSWORD)
    assert response.status_code == 401 and response.json() == FAILURE
    assert case.user.failed_login_count == 5 and case.user.locked_until == lock_time
    case.tokens.assert_not_called()
    detail = case.audit.call_args.args[5]
    assert detail["reason"] == "LOCKED" and detail["locked_until"] == lock_time.isoformat()


def test_success_after_expired_lock_resets_failure_state(login_case):
    case = login_case
    case.user.failed_login_count = 5
    case.user.locked_until = NOW - timedelta(seconds=1)
    response = attempt(case, PASSWORD)
    assert response.status_code == 200
    assert response.json()["data"]["access_token"] == "access-token"
    assert case.user.failed_login_count == 0 and case.user.locked_until is None
    assert case.user.last_login_at == NOW
    case.tokens.assert_called_once()


def test_wrong_password_is_counted_after_expired_lock(login_case):
    case = login_case
    case.user.failed_login_count = 5
    case.user.locked_until = NOW - timedelta(seconds=1)
    response = attempt(case)
    assert response.status_code == 401 and response.json() == FAILURE
    assert case.user.failed_login_count == 6
    assert case.user.locked_until == NOW + timedelta(minutes=15)


@pytest.mark.parametrize("trusted,expected", [(False, "10.0.0.2"), (True, "198.51.100.9")])
def test_successful_login_records_ip_using_the_shared_proxy_policy(monkeypatch, login_case, trusted, expected):
    if trusted:
        monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("10.0.0.0/8"),))
    case = login_case
    response = case.client.post("/api/auth/login", json={"username": "alice", "password": PASSWORD},
                                headers={"X-Forwarded-For": "192.0.2.99, 198.51.100.9, 10.0.0.1"})
    assert response.status_code == 200
    assert case.user.last_login_ip == expected
    assert case.audit.call_args.args[1].ip == expected
