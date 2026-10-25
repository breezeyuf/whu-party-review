from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden
from schemas.common import ok
from services.audit import log
from services.settings import public_settings, test_ai, update_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get('/retention/materials')
def expired_materials(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),status:str=Query('pending',pattern='^(pending|confirmed)$'),
                      db:Session=Depends(get_db),actor:Actor=Depends(get_current_user)):
    from services.retention import list_expired
    return ok(list_expired(db,actor,page,page_size,status))


@router.post('/retention/materials/{version_id}/keep')
def keep_material(version_id:int,body:dict,db:Session=Depends(get_db),actor:Actor=Depends(get_current_user)):
    from services.retention import confirm_keep
    return ok(confirm_keep(db,actor,version_id,body.get('reason')))


@router.post('/delivery/test')
def test_delivery_config(db:Session=Depends(get_db),actor:Actor=Depends(get_current_user)):
    if actor.role!='SYS_ADMIN': raise forbidden()
    from services.delivery import check_config
    from utils import get_setting
    return ok(check_config(get_setting(db,'delivery',{})))


@router.get("")
def get_settings(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        raise forbidden()
    return ok(public_settings(db))


@router.put("")
def put_settings(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        raise forbidden()
    data = update_settings(db, actor, body)
    log(db, actor, "SETTINGS_UPDATE", "settings", None, {k: True for k in (body or {})})
    return ok(data)


@router.post("/ai/test")
def ai_test(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role != "SYS_ADMIN":
        raise forbidden()
    return ok(test_ai(db, body.get("target") or "llm", body.get("override")))
