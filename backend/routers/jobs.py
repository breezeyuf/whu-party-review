from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import case, func, or_

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, not_found
from models import Job, User
from services.scope import scoped_jobs as _scoped_jobs
from schemas.common import ok, page_params
from utils import now

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _job_dict(j: Job, extra=None) -> dict:
    name = None
    d = {
        "id": j.id, "job_type": j.job_type, "status": j.status, "target_type": j.target_type, "target_id": j.target_id,
        "total": j.total, "done_count": j.done_count, "failed_count": j.failed_count, "progress": j.progress,
        "stage_text": j.stage_text, "error": j.error, "created_by_name": name, "created_by": j.created_by, "created_by_username": None,
        "created_at": j.created_at.isoformat() if j.created_at else None,
        "started_at": j.started_at.isoformat() if j.started_at else None,
        "finished_at": j.finished_at.isoformat() if j.finished_at else None,
        "parent_id": j.parent_id, "result": j.result, "params": j.params,
    }
    if extra:
        d.update(extra)
    return d


@router.get("")
def list_jobs(job_type: str | None = None, status: str | None = None, parent_id: int | None = None, mine: bool = False, created_by: int | None = None, q: str | None = None,
              page: int = 1, page_size: int = 20, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    search = q
    q = _scoped_jobs(db, actor)
    if created_by is not None:
        q = q.filter(Job.created_by == created_by if created_by else Job.created_by.is_(None))
    if search:
        q = q.outerjoin(User, User.id == Job.created_by).filter(or_(User.real_name.ilike(f"%{search}%"), User.username.ilike(f"%{search}%")))
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
            d["created_by_name"] = u.real_name if u else "已删除账号"
            d["created_by_username"] = u.username if u else None
        items.append(d)
    return ok({"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/creators")
def job_creators(q: str | None = None, job_type: str | None = None, status: str | None = None,
                 page: int = 1, page_size: int = 10, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    query = _scoped_jobs(db, actor)
    if actor.role == 'STUDENT':
        query = query.filter(Job.created_by == actor.id)
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if status:
        query = query.filter(Job.status == status)
    query = query.outerjoin(User, User.id == Job.created_by)
    if q:
        query = query.filter(or_(User.real_name.ilike(f'%{q}%'), User.username.ilike(f'%{q}%')))
    grouped = query.with_entities(Job.created_by, User.real_name, User.username, func.count(Job.id).label('total'),
        func.sum(case((Job.status == 'RUNNING', 1), else_=0)).label('running'),
        func.sum(case((Job.status.in_(['FAILED', 'PARTIAL']), 1), else_=0)).label('failed'),
        func.max(Job.created_at).label('latest_at'), func.max(Job.id).label('last_id')
    ).group_by(Job.created_by, User.real_name, User.username)
    total = grouped.count()
    page, page_size = page_params(page, page_size)
    rows = grouped.order_by(func.max(Job.created_at).desc(), func.max(Job.id).desc()).offset((page-1)*page_size).limit(page_size).all()
    return ok({'items': [{'created_by': row.created_by or 0, 'name': row.real_name or ('已删除账号' if row.created_by else '系统任务'),
        'username': row.username, 'total': row.total, 'running': int(row.running or 0), 'failed': int(row.failed or 0),
        'latest_at': row.latest_at.isoformat() if row.latest_at else None} for row in rows], 'total': total, 'page': page, 'page_size': page_size})


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
