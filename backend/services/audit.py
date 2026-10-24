from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from models import AuditLog
from services.client_ip import client_ip
from utils import now


def log(
    db: Session,
    actor,
    action: str,
    object_type: Optional[str] = None,
    object_id: Optional[str | int] = None,
    detail: Optional[dict[str, Any]] = None,
    request=None,
) -> None:
    ip = None
    ua = None
    user_id = None
    username = None
    role = None
    if actor is not None:
        user_id = getattr(actor, "id", None) or getattr(getattr(actor, "user", None), "id", None)
        username = getattr(actor, "username", None) or getattr(getattr(actor, "user", None), "username", None)
        role = getattr(actor, "role", None)
        ip = getattr(actor, "ip", None)
        ua = getattr(actor, "user_agent", None)
    if request is not None:
        ip = client_ip(request) or None
        ua = request.headers.get("user-agent", ua)
    db.add(
        AuditLog(
            user_id=user_id,
            username=username,
            role=role,
            action=action,
            object_type=object_type,
            object_id=None if object_id is None else str(object_id),
            detail=detail or {},
            ip=ip,
            user_agent=ua,
            created_at=now(),
        )
    )
    db.flush()
