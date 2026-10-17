from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, not_found
from models import Job, Material, MaterialVersion, Submission, User
from services.scope import scoped_submissions
from schemas.common import ok, page_params
from utils import now

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _scoped_jobs(db, actor):
    query = db.query(Job)
    if actor.role in ("SYS_ADMIN", "ORG_ADMIN"):
        return query
    if actor.role == "STUDENT":
        return query.filter(Job.created_by == actor.id)
    submissions = scoped_submissions(db.query(Submission.id), actor, db)
    versions = db.query(MaterialVersion.id).join(Material).filter(Material.submission_id.in_(submissions))
    return query.filter(or_(
        Job.created_by == actor.id,
        and_(Job.target_type == "submission", Job.target_id.in_(submissions)),
        and_(Job.target_type == "material_version", Job.target_id.in_(versions)),
    ))


def _job_dict(j: Job, extra=None) -> dict:
    name = None
    d = {
        "id": j.id, "job_type": j.job_type, "status": j.status, "target_type": j.target_type, "target_id": j.target_id,
        "total": j.total, "done_count": j.done_count, "failed_count": j.failed_count, "progress": j.progress,
        "stage_text": j.stage_text, "error": j.error, "created_by_name": name,
        "created_at": j.created_at.isoformat() if j.created_at else None,
        "started_at": j.started_at.isoformat() if j.started_at else None,
        "finished_at": j.finished_at.isoformat() if j.finished_at else None,
        "parent_id": j.parent_id, "result": j.result, "params": j.params,
    }
    if extra:
        d.update(extra)
    return d


@router.get("")
def list_jobs(job_type: str | None = None, status: str | None = None, parent_id: int | None = None, mine: bool = False,
              page: int = 1, page_size: int = 20, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = _scoped_jobs(db, actor)
    if actor.role == "STUDENT" or mine:
        q = q.filter(Job.created_by == actor.id)
    if job_type:
        q = q.filter(Job.job_type == job_type)
    if status:
        q = q.filter(Job.status == status)
    if parent_id is not None:
        q = q.filter(Job.parent_id == parent_id)
    page, page_size = page_params(page, page_size)
    total = q.count()
    rows = q.order_by(Job.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for j in rows:
        d = _job_dict(j)
        if j.created_by:
            u = db.query(User).filter(User.id == j.created_by).first()
            d["created_by_name"] = u.real_name if u else None
        items.append(d)
    return ok({"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/{jid}")
def get_job(jid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    j = _scoped_jobs(db, actor).filter(Job.id == jid).first()
    if not j:
        raise not_found()
    if actor.role == "STUDENT" and j.created_by != actor.id:
        raise forbidden()
    kids = db.query(Job).filter(Job.parent_id == jid).all()
    summary = {"queued": 0, "running": 0, "succeeded": 0, "failed": 0}
    failed_children = []
    for k in kids:
        key = {"QUEUED": "queued", "RUNNING": "running", "SUCCEEDED": "succeeded", "FAILED": "failed"}.get(k.status)
        if key:
            summary[key] += 1
        if k.status == "FAILED":
            failed_children.append({"id": k.id, "target_id": k.target_id, "error": k.error})
    d = _job_dict(j, {"children_summary": summary, "failed_children": failed_children})
    if j.created_by:
        u = db.query(User).filter(User.id == j.created_by).first()
        d["created_by_name"] = u.real_name if u else None
    return ok(d)


@router.post("/{jid}/retry")
def retry(jid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    j = db.query(Job).filter(Job.id == jid).first()
    if not j:
        raise not_found()
    if actor.role not in ("SYS_ADMIN", "ORG_ADMIN") and j.created_by != actor.id:
        raise forbidden()
    if j.status not in ("FAILED", "PARTIAL"):
        raise conflict("仅失败或部分失败的任务可重试")
    n = 0
    if j.job_type == "BATCH_AI_CHECK":
        kids = db.query(Job).filter(Job.parent_id == jid, Job.status == "FAILED").all()
        for k in kids:
            k.status = "QUEUED"
            k.error = None
            k.attempts = 0
            k.finished_at = None
            n += 1
        j.status = "QUEUED"
        j.error = None
        n += 1
    else:
        j.status = "QUEUED"
        j.error = None
        n = 1
    j.attempts = 0
    j.finished_at = None
    j.stage_text = "等待重试"
    return ok({"job_id": j.id, "retried": n})
