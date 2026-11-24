"""Opaque, revocable browser sessions; raw credentials never enter the database."""
from datetime import timedelta
import hashlib
import secrets
from urllib.parse import urlsplit

import config
from errors import forbidden, unauthorized, unprocessable
from models import AuthSession
from utils import get_setting, now

COOKIE = 'prw_session'
STATE_COOKIE = 'prw_cas_state'


def auth_config(db):
    value = get_setting(db, 'auth', {})
    if not isinstance(value, dict):
        raise forbidden('认证配置无效，请联系管理员')
    return {'mode': 'demo', **value}


def mode(db):
    value = auth_config(db).get('mode')
    if value not in ('demo', 'sso'):
        raise forbidden('认证配置无效，请联系管理员')
    return value


def require_demo(db):
    if mode(db) != 'demo':
        raise forbidden('统一认证模式不提供本地密码操作')


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def secure_cookie():
    return config.DEPLOYMENT_MODE == 'server' or config.PUBLIC_BASE_URL.startswith('https://')


def cookie_name(name):
    return '__Host-' + name if secure_cookie() else name


def set_cookie(response, name, value, seconds):
    response.set_cookie(cookie_name(name), value, max_age=seconds, httponly=True,
                        secure=secure_cookie(), samesite='lax', path='/' if secure_cookie() else '/api')


def clear_cookie(response, name=COOKIE):
    response.delete_cookie(cookie_name(name), path='/' if secure_cookie() else '/api', httponly=True,
                           secure=secure_cookie(), samesite='lax')


def check_unsafe(request):
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return
    # A non-simple header makes cross-origin browser writes require a CORS
    # preflight. Never accept form posts, even when Origin is absent.
    if request.headers.get('x-requested-with') != 'party-review':
        raise forbidden('请求来源校验失败，请刷新页面')
    origin = request.headers.get('origin')
    allowed = {config.PUBLIC_BASE_URL.rstrip('/')} if config.PUBLIC_BASE_URL else {
        str(request.base_url).rstrip('/'), *config.CORS_ORIGINS}
    if origin and origin not in allowed:
        raise forbidden('不允许跨站操作')
    if request.headers.get('sec-fetch-site') == 'cross-site':
        raise forbidden('不允许跨站操作')


def revoke_cookie(db, request):
    token = request.cookies.get(cookie_name(COOKIE), '')
    if token:
        db.query(AuthSession).filter(AuthSession.token_hash == digest(token)).delete(synchronize_session=False)


def create_session(db, user, request, response, *, auth_mode="demo"):
    if mode(db) != auth_mode:
        raise unauthorized("登录方式已变化，请重新登录")
    revoke_cookie(db, request)
    db.query(AuthSession).filter(AuthSession.expires_at <= now()).delete(synchronize_session=False)
    sec = get_setting(db, 'security', {})
    minutes = max(1, min(1440, int(sec.get('access_token_minutes') or 120)))
    token = secrets.token_urlsafe(48)
    db.add(AuthSession(token_hash=digest(token), user_id=user.id, token_version=user.token_version,
                       auth_mode=auth_mode, created_at=now(), expires_at=now() + timedelta(minutes=minutes)))
    db.flush()
    set_cookie(response, COOKIE, token, minutes * 60)
    return minutes * 60


def session_user_id(db, request):
    check_unsafe(request)
    token = request.cookies.get(cookie_name(COOKIE), '')
    if not token or len(token) > 128:
        raise unauthorized()
    session = db.query(AuthSession).filter(AuthSession.token_hash == digest(token),
                                          AuthSession.expires_at > now()).first()
    if session is None or session.auth_mode != mode(db):
        raise unauthorized('登录已过期，请重新登录')
    return session


def validate_auth_config(value):
    if value.get('mode') not in ('demo', 'sso'):
        raise unprocessable('认证模式须为 demo 或 sso')
    if value['mode'] == 'demo':
        return
    urls = []
    for key in ('login_url', 'validate_url'):
        raw = value.get(key)
        if not isinstance(raw, str):
            raise unprocessable('请配置统一认证登录和验票地址')
        try:
            parsed = urlsplit(raw)
            valid_port = parsed.port is None or 1 <= parsed.port <= 65535
        except ValueError:
            raise unprocessable('统一认证地址格式无效') from None
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                or not valid_port or parsed.query or parsed.fragment or any(c.isspace() for c in raw) or '\\' in raw):
            raise unprocessable('统一认证地址须为不含查询参数的 HTTPS 地址')
        urls.append(parsed.netloc)
    if urls[0] != urls[1]:
        raise unprocessable('统一认证登录和验票地址必须同源')
    try:
        base = urlsplit(config.PUBLIC_BASE_URL)
        if base.port is not None and not 1 <= base.port <= 65535:
            raise ValueError()
    except ValueError:
        raise unprocessable('PUBLIC_BASE_URL 格式无效') from None
    if (base.scheme != 'https' or not base.hostname or base.username or base.password
            or base.path not in ('', '/') or base.query or base.fragment):
        raise unprocessable('统一认证需要配置 HTTPS PUBLIC_BASE_URL')
