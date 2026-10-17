from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from errors import conflict, forbidden, unprocessable
from models import Archive, Org, User, UserRole
from security import hash_password, mask_phone, encrypt_field, random_password
from utils import now, serialize_user_brief


PRIVILEGED = {"ORG_ADMIN", "SYS_ADMIN"}


def can_manage_user(actor, org: Org) -> bool:
    if actor.role == "SYS_ADMIN":
        return True
    if actor.role == "ORG_ADMIN":
        return True
    if actor.role == "COLLEGE_REVIEWER":
        if org.org_type == "COLLEGE" and org.id == actor.org_id:
            return True
        if org.org_type == "BRANCH" and org.parent_id == actor.org_id:
            return True
    return False


def create_user(db: Session, actor, body: dict) -> tuple[User, str]:
    org = db.query(Org).filter(Org.id == body["org_id"]).first()
    if not org:
        raise unprocessable("组织不存在")
    if not can_manage_user(actor, org):
        raise forbidden()
    if db.query(User).filter(User.username == body["username"]).first():
        raise conflict("用户名已存在")
    pwd = body.get("password") or random_password()
    user = User(
        username=body["username"], password_hash=hash_password(pwd), real_name=body["real_name"],
        gender=body.get("gender"), org_id=org.id, email=body.get("email"),
        phone_enc=encrypt_field(body.get("phone")), phone_masked=mask_phone(body.get("phone")),
        is_active=True, must_change_password=True, created_at=now(), updated_at=now(),
    )
    db.add(user)
    db.flush()
    for r in body.get("roles") or []:
        role = r.get("role") if isinstance(r, dict) else r
        oid = r.get("org_id") if isinstance(r, dict) else org.id
        if role in PRIVILEGED and actor.role == "COLLEGE_REVIEWER":
            raise forbidden("不能授予组织部/系统管理员角色")
        db.add(UserRole(user_id=user.id, role=role, org_id=oid, created_at=now()))
    db.flush()
    return user, pwd


def update_user(db: Session, actor, user: User, body: dict) -> User:
    org = db.query(Org).filter(Org.id == user.org_id).first() if user.org_id else None
    manages = bool(org) and can_manage_user(actor, org)
    is_self = actor.id == user.id
    if not manages and not is_self:
        raise forbidden()
    if is_self and not manages:
        # 本人仅可维护基础资料，不得调整角色、所属组织与启用状态
        body = {k: v for k, v in body.items() if k in ("real_name", "gender", "email", "phone")}
    for k in ("real_name", "gender", "email"):
        if k in body and body[k] is not None:
            setattr(user, k, body[k])
    if "phone" in body:
        user.phone_enc = encrypt_field(body.get("phone"))
        user.phone_masked = mask_phone(body.get("phone"))
    if "org_id" in body and body["org_id"] and int(body["org_id"]) != user.org_id:
        target = db.query(Org).filter(Org.id == body["org_id"]).first()
        if not target or not can_manage_user(actor, target):
            raise forbidden("无权调整所属组织")
        user.org_id = target.id
    if "is_active" in body and body["is_active"] is not None:
        if not manages:
            raise forbidden()
        user.is_active = bool(body["is_active"])
        if not user.is_active:
            user.token_version = (user.token_version or 0) + 1
    if "roles" in body and body["roles"] is not None:
        if not manages:
            raise forbidden()
        for r in body["roles"]:
            role = r.get("role") if isinstance(r, dict) else r
            oid = r.get("org_id") if isinstance(r, dict) else user.org_id
            if role in PRIVILEGED and actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
                raise forbidden("不能授予组织部/系统管理员角色")
            rorg = db.query(Org).filter(Org.id == oid).first() if oid else None
            if not rorg or not can_manage_user(actor, rorg):
                raise forbidden("无权在该组织下授予角色")
        db.query(UserRole).filter(UserRole.user_id == user.id).delete()
        for r in body["roles"]:
            role = r.get("role") if isinstance(r, dict) else r
            oid = r.get("org_id") if isinstance(r, dict) else user.org_id
            db.add(UserRole(user_id=user.id, role=role, org_id=oid, created_at=now()))
    user.updated_at = now()
    db.flush()
    return user


def reset_user_password(db: Session, user: User) -> str:
    pwd = random_password()
    user.password_hash = hash_password(pwd)
    user.must_change_password = True
    user.token_version = (user.token_version or 0) + 1
    user.failed_login_count = 0
    user.locked_until = None
    user.updated_at = now()
    db.flush()
    return pwd


def user_to_dict(user: User) -> dict:
    d = serialize_user_brief(user)
    return d
