from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, selectinload

from config import DEMO_LOGIN_HINT, DEMO_PASSWORD
from database import get_db
from deps import Actor, get_current_user, get_current_user_allow_must_change
from errors import unauthorized, unprocessable
from models import RevokedToken, User, UserRole
from schemas.common import ok
from security import decode_token, hash_password, issue_token, password_ok, verify_password
from services.audit import log
from services.client_ip import client_ip
from utils import get_setting, now, serialize_user_brief
from datetime import datetime, timedelta, timezone
import secrets
import jwt

router = APIRouter(prefix="/auth", tags=["auth"])
# Never corresponds to an account; one bcrypt check also runs for unknown users.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))
_LOGIN_FAILURE = "用户名或密码错误"


def _tokens(user: User, minutes: int, days: int):
    access, jti_a, exp_a = issue_token(user.id, user.token_version, "access", minutes=minutes)
    refresh, jti_r, exp_r = issue_token(user.id, user.token_version, "refresh", days=days)
    return access, refresh, int(minutes * 60)


@router.post("/login")
def login(body: dict, request: Request, db: Session = Depends(get_db)):
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
    access, refresh, expires_in = _tokens(user, int(sec.get("access_token_minutes", 120)), int(sec.get("refresh_token_days", 7)))
    log(db, type("A", (), {"id": user.id, "username": user.username, "role": None, "ip": client_ip(request), "user_agent": request.headers.get("user-agent")})(),
        "LOGIN", "user", user.id, {}, request)
    return ok({
        "access_token": access, "refresh_token": refresh, "token_type": "bearer", "expires_in": expires_in,
        "must_change_password": user.must_change_password, "user": serialize_user_brief(user),
    })


@router.post("/logout")
def logout(request: Request, body: dict | None = None, db: Session = Depends(get_db),
           actor: Actor = Depends(get_current_user_allow_must_change)):
    body = body or {}
    tokens = []
    auth = request.headers.get("authorization") if request else None
    if auth and auth.lower().startswith("bearer "):
        tokens.append(("access", auth.split(" ", 1)[1]))
    if body.get("refresh_token"):
        tokens.append(("refresh", body["refresh_token"]))
    for typ, tok in tokens:
        try:
            p = decode_token(tok)
            db.merge(RevokedToken(jti=p["jti"], user_id=int(p["sub"]), token_type=p.get("typ") or typ,
                                  expires_at=datetime.fromtimestamp(p["exp"], tz=timezone.utc) if isinstance(p["exp"], (int, float)) else now(),
                                  revoked_at=now()))
        except Exception:
            pass
    db.flush()
    return ok({})


@router.post("/refresh")
def refresh(body: dict, db: Session = Depends(get_db)):
    token = (body or {}).get("refresh_token")
    if not token:
        raise unauthorized()
    try:
        p = decode_token(token)
    except jwt.InvalidTokenError:
        raise unauthorized()
    if p.get("typ") != "refresh":
        raise unauthorized()
    if db.query(RevokedToken).filter(RevokedToken.jti == p.get("jti")).first():
        raise unauthorized()
    user = db.query(User).filter(User.id == int(p["sub"])).first()
    if not user or not user.is_active or int(p.get("tv", -1)) != user.token_version:
        raise unauthorized()
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise unauthorized("账号已锁定")
    db.merge(RevokedToken(jti=p["jti"], user_id=user.id, token_type="refresh",
                          expires_at=datetime.fromtimestamp(p["exp"], tz=timezone.utc) if isinstance(p["exp"], (int, float)) else now(),
                          revoked_at=now()))
    sec = get_setting(db, "security", {"access_token_minutes": 120, "refresh_token_days": 7})
    access, refresh_tok, expires_in = _tokens(user, int(sec.get("access_token_minutes", 120)), int(sec.get("refresh_token_days", 7)))
    return ok({"access_token": access, "refresh_token": refresh_tok, "expires_in": expires_in})


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
    user["must_change_password"] = actor.user.must_change_password
    return ok(user)


@router.put("/password")
def change_password(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user_allow_must_change)):
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
    return ok({})


@router.get("/demo-accounts")
def demo_accounts(db: Session = Depends(get_db)):
    if not DEMO_LOGIN_HINT:
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
