from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden
from schemas.common import ok
from services.audit import log
from services.settings import public_settings, test_ai, update_settings

router = APIRouter(prefix="/settings", tags=["settings"])


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
