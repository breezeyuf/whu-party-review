from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from errors import conflict, forbidden, unprocessable
from models import (
    AiReport,
    Archive,
    Issue,
    Material,
    MaterialVersion,
    ReviewRecord,
    Submission,
)
from services.messages import notify_role_users, send_message
from services.notices import create_rectification_notice
from services.timeline import lock_stage_nodes
from utils import STATUS_BY_RETURN_LEVEL, now, stage_name

# 通过前校验的唯一口径：有效（is_active）、severity=BLOCK 且 review_status 在此集合内的问题
# 视为未处理。单份通过、批量通过、组织部备案都只调用 ensure_passable()，改口径只改这里。
BLOCKING_REVIEW_STATUSES = ("PENDING",)


def _latest_report(db: Session, sub: Submission) -> Optional[AiReport]:
    if sub.latest_report_id:
        return db.query(AiReport).filter(AiReport.id == sub.latest_report_id).first()
    return (
        db.query(AiReport)
        .filter(AiReport.submission_id == sub.id, AiReport.status == "DONE")
        .order_by(AiReport.report_no.desc())
        .first()
    )


def report_is_stale(db: Session, sub: Submission, report: Optional[AiReport]) -> bool:
    if not report or report.status != "DONE":
        return True
    arch = db.query(Archive).filter(Archive.id == sub.archive_id).first()
    if arch and arch.timeline_updated_at and report.finished_at and arch.timeline_updated_at > report.finished_at:
        return True
    mats = db.query(Material).filter(Material.submission_id == sub.id, Material.status == "ACTIVE").all()
    snap = {m["material_id"]: m.get("version_id") for m in (report.material_versions or []) if isinstance(m, dict)}
    if snap != {m.id: m.current_version_id for m in mats}:
        return True
    for m in mats:
        if report.finished_at and m.updated_at and m.updated_at > report.finished_at:
            return True
    version_ids = [m.current_version_id for m in mats if m.current_version_id]
    if version_ids and report.finished_at:
        from models import ParseResult
        if db.query(ParseResult.id).filter(
            ParseResult.version_id.in_(version_ids), ParseResult.updated_at > report.finished_at,
        ).first():
            return True
    return False


def require_current_report(db: Session, sub: Submission, report: Optional[AiReport]) -> None:
    if sub.ai_status in ("QUEUED", "RUNNING", "FAILED") or report_is_stale(db, sub, report):
        raise conflict("AI 报告已过期或检查未完成，请重新检查", code=40901)


def freeze_versions(db: Session, sub: Submission, frozen: bool) -> None:
    mats = db.query(Material).filter(Material.submission_id == sub.id, Material.status == "ACTIVE").all()
    ids = [m.current_version_id for m in mats if m.current_version_id]
    if ids:
        db.query(MaterialVersion).filter(MaterialVersion.id.in_(ids)).update({"is_frozen": frozen}, synchronize_session=False)


def add_record(db, sub, actor, level, action, from_s, to_s, comment=None, issue_ids=None, is_batch=False, report_id=None):
    rec = ReviewRecord(
        submission_id=sub.id, level=level, action=action, from_status=from_s, to_status=to_s,
        reviewer_id=actor.id, reviewer_name=actor.user.real_name, reviewer_role=actor.role,
        comment=comment, report_id=report_id or sub.latest_report_id, issue_ids=issue_ids or [],
        round_no=sub.round_no, is_batch=is_batch, ip=actor.ip, created_at=now(),
    )
    db.add(rec)
    db.flush()
    return rec


def submit_package(db: Session, sub: Submission, actor, comment: Optional[str] = None) -> dict:
    # 行锁串行化并发提交/审核，双击不会重复推进状态
    sub = db.query(Submission).filter(Submission.id == sub.id).with_for_update().populate_existing().first() or sub
    if sub.status not in ("DRAFT", "RETURNED"):
        raise conflict("当前状态不可提交")
    if sub.status == "DRAFT":
        report = _latest_report(db, sub)
        if not report or report.status != "DONE" or report_is_stale(db, sub, report):
            raise conflict("请先完成 AI 自查", code=40901)
        candidates = (
            db.query(Issue)
            .filter(Issue.submission_id == sub.id, Issue.is_active.is_(True), Issue.severity == "BLOCK",
                    Issue.review_status != "REJECTED")
            .all()
        )
        msg = "存在未回复的阻断问题"
    else:
        # RETURNED: only reviewer-confirmed issues gate resubmission (the student cannot see
        # unconfirmed AI issues); stale reports are fine because resubmit enqueues a RECHECK.
        candidates = (
            db.query(Issue)
            .filter(Issue.submission_id == sub.id, Issue.is_active.is_(True),
                    Issue.review_status.in_(("CONFIRMED", "MODIFIED")))
            .all()
        )
        msg = "存在未回复的已确认问题"
    pending = [iss.id for iss in candidates if not iss.response_type]
    if pending:
        raise conflict(msg, code=40902, data={"issue_ids": pending})
    from_s = sub.status
    if sub.status == "RETURNED":
        to_s = STATUS_BY_RETURN_LEVEL.get(sub.return_level or "BRANCH", "BRANCH_REVIEW")
        action = "RESUBMIT"
        sub.round_no = (sub.round_no or 1) + 1
        # set status together with return_level: enqueue_job autoflushes, and
        # ck_submissions_return requires (status = 'RETURNED') = (return_level IS NOT NULL)
        sub.status = to_s
        sub.return_level = None
        from services.materials import enqueue_job
        job = enqueue_job(db, "AI_CHECK", actor.id, "submission", sub.id,
                          {"submission_id": sub.id, "trigger_type": "RECHECK", "use_llm": True})
        sub.ai_status = "QUEUED"
        sub.ai_job_id = job.id
        recheck_job_id = job.id
    else:
        to_s = "BRANCH_REVIEW"
        action = "SUBMIT"
        recheck_job_id = None
    sub.status = to_s
    sub.submitted_at = now()
    sub.level_entered_at = now()
    freeze_versions(db, sub, True)
    rec = add_record(db, sub, actor, "SELF", action, from_s, to_s, comment)
    notify_role_users(
        db, "BRANCH_REVIEWER", sub.branch_id, msg_type="TASK",
        title=f"{sub.archive.real_name} 已提交{stage_name(db, sub.stage_code)}材料",
        content=comment or "", link_type="submission", link_id=sub.id,
    )
    return {"submission": sub, "review_record_id": rec.id, "recheck_job_id": recheck_job_id}


def _handover_ok(report: Optional[AiReport]) -> bool:
    if not report:
        return False
    if report.handover_status == "REQUIRED":
        return False
    if report.handover_status in ("NOT_REQUIRED", "DONE") and report.effective_recommendation:
        return True
    if report.handover_status == "NOT_REQUIRED":
        return True
    return False


def pending_block_count(db: Session, submission_id: int) -> int:
    """有效、BLOCK、且审核状态仍在 BLOCKING_REVIEW_STATUSES 内的问题数。"""
    return (
        db.query(Issue)
        .filter(
            Issue.submission_id == submission_id,
            Issue.is_active.is_(True),
            Issue.severity == "BLOCK",
            Issue.review_status.in_(BLOCKING_REVIEW_STATUSES),
        )
        .count()
    )


def ensure_passable(db: Session, sub: Submission, report: Optional[AiReport]) -> None:
    """通过前校验：报告有效 → 无未处理阻断 → 人工接管已完成。失败抛 40901/40903/40904。"""
    require_current_report(db, sub, report)
    if pending_block_count(db, sub.id):
        raise conflict("仍有未处理的阻断问题", code=40903)
    if not _handover_ok(report):
        raise conflict("待人工审核", code=40904)


def review_package(db: Session, sub: Submission, actor, level: str, decision: str, comment=None, issue_ids=None, deadline=None, is_batch=False, report_id=None):
    from services.scope import can_review, current_level

    if decision not in ("pass", "return"):
        raise unprocessable("无效的审核决定")
    sub = db.query(Submission).filter(Submission.id == sub.id).with_for_update().populate_existing().first() or sub
    if not can_review(sub, actor, db):
        raise forbidden("当前层级无权审核该提交包")
    expect = current_level(sub)
    if sub.status == "RETURNED":
        raise conflict("退回状态请由学生重新提交")
    mapping = {"BRANCH": "BRANCH_REVIEW", "CROSS": "CROSS_REVIEW", "COLLEGE": "COLLEGE_REVIEW", "ORG": "ORG_FILING"}
    if mapping.get(level) != sub.status:
        raise conflict("审核层级与提交包状态不符")
    report = _latest_report(db, sub)
    if report_id is not None and (not report or report.id != report_id):
        raise conflict("审核报告已更新，请刷新工作区", code=40901)
    if decision == "pass":
        # ORG 层级检查先于报告校验：组织部误调本接口时直接提示改用备案接口
        if level == "ORG":
            raise conflict("组织部通过请调用备案接口")
        ensure_passable(db, sub, report)
        from_s = sub.status
        if sub.status == "BRANCH_REVIEW":
            from models import CrossReviewPair
            pair = (
                db.query(CrossReviewPair)
                .filter(CrossReviewPair.batch_id == sub.batch_id, CrossReviewPair.target_branch_id == sub.branch_id)
                .first()
            )
            to_s = "CROSS_REVIEW" if pair else "COLLEGE_REVIEW"
        elif sub.status == "CROSS_REVIEW":
            to_s = "COLLEGE_REVIEW"
        else:
            to_s = "ORG_FILING"
        sub.status = to_s
        sub.level_entered_at = now()
        rec = add_record(db, sub, actor, level, "PASS", from_s, to_s, comment, is_batch=is_batch, report_id=report_id)
        send_message(db, sub.archive.student_user_id, "PASSED", f"{stage_name(db, sub.stage_code)}已通过{level}审核",
                     comment or "", "submission", sub.id)
        return {"submission": sub, "review_record_id": rec.id, "notice_id": None}
    # return
    ids = issue_ids or []
    if ids:
        if not isinstance(ids, list) or any(type(i) is not int for i in ids):
            raise unprocessable("问题 id 必须为整数列表")
        valid_ids = {i for (i,) in db.query(Issue.id).filter(
            Issue.submission_id == sub.id, Issue.is_active.is_(True), Issue.id.in_(ids),
            Issue.review_status.in_(("CONFIRMED", "MODIFIED")),
            Issue.resolution != "RESOLVED",
        ).all()}
        if set(ids) != valid_ids:
            raise unprocessable("退回只能关联本提交包的有效已确认问题")
    confirmed = (
        db.query(Issue)
        .filter(Issue.submission_id == sub.id, Issue.id.in_(ids) if ids else Issue.id > 0,
                Issue.review_status.in_(("CONFIRMED", "MODIFIED")))
        .count()
        if ids else 0
    )
    if not ids:
        confirmed = (
            db.query(Issue)
            .filter(Issue.submission_id == sub.id, Issue.is_active.is_(True),
                    Issue.resolution != "RESOLVED",
                    Issue.review_status.in_(("CONFIRMED", "MODIFIED")))
            .count()
        )
        ids = [i.id for i in db.query(Issue).filter(Issue.submission_id == sub.id, Issue.is_active.is_(True),
                                                    Issue.resolution != "RESOLVED",
                                                    Issue.review_status.in_(("CONFIRMED", "MODIFIED"))).all()]
    if confirmed == 0 and not (comment or "").strip():
        raise unprocessable("退回须至少选择 1 条已确认问题或填写审核意见")
    from_s = sub.status
    sub.return_level = level
    sub.status = "RETURNED"
    sub.level_entered_at = now()
    freeze_versions(db, sub, False)
    rec = add_record(db, sub, actor, level, "RETURN", from_s, "RETURNED", comment, ids, is_batch, report_id)
    notice = create_rectification_notice(db, sub, actor, ids, deadline, send=True, note=comment, allow_note_only=True)
    send_message(db, sub.archive.student_user_id, "RETURNED",
                 f"{stage_name(db, sub.stage_code)}材料已退回，请按整改通知修改",
                 comment or "", "notice", notice.id if notice else sub.id)
    return {"submission": sub, "review_record_id": rec.id, "notice_id": notice.id if notice else None}


def file_package(db: Session, sub: Submission, actor, comment=None):
    sub = db.query(Submission).filter(Submission.id == sub.id).with_for_update().populate_existing().first() or sub
    if sub.status != "ORG_FILING":
        raise conflict("仅组织部备案阶段可备案")
    if actor.role != "ORG_ADMIN":
        raise forbidden()
    report = _latest_report(db, sub)
    ensure_passable(db, sub, report)
    from_s = sub.status
    sub.status = "FILED"
    sub.filed_at = now()
    sub.filed_by = actor.id
    sub.level_entered_at = now()
    rec = add_record(db, sub, actor, "ORG", "FILE", from_s, "FILED", comment)
    arch = db.query(Archive).filter(Archive.id == sub.archive_id).first()
    lock_stage_nodes(db, arch, sub.stage_code)
    next_id = None
    if arch.current_stage < 5:
        arch.current_stage = arch.current_stage + 1
        existing = db.query(Submission).filter(Submission.archive_id == arch.id, Submission.stage_code == arch.current_stage).first()
        if not existing:
            nxt = Submission(
                archive_id=arch.id, stage_code=arch.current_stage, batch_id=arch.batch_id,
                college_id=arch.college_id, branch_id=arch.branch_id, status="DRAFT",
                round_no=1, ai_status="NONE", created_at=now(), updated_at=now(),
            )
            db.add(nxt)
            db.flush()
            next_id = nxt.id
        else:
            next_id = existing.id
    else:
        arch.status = "COMPLETED"
    send_message(db, arch.student_user_id, "FILED", f"{stage_name(db, sub.stage_code)}已备案",
                 comment or "", "archive", arch.id)
    return {"submission": sub, "archive": arch, "next_submission_id": next_id, "review_record_id": rec.id}


def can_actions(db, sub: Submission, actor) -> dict:
    from services.scope import can_review, current_level
    st = sub.status
    is_student = actor.role == "STUDENT"
    owner = is_student and sub.archive.student_user_id == actor.id
    review = can_review(sub, actor, db)
    return {
        "upload": (owner and st in ("DRAFT", "RETURNED")) or (actor.role == "BRANCH_REVIEWER" and st in ("DRAFT", "RETURNED")),
        "self_check": owner and st in ("DRAFT", "RETURNED"),
        "submit": owner and st in ("DRAFT", "RETURNED"),
        "ai_check": review or ((owner or actor.role == "BRANCH_REVIEWER") and st in ("DRAFT", "RETURNED")),
        "handover": review and bool(sub.latest_report_id) and bool(
            (report := _latest_report(db, sub)) and report.handover_status == "REQUIRED"
        ),
        "review": review,
        "file": actor.role == "ORG_ADMIN" and st == "ORG_FILING",
        "add_issue": review,
        "edit_timeline": actor.role in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"),
    }
