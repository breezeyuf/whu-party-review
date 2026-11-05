from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden
from schemas.common import ok
from services.audit import log
from services.demo import seed_demo

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/seed-demo")
def seed(body: dict | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    from services.sessions import require_demo
    require_demo(db)
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        raise forbidden()
    body = body or {}
    result = seed_demo(db, actor, reset=bool(body.get("reset")), run_checks=body.get("run_checks", True))
    log(db, actor, "SEED_DEMO", "demo", None, {"reset": body.get("reset")})
    return ok(result)
