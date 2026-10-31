from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session, selectinload

from config import DEMO_LOGIN_HINT, DEMO_PASSWORD
from database import get_db
from deps import Actor, get_current_user, get_current_user_allow_must_change
from errors import unauthorized, unprocessable
from models import User, UserRole
from schemas.common import ok
from security import hash_password, password_ok, verify_password
from services.sessions import (mode, require_demo, check_unsafe, create_session, revoke_cookie, clear_cookie)
from services.audit import log
from services.client_ip import client_ip
from utils import get_setting, now, serialize_user_brief
from datetime import timedelta
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])
# Never corresponds to an account; one bcrypt check also runs for unknown users.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))
_LOGIN_FAILURE = "用户名或密码错误"


@router.get("/config")
def configuration(db: Session = Depends(get_db)):
    return ok({"mode": mode(db)})


@router.get('/sso/start')
def sso_start(db: Session = Depends(get_db)):
    from services.cas import start
    return start(db)


@router.get('/sso/callback')
def sso_callback(request: Request, ticket: str = '', state: str = '', db: Session = Depends(get_db)):
    from services.cas import callback
    return callback(db, request, ticket, state)


@router.post("/login")
def login(body: dict, request: Request, response: Response, db: Session = Depends(get_db)):
    check_unsafe(request)
    require_demo(db)
    username = (body or {}).get("username") or ""
    password = (body or {}).get("password") or ""
    username = username if isinstance(username, str) else ""
    password = password if isinstance(password, str) else ""
    user = db.query(User).options(selectinload(User.roles).selectinload(UserRole.org), selectinload(User.org)).filter(User.username == username).first()
    sec = get_setting(db, "security", {"max_failed_login": 5, "lock_minutes": 15, "access_token_minutes": 120, "refresh_token_days": 7})
    is_locked = bool(user and user.locked_until and user.locked_until > now())
    check_hash = user.password_hash if user and user.is_active and not is_locked else _DUMMY_PASSWORD_HASH
    password_valid = verify_password(password, check_hash)
    if not user or not password_valid or not user.is_active or is_locked:
        detail = {"username": username}
        if user:
            if is_locked:
                detail["reason"] = "LOCKED"
            else:
                user.failed_login_count = (user.failed_login_count or 0) + 1
                max_failed = int(sec.get("max_failed_login", 5))
                detail["remain"] = max(0, max_failed - user.failed_login_count)
                detail["reason"] = "BAD_PASSWORD" if user.is_active else "INACTIVE"
                if user.failed_login_count >= max_failed:
                    user.locked_until = now() + timedelta(minutes=int(sec.get("lock_minutes", 15)))
                    detail["reason"] = "LOCKED"
            if user.locked_until:
                detail["locked_until"] = user.locked_until.isoformat()
        else:
            detail["reason"] = "UNKNOWN_USER"
        log(db, None, "LOGIN_FAILED", "user", user.id if user else None, detail, request)
        db.commit()
        raise unauthorized(_LOGIN_FAILURE)
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now()
    user.last_login_ip = client_ip(request)
    expires_in = create_session(db, user, request, response)
    log(db, type("A", (), {"id": user.id, "username": user.username, "role": None, "ip": client_ip(request), "user_agent": request.headers.get("user-agent")})(),
        "LOGIN", "user", user.id, {}, request)
    db.commit()
    response.headers['Cache-Control'] = 'no-store'
    return ok({
        "expires_in": expires_in,
        "must_change_password": user.must_change_password, "user": serialize_user_brief(user),
    })


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    check_unsafe(request)
    revoke_cookie(db, request)
    db.commit()
    clear_cookie(response)
    return ok({})


@router.get("/me")
def me(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user_allow_must_change)):
    from models import Archive
    from services.scope import scoped_archives
    user = serialize_user_brief(actor.user)
    user["active_role"] = {"role": actor.role, "org_id": actor.org_id}
    scope_type = {"STUDENT": "SELF", "BRANCH_REVIEWER": "BRANCH", "CROSS_REVIEWER": "CROSS",
                  "COLLEGE_REVIEWER": "COLLEGE", "ORG_ADMIN": "SCHOOL", "SYS_ADMIN": "SCHOOL"}.get(actor.role)
    user["scope"] = {"type": scope_type, "org_ids": [actor.org_id]}
    arch = db.query(Archive).filter(Archive.student_user_id == actor.id).first()
    user["archive_id"] = arch.id if arch else None
    user["auth_mode"] = mode(db)
    user["must_change_password"] = mode(db) == "demo" and actor.user.must_change_password
    return ok(user)


@router.put("/password")
def change_password(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user_allow_must_change)):
    require_demo(db)
    old = (body or {}).get("old_password") or ""
    new = (body or {}).get("new_password") or ""
    if not verify_password(old, actor.user.password_hash):
        raise unauthorized("原密码不正确")
    err = password_ok(new, old)
    if err:
        raise unprocessable(err)
    actor.user.password_hash = hash_password(new)
    actor.user.must_change_password = False
    actor.user.token_version = (actor.user.token_version or 0) + 1
    db.flush()
    # The client immediately logs in again; persist before sending a success response.
    db.commit()
    return ok({})


@router.get("/demo-accounts")
def demo_accounts(db: Session = Depends(get_db)):
    if mode(db) != "demo" or not DEMO_LOGIN_HINT:
        return ok([])
    users = db.query(User).options(selectinload(User.roles)).filter(User.is_demo.is_(True)).all()
    if not users:
        return ok([])
    out = []
    for u in users:
        out.append({
            "username": u.username, "real_name": u.real_name,
            "roles": [r.role for r in u.roles], "password_hint": DEMO_PASSWORD,
        })
    return ok(out)
