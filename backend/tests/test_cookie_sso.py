from datetime import timedelta
from urllib.parse import urlsplit, parse_qs
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

import config
from database import get_db
from models import AuthSession, CasLoginState, SystemSetting
from routers import auth
from security import hash_password
from services import sessions, cas
from services.settings import update_settings
from services.users import reset_user_password
from errors import AppError
from utils import now
from .pg_fixtures import pg_schema, case

PASSWORD = 'CookieOnlyPassword9!'
HEADERS = {'X-Requested-With': 'party-review'}


@pytest.fixture
def client(case, monkeypatch):
    monkeypatch.setattr(config, 'PUBLIC_BASE_URL', '')
    monkeypatch.setattr(config, 'DEPLOYMENT_MODE', 'desktop')
    case.student.user.password_hash = hash_password(PASSWORD)
    case.db.flush()
    app = FastAPI()
    app.include_router(auth.router, prefix='/api')
    app.dependency_overrides[get_db] = lambda: case.db
    with TestClient(app, headers=HEADERS) as value:
        yield value


def login(client):
    return client.post('/api/auth/login', json={'username': 'student_a', 'password': PASSWORD})


def test_cookie_only_database_hash_and_logout(client, case):
    response = login(client)
    assert response.status_code == 200
    assert 'access_token' not in response.json()['data']
    assert 'refresh_token' not in response.json()['data']
    assert 'HttpOnly' in response.headers['set-cookie']
    assert 'SameSite=lax' in response.headers['set-cookie']
    token = client.cookies.get(sessions.COOKIE)
    row = case.db.query(AuthSession).one()
    assert row.token_hash == sessions.digest(token) and row.token_hash != token
    assert client.get('/api/auth/me').status_code == 200
    assert client.post('/api/auth/logout').status_code == 200
    assert case.db.query(AuthSession).count() == 0
    assert client.get('/api/auth/me').status_code == 401


def test_relogin_replaces_previous_browser_session(client, case):
    assert login(client).status_code == 200
    old = client.cookies.get(sessions.COOKIE)
    assert login(client).status_code == 200
    assert client.cookies.get(sessions.COOKIE) != old
    assert case.db.query(AuthSession).count() == 1
    assert client.get('/api/auth/me', headers={'Cookie': sessions.COOKIE + '=' + old}).status_code == 401


@pytest.mark.parametrize('change', ['expired', 'disabled', 'version', 'mode'])
def test_old_sessions_rejected(client, case, change):
    assert login(client).status_code == 200
    if change == 'expired':
        case.db.query(AuthSession).one().expires_at = now() - timedelta(seconds=1)
    elif change == 'disabled':
        case.student.user.is_active = False
    elif change == 'version':
        case.student.user.token_version += 1
    else:
        case.db.add(SystemSetting(key='auth', value={'mode': 'sso'}, updated_at=now()))
    case.db.flush()
    assert client.get('/api/auth/me').status_code == 401


def test_bearer_no_longer_authenticates(client):
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer old-jwt'}).status_code == 401


def test_login_and_cookie_writes_reject_csrf(client):
    client.headers.pop('X-Requested-With')
    assert login(client).status_code == 403
    client.headers.update(HEADERS)
    assert login(client).status_code == 200
    assert client.post('/api/auth/logout', headers={'Origin': 'https://attacker.invalid'}).status_code == 403
    assert client.get('/api/auth/me').status_code == 200
    client.headers.pop('X-Requested-With')
    assert client.post('/api/auth/logout').status_code == 403


def setup_sso(case, monkeypatch):
    monkeypatch.setattr(config, 'PUBLIC_BASE_URL', 'https://testserver')
    update_settings(case.db, case.sys_admin, {'auth': {'mode': 'sso',
        'login_url': 'https://cas.school.test/login', 'validate_url': 'https://cas.school.test/serviceValidate'}})
    case.db.flush()


def begin(client):
    response = client.get('https://testserver/api/auth/sso/start', follow_redirects=False)
    assert response.status_code == 303 and 'Secure' in response.headers['set-cookie']
    assert response.headers['set-cookie'].startswith('__Host-prw_cas_state=')
    assert 'Path=/' in response.headers['set-cookie'] and 'Domain=' not in response.headers['set-cookie']
    service = parse_qs(urlsplit(response.headers['location']).query)['service'][0]
    return service, parse_qs(urlsplit(service).query)['state'][0]


def test_sso_success_browser_binding_replay_and_no_password_gate(client, case, monkeypatch):
    setup_sso(case, monkeypatch)
    case.student.user.must_change_password = True
    case.db.flush()
    validate = Mock(return_value='student_a')
    monkeypatch.setattr(cas, 'validate_ticket', validate)
    service, state = begin(client)
    assert client.get(service + '&ticket=ST-synthetic', follow_redirects=False).status_code == 303
    validate.assert_called_once()
    assert validate.call_args.args[2] == service
    row = case.db.query(AuthSession).one()
    assert row.auth_mode == 'sso'
    me = client.get('https://testserver/api/auth/me')
    assert me.status_code == 200 and not me.json()['data']['must_change_password']
    assert client.get(service + '&ticket=ST-synthetic', follow_redirects=False).status_code == 401


@pytest.mark.parametrize('identity', ['unknown-person', 'student_b'])
def test_unprovisioned_or_disabled_sso_cannot_login(client, case, monkeypatch, identity):
    setup_sso(case, monkeypatch)
    case.student_b.user.is_active = False
    case.db.flush()
    monkeypatch.setattr(cas, 'validate_ticket', lambda *args: identity)
    service, state = begin(client)
    assert client.get(service + '&ticket=ST-synthetic', follow_redirects=False).status_code == 403
    assert case.db.query(AuthSession).count() == 0
    assert case.db.query(CasLoginState).count() == 0


def test_sso_state_missing_or_wrong_browser_never_validates(client, case, monkeypatch):
    setup_sso(case, monkeypatch)
    validate = Mock()
    monkeypatch.setattr(cas, 'validate_ticket', validate)
    service, state = begin(client)
    client.cookies.clear()
    assert client.get(service + '&ticket=ST-synthetic', follow_redirects=False).status_code == 401
    validate.assert_not_called()


def test_sso_disables_local_login_and_reset_and_invalidates_sessions(client, case, monkeypatch):
    assert login(client).status_code == 200
    setup_sso(case, monkeypatch)
    assert case.db.query(AuthSession).count() == 0
    assert login(client).status_code == 403
    with pytest.raises(AppError):
        reset_user_password(case.db, case.student.user)
    assert client.get('/api/auth/config').json()['data'] == {'mode': 'sso'}


def test_password_change_invalidates_cookie(client, case):
    assert login(client).status_code == 200
    response = client.put('/api/auth/password', json={'old_password': PASSWORD, 'new_password': 'NewPassword123!'})
    assert response.status_code == 200
    assert client.get('/api/auth/me').status_code == 401


def test_sso_new_user_has_no_local_password(client, case, monkeypatch):
    from services.users import create_user
    setup_sso(case, monkeypatch)
    user, password = create_user(case.db, case.sys_admin, {'username': 'new_sso_user',
        'real_name': '虚构用户', 'org_id': case.school.id, 'roles': [{'role': 'SYS_ADMIN', 'org_id': case.school.id}]})
    assert password is None and user.password_hash == '!SSO_ONLY' and not user.must_change_password


def test_mode_switch_during_ticket_validation_cannot_issue_demo_session(client, case, monkeypatch):
    setup_sso(case, monkeypatch)
    def validate(*args):
        update_settings(case.db, case.sys_admin, {'auth': {'mode': 'demo'}})
        return 'student_a'
    monkeypatch.setattr(cas, 'validate_ticket', validate)
    service, _ = begin(client)
    assert client.get(service + '&ticket=ST-test', follow_redirects=False).status_code == 401
    assert case.db.query(AuthSession).count() == 0


def test_expired_cas_state_is_not_sent_for_validation(client, case, monkeypatch):
    setup_sso(case, monkeypatch)
    service, _ = begin(client)
    case.db.query(CasLoginState).one().expires_at = now() - timedelta(seconds=1)
    case.db.flush()
    validate = Mock()
    monkeypatch.setattr(cas, 'validate_ticket', validate)
    assert client.get(service + '&ticket=ST-test', follow_redirects=False).status_code == 401
    validate.assert_not_called()


@pytest.mark.parametrize('url', ['https://[bad', 'http://cas.test/login', 'https://cas.test:0/login',
    'https://cas.test:bad/login', 'https://cas.test/login?redirect=x'])
def test_invalid_sso_configuration_preserves_sessions(client, case, monkeypatch, url):
    assert login(client).status_code == 200
    monkeypatch.setattr(config, 'PUBLIC_BASE_URL', 'https://testserver')
    with pytest.raises(AppError):
        update_settings(case.db, case.sys_admin, {'auth': {'mode': 'sso',
            'login_url': url, 'validate_url': 'https://cas.test/serviceValidate'}})
    assert case.db.query(AuthSession).count() == 1


@pytest.mark.parametrize('group', ['ai', 'ocr_vision'])
def test_model_settings_reject_public_destination_before_saving(client, case, group):
    from copy import deepcopy
    row = case.db.query(SystemSetting).filter(SystemSetting.key == group).first()
    before = deepcopy(row.value) if row else None
    with pytest.raises(AppError):
        update_settings(case.db, case.sys_admin, {group: {'base_url': 'https://8.8.8.8/v1', 'api_key': 'synthetic-key'}})
    row = case.db.query(SystemSetting).filter(SystemSetting.key == group).first()
    assert (row.value if row else None) == before
