from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session, selectinload

from database import get_db
from errors import forbidden, unauthorized
from models import User, UserRole
from services.client_ip import client_ip


@dataclass
class Actor:
    user: User
    role: str
    org_id: int
    roles: list[UserRole]
    ip: str
    user_agent: str

    @property
    def id(self) -> int:
        return self.user.id

    @property
    def username(self) -> str:
        return self.user.username

    def has_role(self, *roles: str) -> bool:
        return self.role in roles or any(r.role in roles for r in self.roles)

    def org_ids_for(self, role: str) -> list[int]:
        return [r.org_id for r in self.roles if r.role == role]


ROLE_PRIORITY = [
    "SYS_ADMIN",
    "ORG_ADMIN",
    "COLLEGE_REVIEWER",
    "CROSS_REVIEWER",
    "BRANCH_REVIEWER",
    "STUDENT",
]


def _load_user(db: Session, user_id: int) -> User:
    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(UserRole.org), selectinload(User.org))
        .filter(User.id == user_id)
        .first()
    )
    if not user or not user.is_active:
        raise unauthorized("账号不存在或已停用")
    return user


def _actor_from_request(
    request: Request,
    db: Session,
    authorization: Optional[str],
    x_active_role: Optional[str],
    require_password_ok: bool,
) -> Actor:
    from services.sessions import session_user_id, mode
    session = session_user_id(db, request)
    user = _load_user(db, session.user_id)
    if session.token_version != user.token_version:
        raise unauthorized("登录已失效，请重新登录")
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise unauthorized("账号已锁定")
    path = request.url.path
    if require_password_ok and mode(db) == "demo" and user.must_change_password and not path.startswith("/api/auth"):
        raise forbidden("请先修改初始密码", code=40301)
    roles = list(user.roles or [])
    if not roles:
        raise forbidden("账号未分配角色")
    active_role, active_org = _pick_role(roles, x_active_role)
    return Actor(
        user=user,
        role=active_role,
        org_id=active_org,
        roles=roles,
        ip=client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
    )


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
    x_active_role: Optional[str] = Header(default=None, alias="X-Active-Role"),
) -> Actor:
    return _actor_from_request(request, db, authorization, x_active_role, True)


def get_current_user_allow_must_change(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
    x_active_role: Optional[str] = Header(default=None, alias="X-Active-Role"),
) -> Actor:
    return _actor_from_request(request, db, authorization, x_active_role, False)


def _pick_role(roles: list[UserRole], header: Optional[str]) -> tuple[str, int]:
    if header and "@" not in header:
        raise forbidden("当前角色无效")
    if header and "@" in header:
        role, org_s = header.split("@", 1)
        try:
            org_id = int(org_s)
        except ValueError:
            org_id = None
        for r in roles:
            if r.role == role and r.org_id == org_id:
                return r.role, r.org_id
        raise forbidden("当前角色无效")
    roles_sorted = sorted(roles, key=lambda r: ROLE_PRIORITY.index(r.role) if r.role in ROLE_PRIORITY else 99)
    top = roles_sorted[0]
    return top.role, top.org_id


def require_roles(*allowed: str) -> Callable:
    def _dep(actor: Actor = Depends(get_current_user)) -> Actor:
        if actor.role not in allowed:
            raise forbidden()
        return actor

    return _dep
