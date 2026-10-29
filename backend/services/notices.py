from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from errors import conflict, unprocessable
from models import Issue, Notice, Submission
from services.messages import send_message
from utils import CATEGORY_NAMES, SEVERITY_NAMES, as_date, now, stage_name


def create_rectification_notice(db: Session, sub: Submission, actor, issue_ids=None, deadline=None, send=True, note=None,
                                *, allow_note_only=False) -> Notice:
    if issue_ids is not None and (not isinstance(issue_ids, list) or any(type(i) is not int or i <= 0 for i in issue_ids)):
        raise unprocessable("问题编号须为正整数列表")
    if type(send) is not bool or (note is not None and not isinstance(note, str)):
        raise unprocessable("发送选项须为布尔值，备注须为文本")
    if deadline is not None and not as_date(deadline):
        raise unprocessable("整改截止日期无效")
    q = db.query(Issue).filter(Issue.submission_id == sub.id, Issue.is_active.is_(True),
                               Issue.review_status.in_(("CONFIRMED", "MODIFIED")), Issue.resolution != "RESOLVED")
    if issue_ids:
        q = q.filter(Issue.id.in_(issue_ids))
    issues = q.order_by(Issue.id).all()
    if issue_ids and set(issue_ids) != {i.id for i in issues}:
        raise unprocessable("只能关联本提交包中有效、已确认且未解决的问题")
    if not issues and not (allow_note_only and (note or "").strip()):
        raise unprocessable("没有已确认问题，无法生成整改通知")
    arch = sub.archive
    items = []
    for i, iss in enumerate(issues, start=1):
        loc = iss.location or {}
        items.append({
            "no": i, "issue_id": iss.id, "category": CATEGORY_NAMES.get(iss.category, iss.category),
            "severity": SEVERITY_NAMES.get(iss.severity, iss.severity),
            "material": None, "location": f"第 {loc.get('page_no')} 页" if loc.get("page_no") else "",
            "problem": iss.description, "basis": iss.rule_basis, "suggestion": iss.suggestion, "example": iss.suggestion_example,
        })
    content = {
        "student": {"name": arch.real_name, "student_no": arch.student_no, "anon_code": arch.anon_code,
                    "branch": arch.branch.name if arch.branch else ""},
        "stage": stage_name(db, sub.stage_code),
        "issued_by": actor.user.real_name,
        "issued_at": now().date().isoformat(),
        "intro": "经 AI 辅助校验与审核，你提交的材料存在以下问题，请于截止日期前完成整改并重新提交。",
        "items": items,
        "completion_items": [],
        "note": note,
    }
    dl = as_date(deadline) or (now().date() + timedelta(days=7))
    notice = Notice(
        notice_type="RECTIFICATION", submission_id=sub.id, archive_id=arch.id,
        student_user_id=arch.student_user_id, report_id=sub.latest_report_id, round_no=sub.round_no,
        title=f"关于{arch.real_name}《{stage_name(db, sub.stage_code)}》阶段材料的整改通知（第 {sub.round_no} 轮）",
        content=content, deadline=dl, status="DRAFT", created_by=actor.id, created_at=now(), updated_at=now(),
    )
    db.add(notice)
    db.flush()
    if send:
        send_notice(db, notice)
    return notice


def create_completion_notice(db, sub: Submission, actor, completeness: dict, deadline=None, send=True, note=None) -> Optional[Notice]:
    missing = [it for it in completeness.get("items") or [] if it.get("missing") and it.get("required")]
    if not missing:
        return None
    arch = sub.archive
    items = []
    for i, it in enumerate(missing, start=1):
        mt = it.get("material_type") or {}
        name = mt.get("name") if isinstance(mt, dict) else it.get("material_type_name")
        items.append({
            "no": i, "material": name, "expected": it.get("expected"), "actual": it.get("actual"),
            "missing": it.get("missing"), "requirement": it.get("requirement_text"),
        })
    content = {
        "student": {"name": arch.real_name, "student_no": arch.student_no, "anon_code": arch.anon_code,
                    "branch": arch.branch.name if arch.branch else ""},
        "stage": stage_name(db, sub.stage_code),
        "issued_by": actor.user.real_name,
        "issued_at": now().date().isoformat(),
        "intro": "对照本阶段材料清单，以下材料尚未交齐，请尽快补交。",
        "items": [],
        "completion_items": items,
        "note": note,
    }
    notice = Notice(
        notice_type="COMPLETION", submission_id=sub.id, archive_id=arch.id, student_user_id=arch.student_user_id,
        report_id=sub.latest_report_id, round_no=sub.round_no,
        title=f"{arch.real_name}《{stage_name(db, sub.stage_code)}》材料补全提示",
        content=content, deadline=as_date(deadline), status="DRAFT",
        created_by=actor.id, created_at=now(), updated_at=now(),
    )
    db.add(notice)
    db.flush()
    if send:
        send_notice(db, notice)
    return notice


def send_notice(db: Session, notice: Notice) -> Notice:
    notice = db.query(Notice).filter(Notice.id == notice.id).with_for_update().populate_existing().one()
    if notice.status == "SENT":
        raise conflict("通知已发送")
    notice.status = "SENT"
    notice.sent_at = now()
    msg_type = "RECTIFICATION" if notice.notice_type == "RECTIFICATION" else "COMPLETION"
    send_message(db, notice.student_user_id, msg_type, notice.title, "", "notice", notice.id)
    db.flush()
    return notice


def serialize_notice(n: Notice, brief=False) -> dict:
    c = n.content or {}
    stu = c.get("student") or {}
    item_count = len(c.get("items") or []) + len(c.get("completion_items") or [])
    data = {
        "id": n.id, "notice_type": n.notice_type, "title": n.title,
        "student_name": stu.get("name"), "student_no": stu.get("student_no"),
        "stage_name": c.get("stage"), "round_no": n.round_no, "item_count": item_count,
        "deadline": n.deadline.isoformat() if n.deadline else None,
        "status": n.status, "sent_at": n.sent_at.isoformat() if n.sent_at else None,
        "created_by_name": n.creator.real_name if n.creator else None,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "submission_id": n.submission_id, "archive_id": n.archive_id, "report_id": n.report_id,
    }
    if not brief:
        data["content"] = c
    return data
