from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from models import Message
from utils import now


def send_message(
    db: Session,
    user_id: int,
    msg_type: str,
    title: str,
    content: str = "",
    link_type: Optional[str] = None,
    link_id: Optional[int] = None,
    dedup_key: Optional[str] = None,
) -> Optional[Message]:
    if dedup_key:
        exists = db.query(Message).filter(Message.dedup_key == dedup_key).first()
        if exists:
            return exists
    msg = Message(
        user_id=user_id,
        msg_type=msg_type,
        title=title,
        content=content,
        link_type=link_type,
        link_id=link_id,
        is_read=False,
        dedup_key=dedup_key,
        created_at=now(),
    )
    db.add(msg)
    db.flush()
    return msg


def notify_role_users(db: Session, role: str, org_id: int, **kwargs) -> int:
    from models import UserRole

    rows = db.query(UserRole.user_id).filter(UserRole.role == role, UserRole.org_id == org_id).all()
    n = 0
    for (uid,) in rows:
        send_message(db, uid, **kwargs)
        n += 1
    return n
