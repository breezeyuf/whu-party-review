from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response, UploadFile, File, Form
from sqlalchemy.orm import Session, selectinload

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden, not_found, too_large
from models import Org, User, UserRole
from schemas.common import ok, page_params
from services.audit import log
from services.exporter import xlsx_response
from services.importer import import_users_xlsx, users_template
from services.users import create_user, reset_user_password, update_user, user_to_dict, can_manage_user
from services.scope import deny_object_access

router = APIRouter(prefix="/users", tags=["users"])


def _scope_users(db, actor, q, role=None):
    if actor.role in ("SYS_ADMIN", "ORG_ADMIN"):
        return q
    if actor.role == "COLLEGE_REVIEWER":
        ids = [actor.org_id] + [r[0] for r in db.query(Org.id).filter(Org.parent_id == actor.org_id).all()]
        # A person's default organization may differ from the organization on
        # their CROSS_REVIEWER grant. Cross-review assignment must be scoped by
        # that grant, otherwise valid reviewers disappear from the selector.
        if role == "CROSS_REVIEWER":
            return q.filter(User.id.in_(db.query(UserRole.user_id).filter(
                UserRole.role == role, UserRole.org_id.in_(ids),
            )))
        return q.filter(User.org_id.in_(ids))
    return q.filter(User.id == actor.id)


@router.get("")
def list_users(q: str | None = None, org_id: int | None = None, role: str | None = None, is_active: bool | None = None,
               page: int = 1, page_size: int = 20, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    query = _scope_users(db, actor, db.query(User).options(selectinload(User.roles).selectinload(UserRole.org), selectinload(User.org)), role)
    if q:
        like = f"%{q}%"
        query = query.filter((User.username.ilike(like)) | (User.real_name.ilike(like)))
    if org_id:
        query = query.filter(User.org_id == org_id)
    if is_active is not None:
        query = query.filter(User.is_active.is_(is_active))
    if role:
        query = query.join(UserRole).filter(UserRole.role == role)
    page, page_size = page_params(page, page_size)
    total = query.count()
    rows = query.order_by(User.id).offset((page - 1) * page_size).limit(page_size).all()
    return ok({"items": [user_to_dict(u) for u in rows], "total": total, "page": page, "page_size": page_size})


@router.post("")
def create(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    user, pwd = create_user(db, actor, body)
    log(db, actor, "USER_CREATE", "user", user.id, {"username": user.username})
    db.refresh(user)
    return ok({"user": user_to_dict(user), "initial_password": pwd})


@router.get("/import-template")
def import_template(actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    return xlsx_response("用户导入模板.xlsx", users_template())


@router.post("/import")
async def import_users(response: Response, file: UploadFile = File(...), dry_run: str = Form("true"), batch_id: int | None = Form(None),
                       db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024:
        raise too_large("导入文件超过 10 MB")
    dry = str(dry_run).lower() in ("1", "true", "yes")
    result = import_users_xlsx(db, actor, data, dry_run=dry, batch_id=batch_id)
    response.headers["Cache-Control"] = "no-store, private"
    log(db, actor, "USER_IMPORT", "user", None, {"dry_run": dry})
    return ok(result)


@router.get("/import-passwords/{file_id}/download")
def download_import_passwords(file_id: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    from services.sessions import require_demo
    require_demo(db)
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    from services.import_passwords import consume_password_file
    response = consume_password_file(db, actor, file_id)
    log(db, actor, "IMPORT_PASSWORDS_DOWNLOAD", "import_password_file", file_id)
    return response


@router.get("/{uid}")
def get_user(uid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    user = _scope_users(db, actor, db.query(User).options(selectinload(User.roles).selectinload(UserRole.org), selectinload(User.org))).filter(User.id == uid).first()
    if not user:
        deny_object_access(db, actor, "user", uid)
    return ok(user_to_dict(user))


@router.put("/{uid}")
def put_user(uid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    user = db.query(User).options(selectinload(User.roles).selectinload(UserRole.org)).filter(User.id == uid).first()
    if not user:
        raise not_found()
    update_user(db, actor, user, body)
    log(db, actor, "USER_UPDATE", "user", uid, body)
    db.refresh(user)
    return ok(user_to_dict(user))


@router.post("/{uid}/reset-password")
def reset(uid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise not_found()
    org = db.query(Org).filter(Org.id == user.org_id).first()
    if org and not can_manage_user(actor, org):
        raise forbidden()
    pwd = reset_user_password(db, user)
    log(db, actor, "USER_RESET_PASSWORD", "user", uid, {})
    return ok({"initial_password": pwd})
