from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import not_found
from models import Message
from schemas.common import ok, page_params
from utils import now

router = APIRouter(prefix="/messages", tags=["messages"])


def _msg(m: Message) -> dict:
    return {
        "id": m.id, "msg_type": m.msg_type, "title": m.title, "content": m.content,
        "link_type": m.link_type, "link_id": m.link_id, "is_read": m.is_read,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


@router.get("")
def list_messages(is_read: bool | None = None, msg_type: str | None = None, page: int = 1, page_size: int = 20,
                  db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = db.query(Message).filter(Message.user_id == actor.id)
    if is_read is not None:
        q = q.filter(Message.is_read.is_(is_read))
    if msg_type:
        q = q.filter(Message.msg_type == msg_type)
    page, page_size = page_params(page, page_size)
    total = q.count()
    rows = q.order_by(Message.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ok({"items": [_msg(m) for m in rows], "total": total, "page": page, "page_size": page_size})


@router.get("/unread-count")
def unread(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    n = db.query(Message).filter(Message.user_id == actor.id, Message.is_read.is_(False)).count()
    return ok({"count": n})


@router.put("/{mid}/read")
def read_one(mid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Message).filter(Message.id == mid, Message.user_id == actor.id).first()
    if not m:
        raise not_found()
    m.is_read = True
    m.read_at = now()
    return ok({})


@router.put("/read-all")
def read_all(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    n = db.query(Message).filter(Message.user_id == actor.id, Message.is_read.is_(False)).update(
        {"is_read": True, "read_at": now()}, synchronize_session=False
    )
    return ok({"updated": n})
