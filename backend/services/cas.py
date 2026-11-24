"""CAS service tickets are validated once, over TLS, with browser-bound state."""
from datetime import timedelta
import secrets
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

import httpx
from sqlalchemy import delete
from fastapi.responses import RedirectResponse

import config
from errors import forbidden, unauthorized
from models import CasLoginState, User, UserRole
from sqlalchemy.orm import selectinload
from services.sessions import (auth_config, mode, validate_auth_config, digest,
                               STATE_COOKIE, cookie_name, set_cookie, clear_cookie, create_session)
from utils import now


def settings(db):
    if mode(db) != 'sso':
        raise forbidden('当前未启用统一认证')
    cfg = auth_config(db)
    validate_auth_config(cfg)
    return cfg


def service_url(state):
    return config.PUBLIC_BASE_URL.rstrip('/') + '/api/auth/sso/callback?' + urlencode({'state': state})


def start(db):
    cfg = settings(db)
    state = secrets.token_urlsafe(32)
    db.query(CasLoginState).filter(CasLoginState.expires_at <= now()).delete(synchronize_session=False)
    db.add(CasLoginState(state_hash=digest(state), expires_at=now() + timedelta(minutes=10)))
    db.commit()
    response = RedirectResponse(cfg['login_url'] + '?' + urlencode({'service': service_url(state)}), status_code=303)
    set_cookie(response, STATE_COOKIE, state, 600)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


def validate_ticket(cfg, ticket, service):
    try:
        # No proxy environment, redirects, response body logs or unbounded XML.
        with httpx.Client(timeout=10, trust_env=False, follow_redirects=False) as client:
            with client.stream('GET', cfg['validate_url'], params={'ticket': ticket, 'service': service}) as response:
                if response.status_code != 200:
                    raise ValueError('CAS status')
                data = bytearray()
                for chunk in response.iter_bytes(chunk_size=8192):
                    if len(data) + len(chunk) > 65536:
                        raise ValueError('CAS response size')
                    data.extend(chunk)
        document = data.decode('utf-8-sig')
        if '<!DOCTYPE' in document.upper() or '<!ENTITY' in document.upper() or '\x00' in document:
            raise ValueError('CAS XML declarations')
        root = ET.fromstring(document)
        ns = '{http://www.yale.edu/tp/cas}'
        if root.tag != ns + 'serviceResponse' or root.find(ns + 'authenticationFailure') is not None:
            raise ValueError('CAS rejected')
        successes = root.findall(ns + 'authenticationSuccess')
        users = successes[0].findall(ns + 'user') if len(successes) == 1 else []
        if len(users) != 1 or not (users[0].text or '').strip() or len(users[0].text) > 200:
            raise ValueError('CAS identity')
        return users[0].text.strip()
    except (httpx.HTTPError, ValueError, ET.ParseError):
        raise unauthorized('统一认证验票失败，请重新登录') from None


def callback(db, request, ticket, state):
    cfg = settings(db)
    cookie = request.cookies.get(cookie_name(STATE_COOKIE), '')
    if (not state or len(state) > 128 or not state.isascii() or not cookie or not cookie.isascii()
            or not secrets.compare_digest(state, cookie) or not ticket or len(ticket) > 4096
            or not ticket.isascii() or any(c.isspace() for c in ticket) or not ticket.startswith('ST-')):
        raise unauthorized('统一认证回调无效，请重新登录')
    consumed = db.execute(delete(CasLoginState).where(
        CasLoginState.state_hash == digest(state), CasLoginState.expires_at > now()
    ).returning(CasLoginState.state_hash)).scalar_one_or_none()
    db.commit()  # Invalid tickets must also consume the state, including across workers.
    if consumed is None:
        raise unauthorized('统一认证请求已过期或已使用')
    username = validate_ticket(cfg, ticket, service_url(state))
    user = (db.query(User).options(selectinload(User.roles).selectinload(UserRole.org))
            .filter(User.username == username).first())
    if not user or not user.is_active or not user.roles:
        raise forbidden('账号尚未开通或分配身份，请联系组织管理员')
    if user.locked_until and user.locked_until > now():
        raise unauthorized('账号已锁定')
    response = RedirectResponse('/login', status_code=303)
    from services.client_ip import client_ip
    from services.audit import log
    user.last_login_at, user.last_login_ip = now(), client_ip(request)
    create_session(db, user, request, response, auth_mode="sso")
    log(db, None, 'SSO_LOGIN', 'user', user.id, {}, request)
    db.commit()
    clear_cookie(response, STATE_COOKIE)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response
