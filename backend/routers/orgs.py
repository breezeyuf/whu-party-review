from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, unprocessable
from models import Archive, Org, User
from schemas.common import ok
from services.audit import log
from utils import now

router = APIRouter(prefix="/orgs", tags=["orgs"])


def _tree(orgs: list[Org], parent_id=None) -> list:
    out = []
    for o in orgs:
        if o.parent_id == parent_id:
            item = _org(o)
            item["children"] = _tree(orgs, o.id)
            out.append(item)
    return out


def _org(o: Org) -> dict:
    return {
        "id": o.id, "parent_id": o.parent_id, "org_type": o.org_type, "name": o.name,
        "code": o.code, "sort_order": o.sort_order, "is_active": o.is_active, "is_demo": o.is_demo,
    }


@router.get("")
def list_orgs(flat: bool = False, include_inactive: bool = False, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = db.query(Org)
    if not include_inactive:
        q = q.filter(Org.is_active.is_(True))
    orgs = q.order_by(Org.sort_order, Org.id).all()
    if flat:
        return ok([_org(o) for o in orgs])
    return ok(_tree(orgs, None))


@router.post("")
def create_org(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        raise forbidden()
    parent = db.query(Org).filter(Org.id == body.get("parent_id")).first() if body.get("parent_id") else None
    org_type = body.get("org_type")
    if org_type == "SCHOOL" and parent:
        raise unprocessable("学校不能有上级")
    if org_type == "COLLEGE" and (not parent or parent.org_type != "SCHOOL"):
        raise unprocessable("学院必须挂在学校下")
    if org_type == "BRANCH" and (not parent or parent.org_type != "COLLEGE"):
        raise unprocessable("支部必须挂在学院下")
    o = Org(
        parent_id=parent.id if parent else None, org_type=org_type, name=body["name"],
        code=body.get("code"), sort_order=body.get("sort_order") or 0, is_active=True,
        created_at=now(), updated_at=now(),
    )
    db.add(o)
    db.flush()
    log(db, actor, "ORG_CREATE", "org", o.id, {"name": o.name})
    return ok(_org(o))


@router.put("/{oid}")
def update_org(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    o = db.query(Org).filter(Org.id == oid).first()
    if not o:
        from errors import not_found
        raise not_found()
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        if actor.role == "COLLEGE_REVIEWER" and o.org_type == "BRANCH" and o.parent_id == actor.org_id:
            if "name" in body:
                o.name = body["name"]
            o.updated_at = now()
            return ok(_org(o))
        raise forbidden()
    for k in ("name", "code", "sort_order", "is_active", "parent_id"):
        if k in body and body[k] is not None:
            setattr(o, k, body[k])
    o.updated_at = now()
    log(db, actor, "ORG_UPDATE", "org", o.id, body)
    return ok(_org(o))


@router.delete("/{oid}")
def delete_org(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role != "SYS_ADMIN":
        raise forbidden()
    o = db.query(Org).filter(Org.id == oid).first()
    if not o:
        from errors import not_found
        raise not_found()
    if db.query(Org).filter(Org.parent_id == oid).first() or db.query(User).filter(User.org_id == oid).first() or db.query(Archive).filter((Archive.branch_id == oid) | (Archive.college_id == oid)).first():
        raise conflict("存在子组织、用户或档案，请改为停用")
    db.delete(o)
    log(db, actor, "ORG_DELETE", "org", oid, {})
    return ok({})
