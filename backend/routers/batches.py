from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, not_found, unprocessable
from models import Archive, Batch, CrossReviewPair, Org, Submission, User
from schemas.common import ok, page_params
from services.audit import log
from utils import as_date, now

router = APIRouter(prefix="/batches", tags=["batches"])


def _batch_dict(b: Batch, extra=None) -> dict:
    d = {
        "id": b.id, "name": b.name, "year": b.year, "term": b.term, "stage_codes": b.stage_codes,
        "description": b.description, "start_date": b.start_date.isoformat() if b.start_date else None,
        "end_date": b.end_date.isoformat() if b.end_date else None,
        "self_deadline": b.self_deadline.isoformat() if b.self_deadline else None,
        "branch_deadline": b.branch_deadline.isoformat() if b.branch_deadline else None,
        "cross_deadline": b.cross_deadline.isoformat() if b.cross_deadline else None,
        "college_deadline": b.college_deadline.isoformat() if b.college_deadline else None,
        "org_deadline": b.org_deadline.isoformat() if b.org_deadline else None,
        "status": b.status, "is_demo": b.is_demo,
    }
    if extra:
        d.update(extra)
    return d


@router.get("")
def list_batches(year: int | None = None, status: str | None = None, page: int = 1, page_size: int = 20,
                 db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = db.query(Batch)
    if year:
        q = q.filter(Batch.year == year)
    if status:
        q = q.filter(Batch.status == status)
    page, page_size = page_params(page, page_size)
    total = q.count()
    rows = q.order_by(Batch.year.desc(), Batch.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for b in rows:
        ac = db.query(func.count(Archive.id)).filter(Archive.batch_id == b.id).scalar() or 0
        stats = dict(db.query(Submission.status, func.count(Submission.id)).filter(Submission.batch_id == b.id).group_by(Submission.status).all())
        items.append(_batch_dict(b, {"archive_count": ac, "submission_stats": stats}))
    return ok({"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("")
def create_batch(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role != "ORG_ADMIN":
        raise forbidden()
    b = Batch(
        name=body["name"], year=body["year"], term=body.get("term") or "FULL_YEAR",
        stage_codes=body.get("stage_codes") or [1, 2, 3, 4, 5],
        start_date=as_date(body["start_date"]), end_date=as_date(body["end_date"]),
        self_deadline=as_date(body.get("self_deadline")), branch_deadline=as_date(body.get("branch_deadline")),
        cross_deadline=as_date(body.get("cross_deadline")), college_deadline=as_date(body.get("college_deadline")),
        org_deadline=as_date(body.get("org_deadline")), description=body.get("description"),
        created_by=actor.id, created_at=now(), updated_at=now(),
    )
    db.add(b)
    db.flush()
    log(db, actor, "BATCH_CREATE", "batch", b.id, {"name": b.name})
    return ok(_batch_dict(b))


@router.get("/{bid}")
def get_batch(bid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    b = db.query(Batch).filter(Batch.id == bid).first()
    if not b:
        raise not_found()
    ac = db.query(func.count(Archive.id)).filter(Archive.batch_id == bid).scalar() or 0
    stats = dict(db.query(Submission.status, func.count(Submission.id)).filter(Submission.batch_id == bid).group_by(Submission.status).all())
    by_stage = dict(db.query(Submission.stage_code, func.count(Submission.id)).filter(Submission.batch_id == bid).group_by(Submission.stage_code).all())
    return ok(_batch_dict(b, {"archive_count": ac, "submission_stats": stats, "by_stage": by_stage}))


@router.put("/{bid}")
def update_batch(bid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role != "ORG_ADMIN":
        raise forbidden()
    b = db.query(Batch).filter(Batch.id == bid).first()
    if not b:
        raise not_found()
    for k in ("name", "year", "term", "stage_codes", "description", "status"):
        if k in body and body[k] is not None:
            setattr(b, k, body[k])
    for k in ("start_date", "end_date", "self_deadline", "branch_deadline", "cross_deadline", "college_deadline", "org_deadline"):
        if k in body:
            setattr(b, k, as_date(body[k]))
    b.updated_at = now()
    log(db, actor, "BATCH_UPDATE", "batch", bid, body)
    return ok(_batch_dict(b))


@router.delete("/{bid}")
def delete_batch(bid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role != "ORG_ADMIN":
        raise forbidden()
    b = db.query(Batch).filter(Batch.id == bid).first()
    if not b:
        raise not_found()
    if db.query(Archive).filter(Archive.batch_id == bid).first():
        raise conflict("已有档案，请改为关闭")
    db.delete(b)
    log(db, actor, "BATCH_DELETE", "batch", bid, {})
    return ok({})


def _pair_dict(p: CrossReviewPair) -> dict:
    ru = p.reviewer_user
    return {
        "id": p.id, "college_id": p.college_id,
        "target_branch": {"id": p.target_branch.id, "name": p.target_branch.name} if p.target_branch else None,
        "reviewer_branch": {"id": p.reviewer_branch.id, "name": p.reviewer_branch.name} if p.reviewer_branch else None,
        "reviewer_user": {"id": ru.id, "real_name": ru.real_name} if ru else None,
    }


@router.get("/{bid}/cross-review-pairs")
def get_pairs(bid: int, college_id: int | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = db.query(CrossReviewPair).filter(CrossReviewPair.batch_id == bid)
    if college_id:
        q = q.filter(CrossReviewPair.college_id == college_id)
    elif actor.role == "COLLEGE_REVIEWER":
        q = q.filter(CrossReviewPair.college_id == actor.org_id)
    return ok([_pair_dict(p) for p in q.all()])


@router.put("/{bid}/cross-review-pairs")
def set_pairs(bid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    college_id = body.get("college_id")
    if actor.role == "COLLEGE_REVIEWER" and college_id != actor.org_id:
        raise forbidden()
    pairs = body.get("pairs") or []
    seen = set()
    for p in pairs:
        t, r = p.get("target_branch_id"), p.get("reviewer_branch_id")
        if t == r:
            raise unprocessable("不能同支部自查")
        tb = db.query(Org).filter(Org.id == t).first()
        rb = db.query(Org).filter(Org.id == r).first()
        if not tb or not rb or tb.parent_id != college_id or rb.parent_id != college_id:
            raise unprocessable("互查支部必须同学院")
        if t in seen:
            raise unprocessable("重复配对")
        seen.add(t)
    db.query(CrossReviewPair).filter(CrossReviewPair.batch_id == bid, CrossReviewPair.college_id == college_id).delete()
    out = []
    for p in pairs:
        row = CrossReviewPair(
            batch_id=bid, college_id=college_id, target_branch_id=p["target_branch_id"],
            reviewer_branch_id=p["reviewer_branch_id"], reviewer_user_id=p.get("reviewer_user_id"),
            created_by=actor.id, created_at=now(),
        )
        db.add(row)
        db.flush()
        out.append(row)
    log(db, actor, "CROSS_PAIRS", "batch", bid, {"college_id": college_id})
    return ok([_pair_dict(p) for p in out])
