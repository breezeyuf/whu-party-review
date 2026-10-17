from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden, not_found, unprocessable
from models import Issue, Material, Submission
from schemas.common import ok
from services.audit import log
from services.issues import act_issue, respond_issue, serialize_issue
from services.scope import REVIEWER_ROLES, can_review, current_level, ensure_submission_access
from utils import now

router = APIRouter(tags=["issues"])


@router.get("/submissions/{sid}/issues")
def list_issues(sid: int, category: str | None = None, severity: str | None = None, review_status: str | None = None,
                resolution: str | None = None, material_id: int | None = None, source: str | None = None,
                active: bool = True, report_id: int | None = None, request: Request = None,
                db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    q = db.query(Issue).filter(Issue.submission_id == sid)
    if active:
        q = q.filter(Issue.is_active.is_(True))
    if category:
        q = q.filter(Issue.category == category)
    if severity:
        q = q.filter(Issue.severity == severity)
    if review_status:
        q = q.filter(Issue.review_status == review_status)
    if resolution:
        q = q.filter(Issue.resolution == resolution)
    if material_id:
        q = q.filter(Issue.material_id == material_id)
    if source:
        q = q.filter(Issue.source == source)
    if report_id:
        q = q.filter((Issue.report_id == report_id) | (Issue.source == "MANUAL"))
    items = q.order_by(Issue.severity, Issue.id).all()
    if actor.role == "STUDENT" and s.status == "RETURNED":
        items = [i for i in items if i.review_status in ("CONFIRMED", "MODIFIED") or i.source == "MANUAL"]
    by_cat = dict(Counter(i.category for i in items))
    by_sev = dict(Counter(i.severity for i in items))
    by_rev = dict(Counter(i.review_status for i in items))
    pending_block = sum(1 for i in items if i.severity == "BLOCK" and i.review_status == "PENDING")
    return ok({
        "items": [serialize_issue(i) for i in items],
        "counts": {"by_category": by_cat, "by_severity": by_sev, "by_review_status": by_rev, "pending_block": pending_block},
    })


@router.post("/submissions/{sid}/issues")
def add_issue(sid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    if actor.role not in ("BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    if not can_review(s, actor, db):
        raise forbidden("当前审核层级不可新增问题")
    level = {"BRANCH_REVIEWER": "BRANCH", "CROSS_REVIEWER": "CROSS", "COLLEGE_REVIEWER": "COLLEGE", "ORG_ADMIN": "ORG"}[actor.role]
    category = body.get("category")
    severity = body.get("severity")
    title = (body.get("title") or "").strip()
    description = (body.get("description") or "").strip()
    if not category or not severity or not title or not description:
        raise unprocessable("缺少必填字段：category、severity、title、description")
    if category not in ("COMPLETENESS", "TIME", "FORMAT", "CONTENT") or severity not in ("BLOCK", "WARN", "INFO"):
        raise unprocessable("问题类别或级别无效")
    if body.get("material_id") and not db.query(Material.id).filter(
        Material.id == body["material_id"], Material.submission_id == sid, Material.status == "ACTIVE",
    ).first():
        raise unprocessable("材料不属于当前提交包")
    iss = Issue(
        submission_id=sid, report_id=None, material_id=body.get("material_id"),
        source="MANUAL", category=category, severity=severity,
        rule_code=body.get("rule_code"), title=title, description=description,
        location=body.get("location") or {}, suggestion=body.get("suggestion"),
        review_status="CONFIRMED", created_by=actor.id, created_level=level,
        is_active=True, created_at=now(), updated_at=now(),
    )
    db.add(iss)
    db.flush()
    log(db, actor, "ISSUE_ADD", "issue", iss.id, {})
    return ok(serialize_issue(iss))


@router.put("/issues/{iid}")
def put_issue(iid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    iss = db.query(Issue).filter(Issue.id == iid).first()
    if not iss:
        raise not_found()
    s = ensure_submission_access(db, actor, iss.submission_id, request)
    if not iss.is_active or not can_review(s, actor, db):
        raise forbidden("仅当前层级审核员可处理有效问题")
    act_issue(db, iss, actor, body.get("action"), body.get("note"), body.get("patch"))
    return ok(serialize_issue(iss))


@router.put("/issues/{iid}/response")
def put_response(iid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    iss = db.query(Issue).filter(Issue.id == iid).first()
    if not iss:
        raise not_found()
    ensure_submission_access(db, actor, iss.submission_id, request)
    respond_issue(db, iss, actor, body.get("response_type"), body.get("response_text") or "", body.get("version_id"))
    return ok(serialize_issue(iss))
