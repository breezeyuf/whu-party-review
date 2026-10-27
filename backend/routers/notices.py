from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden, not_found
from models import Notice, Submission
from schemas.common import ok, page_params
from services.exporter import export_notice_file
from services.notices import create_rectification_notice, send_notice, serialize_notice
from services.scope import REVIEWER_ROLES, can_review, deny_object_access, ensure_submission_access, scoped_submissions

router = APIRouter(tags=["notices"])


@router.post("/submissions/{sid}/rectification-notice")
def rectification(sid: int, body: dict | None = None, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    s = db.query(Submission).filter(Submission.id == sid).with_for_update().populate_existing().one()
    if not can_review(s, actor, db):
        raise forbidden("仅当前层级审核员可生成整改通知")
    body = body or {}
    n = create_rectification_notice(db, s, actor, body.get("issue_ids"), body.get("deadline"), body.get("send", True), body.get("note"))
    return ok(serialize_notice(n))


@router.get("/notices")
def list_notices(notice_type: str | None = None, status: str | None = None, batch_id: int | None = None,
                 branch_id: int | None = None, submission_id: int | None = None, page: int = 1, page_size: int = 20,
                 db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = db.query(Notice).join(Submission, Submission.id == Notice.submission_id)
    if actor.role == "STUDENT":
        q = q.filter(Notice.student_user_id == actor.id, Notice.status == "SENT")
    else:
        q = scoped_submissions(q, actor, db)
    if notice_type:
        q = q.filter(Notice.notice_type == notice_type)
    if status:
        q = q.filter(Notice.status == status)
    if submission_id:
        q = q.filter(Notice.submission_id == submission_id)
    if batch_id:
        q = q.filter(Submission.batch_id == batch_id)
    if branch_id:
        q = q.filter(Submission.branch_id == branch_id)
    page, page_size = page_params(page, page_size)
    total = q.count()
    rows = q.order_by(Notice.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ok({"items": [serialize_notice(n, brief=True) for n in rows], "total": total, "page": page, "page_size": page_size})


def _notice_access(db, actor, nid):
    n = db.query(Notice).filter(Notice.id == nid).first()
    if not n or (actor.role == "STUDENT" and (n.student_user_id != actor.id or n.status != "SENT")):
        deny_object_access(db, actor, "notice", nid)
    allowed = scoped_submissions(db.query(Submission), actor, db).filter(Submission.id == n.submission_id).first()
    if not allowed:
        deny_object_access(db, actor, "notice", nid)
    return n


@router.get("/notices/{nid}")
def get_notice(nid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    n = _notice_access(db, actor, nid)
    return ok(serialize_notice(n))


@router.get("/notices/{nid}/export")
def export_notice(nid: int, format: str = "pdf", db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    n = _notice_access(db, actor, nid)
    return export_notice_file(n, format)


@router.post("/notices/{nid}/send")
def do_send(nid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    n = _notice_access(db, actor, nid)
    if actor.role not in REVIEWER_ROLES and actor.id != n.created_by:
        raise forbidden()
    send_notice(db, n)
    return ok(serialize_notice(n))
