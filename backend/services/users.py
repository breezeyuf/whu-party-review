from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from errors import conflict, forbidden, unprocessable
from models import Archive, Org, User, UserRole
from security import hash_password, mask_phone, encrypt_field, random_password, password_ok
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


ROLES = {"STUDENT", "BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN", "SYS_ADMIN"}


def _org_id(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise unprocessable("组织编号须为正整数")
    try:
        number = int(value)
        if number <= 0 or str(number) != str(value):
            raise ValueError()
    except (ValueError, TypeError):
        raise unprocessable("组织编号须为正整数") from None
    return number


def _validate_profile_fields(body):
    for key in ('real_name', 'gender', 'email', 'phone'):
        if key in body and body[key] is not None and not isinstance(body[key], str):
            raise unprocessable('用户资料字段须为文字或 null')


def can_manage_account(db: Session, actor, user: User) -> bool:
    if actor.role in PRIVILEGED:
        return True
    if actor.role != "COLLEGE_REVIEWER":
        return False
    org = db.get(Org, user.org_id) if user.org_id else None
    if not org or not can_manage_user(actor, org):
        return False
    # Default organization is not the whole account's authority. A multi-role
    # account may hold school-wide or other-college grants that must be protected.
    for grant in user.roles:
        grant_org = db.get(Org, grant.org_id)
        if grant.role in PRIVILEGED or not grant_org or not can_manage_user(actor, grant_org):
            return False
    return True


def validate_grants(db: Session, actor, rows, default_org_id: int) -> list[dict]:
    if not isinstance(rows, list) or not rows:
        raise unprocessable("请至少保留一条有效身份授权")
    grants, seen = [], set()
    for entry in rows:
        if not isinstance(entry, (dict, str)):
            raise unprocessable("身份授权须为角色或角色与组织对象")
        role = entry.get("role") if isinstance(entry, dict) else entry
        if not isinstance(role, str) or role not in ROLES:
            raise unprocessable("角色无效")
        oid = _org_id(entry.get("org_id", default_org_id) if isinstance(entry, dict) else default_org_id)
        org = db.get(Org, oid)
        if not org or not org.is_active:
            raise unprocessable("授权组织不存在或已停用")
        if not can_manage_user(actor, org) or (role in PRIVILEGED and actor.role not in PRIVILEGED):
            raise forbidden("无权在该组织下授予该角色")
        key = (role, oid)
        if key in seen:
            raise unprocessable("同一组织的角色授权不能重复")
        seen.add(key)
        grants.append({"role": role, "org_id": oid})
    return grants


def create_user(db: Session, actor, body: dict) -> tuple[User, str | None]:
    from services.sessions import mode
    sso = mode(db) == "sso"
    _validate_profile_fields(body)
    oid = _org_id(body.get("org_id"))
    org = db.get(Org, oid)
    if not org or not org.is_active:
        raise unprocessable("组织不存在或已停用")
    if not can_manage_user(actor, org):
        raise forbidden()
    username, name = body.get("username"), body.get("real_name")
    if not isinstance(username, str) or not username.strip() or len(username.strip()) > 100:
        raise unprocessable("账号须为不超过 100 个字符的文字")
    if not isinstance(name, str) or not name.strip():
        raise unprocessable("姓名不能为空")
    username, name = username.strip(), name.strip()
    grants = validate_grants(db, actor, body.get("roles"), oid)
    if db.query(User).filter(User.username == username).first():
        raise conflict("用户名已存在")
    if body.get('password') is not None and not isinstance(body['password'], str):
        raise unprocessable('初始密码须为文字')
    if sso and body.get('password'):
        raise unprocessable('统一认证用户不设置本地密码')
    pwd = None if sso else (body.get("password") or random_password())
    if not sso:
        if len(pwd.encode('utf-8')) > 72:
            raise unprocessable("初始密码须为最多 72 字节的文字")
        error = password_ok(pwd)
        if error:
            raise unprocessable(error)
    user = User(
        username=username, password_hash="!SSO_ONLY" if sso else hash_password(pwd), real_name=name,
        gender=body.get("gender"), org_id=org.id, email=body.get("email"),
        phone_enc=encrypt_field(body.get("phone")), phone_masked=mask_phone(body.get("phone")),
        is_active=True, must_change_password=not sso, created_at=now(), updated_at=now(),
    )
    db.add(user)
    db.flush()
    for grant in grants:
        db.add(UserRole(user_id=user.id, **grant, created_at=now()))
    db.flush()
    return user, pwd


def update_user(db: Session, actor, user: User, body: dict) -> User:
    manages = can_manage_account(db, actor, user)
    is_self = actor.id == user.id
    if not manages and not is_self:
        raise forbidden()
    if is_self and not manages:
        body = {k: v for k, v in body.items() if k in ("real_name", "gender", "email", "phone")}
    # Validate all requested changes before mutating profile data or deleting grants.
    _validate_profile_fields(body)
    if "is_active" in body and body["is_active"] is not None and type(body["is_active"]) is not bool:
        raise unprocessable("启用状态须为开关值")
    if "real_name" in body and (not isinstance(body['real_name'], str) or not body['real_name'].strip()):
        raise unprocessable("姓名不能为空")
    oid = user.org_id
    if body.get("org_id") is not None:
        oid = _org_id(body["org_id"])
        target = db.get(Org, oid)
        if not target or not target.is_active or not can_manage_user(actor, target):
            raise forbidden("无权调整所属组织")
    grants = None
    if "roles" in body and body["roles"] is not None:
        if not manages:
            raise forbidden()
        grants = validate_grants(db, actor, body["roles"], oid)
    for key in ("real_name", "gender", "email"):
        if key in body and body[key] is not None:
            setattr(user, key, body[key])
    if "phone" in body:
        user.phone_enc = encrypt_field(body.get("phone"))
        user.phone_masked = mask_phone(body.get("phone"))
    if "org_id" in body and body["org_id"] is not None:
        user.org_id = oid
    if "is_active" in body and body["is_active"] is not None:
        user.is_active = body["is_active"]
        if not user.is_active:
            user.token_version = (user.token_version or 0) + 1
    if grants is not None:
        db.query(UserRole).filter(UserRole.user_id == user.id).delete(synchronize_session=False)
        for grant in grants:
            db.add(UserRole(user_id=user.id, **grant, created_at=now()))
    user.updated_at = now()
    db.flush()
    if grants is not None:
        db.expire(user, ['roles'])
    return user


def reset_user_password(db: Session, user: User) -> str:
    from services.sessions import require_demo
    require_demo(db)
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
