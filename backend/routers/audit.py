from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden
from models import AuditLog
from schemas.common import ok, page_params
from utils import as_date
from datetime import datetime, time, timezone, timedelta

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
def list_logs(user_id: int | None = None, username: str | None = None, action: str | None = None,
              object_type: str | None = None, object_id: str | None = None, ip: str | None = None,
              date_from: str | None = None, date_to: str | None = None, page: int = 1, page_size: int = 20,
              db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        raise forbidden()
    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if username:
        q = q.filter(AuditLog.username.ilike(f"%{username}%"))
    if action:
        q = q.filter(AuditLog.action == action)
    if object_type:
        q = q.filter(AuditLog.object_type == object_type)
    if object_id:
        q = q.filter(AuditLog.object_id == str(object_id))
    if ip:
        q = q.filter(AuditLog.ip == ip)
    if date_from:
        d = as_date(date_from)
        if d:
            q = q.filter(AuditLog.created_at >= datetime.combine(d, time.min, tzinfo=timezone(timedelta(hours=8))))
    if date_to:
        d = as_date(date_to)
        if d:
            q = q.filter(AuditLog.created_at <= datetime.combine(d, time.max, tzinfo=timezone(timedelta(hours=8))))
    page, page_size = page_params(page, page_size)
    total = q.count()
    rows = q.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [{
        "id": r.id, "username": r.username, "role": r.role, "action": r.action,
        "object_type": r.object_type, "object_id": r.object_id, "detail": r.detail,
        "ip": r.ip, "user_agent": r.user_agent,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    } for r in rows]
    return ok({"items": items, "total": total, "page": page, "page_size": page_size})
