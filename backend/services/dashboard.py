from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import AiReport, Archive, Batch, Issue, Material, Message, Submission
from services.scope import scoped_archives, scoped_submissions
from utils import now, stage_name


def _deadline_of(s: Submission):
    b = s.archive.batch if s.archive else None
    if not b:
        return None
    mapping = {
        "DRAFT": b.self_deadline, "RETURNED": b.self_deadline, "BRANCH_REVIEW": b.branch_deadline,
        "CROSS_REVIEW": b.cross_deadline, "COLLEGE_REVIEW": b.college_deadline, "ORG_FILING": b.org_deadline,
    }
    return mapping.get(s.status)


def dashboard(db: Session, actor, batch_id=None) -> dict:
    if actor.role == "STUDENT":
        return student_dashboard(db, actor)
    if batch_id:
        batch = db.query(Batch).filter(Batch.id == int(batch_id)).first()
    else:
        batch = db.query(Batch).filter(Batch.status == "ACTIVE").order_by(Batch.id.desc()).first()
    q = scoped_submissions(db.query(Submission), actor, db)
    if batch_id:
        q = q.filter(Submission.batch_id == int(batch_id))
    subs = q.all()
    to_review = 0
    returned_waiting = 0
    pending_ai = 0
    due_soon = 0
    today = now().date()
    by_stage = defaultdict(Counter)
    deadlines = []
    for s in subs:
        by_stage[s.stage_code][s.status] += 1
        if actor.role == "BRANCH_REVIEWER" and s.status == "BRANCH_REVIEW":
            to_review += 1
        if actor.role == "CROSS_REVIEWER" and s.status == "CROSS_REVIEW":
            to_review += 1
        if actor.role == "COLLEGE_REVIEWER" and s.status == "COLLEGE_REVIEW":
            to_review += 1
        if actor.role == "ORG_ADMIN" and s.status == "ORG_FILING":
            to_review += 1
        if s.status == "RETURNED":
            returned_waiting += 1
        if s.ai_status in ("QUEUED", "RUNNING"):
            pending_ai += 1
        dl = _deadline_of(s)
        if dl and s.status not in ("FILED",) and (dl - today).days <= 7:
            deadlines.append({
                "submission_id": s.id,
                "student_name": s.archive.real_name if s.archive else None,
                "deadline": dl.isoformat(),
                "days_left": (dl - today).days,
            })
    due_soon = sum(1 for d in deadlines if d["days_left"] >= 0)
    deadlines.sort(key=lambda d: d["days_left"])
    deadlines = deadlines[:8]
    def scoped_issues(cols):
        iq = scoped_submissions(db.query(*cols).join(Submission, Submission.id == Issue.submission_id), actor, db)
        iq = iq.filter(Issue.is_active.is_(True))
        if batch_id:
            iq = iq.filter(Submission.batch_id == int(batch_id))
        return iq

    dist = {k: v for k, v in scoped_issues((Issue.category, func.count(Issue.id))).group_by(Issue.category).all()}
    top = (
        scoped_issues((Issue.rule_code, Issue.title, func.count(Issue.id)))
        .filter(Issue.rule_code.isnot(None))
        .group_by(Issue.rule_code, Issue.title)
        .order_by(func.count(Issue.id).desc())
        .limit(5)
        .all()
    )
    msgs = db.query(Message).filter(Message.user_id == actor.id).order_by(Message.created_at.desc()).limit(5).all()
    progress = [{"stage_code": sc, **dict(ct)} for sc, ct in by_stage.items()]
    return {
        "role": actor.role,
        "batch": {
            "id": batch.id, "name": batch.name,
            "self_deadline": batch.self_deadline.isoformat() if batch.self_deadline else None,
            "branch_deadline": batch.branch_deadline.isoformat() if batch.branch_deadline else None,
        } if batch else None,
        "todo": {"to_review": to_review, "returned_waiting": returned_waiting, "pending_ai": pending_ai, "due_soon": due_soon},
        "progress": {"by_stage": progress},
        "issue_distribution": dist,
        "top_rules": [{"rule_code": a, "name": b, "count": c} for a, b, c in top],
        "deadlines": deadlines,
        "recent_messages": [{"id": m.id, "title": m.title, "created_at": m.created_at.isoformat() if m.created_at else None} for m in msgs],
    }


def student_dashboard(db, actor) -> dict:
    arch = db.query(Archive).filter(Archive.student_user_id == actor.id).first()
    if not arch:
        return {"role": "STUDENT", "archive_id": None, "next_action": "暂无发展档案"}
    sub = db.query(Submission).filter(Submission.archive_id == arch.id, Submission.stage_code == arch.current_stage).first()
    open_issues = {"BLOCK": 0, "WARN": 0, "INFO": 0}
    if sub:
        rows = db.query(Issue.severity, func.count(Issue.id)).filter(
            Issue.submission_id == sub.id, Issue.is_active.is_(True)
        ).group_by(Issue.severity).all()
        for s, n in rows:
            open_issues[s] = n
    from services.timeline import node_map_for_archive
    nm = node_map_for_archive(db, arch.id)
    preview = [{"code": c, "date": n.get("date")} for c, n in nm.items() if n.get("date")][:6]
    next_action = "请上传材料并发起 AI 自查"
    if sub:
        if sub.status == "RETURNED":
            next_action = f"请处理整改问题后重新提交"
        elif sub.status == "DRAFT" and sub.ai_status == "DONE":
            next_action = "请提交党支部审核"
        elif sub.status not in ("DRAFT", "RETURNED"):
            next_action = "等待上级审核"
    return {
        "role": "STUDENT",
        "archive_id": arch.id,
        "current_stage": arch.current_stage,
        "stage_name": stage_name(db, arch.current_stage),
        "submission": {
            "id": sub.id if sub else None, "status": sub.status if sub else None,
            "round_no": sub.round_no if sub else None,
        } if sub else None,
        "next_action": next_action,
        "checklist_progress": {"expected": 0, "actual": 0},
        "open_issues": open_issues,
        "timeline_preview": preview,
    }
