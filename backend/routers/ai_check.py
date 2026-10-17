from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, not_found, unprocessable
from models import AiReport, HandoverRecord, Issue, Job, Material, RuleVersion, Submission
from schemas.common import ok
from services.audit import log
from services.materials import enqueue_job
from services.notices import create_completion_notice
from services.scope import can_review, ensure_submission_access, scoped_submissions
from services.issues import serialize_issue
from ai.checks.completeness import run_completeness
from services.timeline import node_map_for_archive
from utils import now

router = APIRouter(tags=["ai"])

DISCLAIMER = "AI 结论仅作审核参考，未发现问题不等于审核合格，最终结论以审核人员确认为准。"


@router.post("/submissions/{sid}/ai-check")
def ai_check(sid: int, body: dict | None = None, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    from services.workflow import can_actions
    if not can_actions(db, s, actor)["ai_check"]:
        raise forbidden("当前状态或角色不可发起 AI 检查")
    s = db.query(Submission).filter(Submission.id == sid).with_for_update().populate_existing().one()
    existing = db.query(Job).filter(Job.target_type == "submission", Job.target_id == sid, Job.job_type == "AI_CHECK", Job.status.in_(("QUEUED", "RUNNING"))).first()
    if existing:
        return ok({"job_id": existing.id, "report_no": None})
    trig = "SELF_CHECK" if actor.role == "STUDENT" else "REVIEW"
    use_llm = (body or {}).get("use_llm", True)
    job = enqueue_job(db, "AI_CHECK", actor.id, "submission", sid, {"submission_id": sid, "trigger_type": trig, "use_llm": use_llm})
    s.ai_status = "QUEUED"
    s.ai_job_id = job.id
    last = db.query(AiReport.report_no).filter(AiReport.submission_id == sid).order_by(AiReport.report_no.desc()).first()
    log(db, actor, "AI_CHECK", "submission", sid, {})
    return ok({"job_id": job.id, "report_no": (last[0] + 1) if last else 1})


@router.post("/ai-check/batch")
def batch_ai(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    ids = body.get("submission_ids")
    q = scoped_submissions(db.query(Submission), actor, db)
    allowed_states = {
        "BRANCH_REVIEWER": ("DRAFT", "RETURNED", "BRANCH_REVIEW"),
        "COLLEGE_REVIEWER": ("COLLEGE_REVIEW",),
        "ORG_ADMIN": ("ORG_FILING",),
    }
    q = q.filter(Submission.status.in_(allowed_states[actor.role]))
    if ids:
        q = q.filter(Submission.id.in_(ids))
    else:
        if body.get("batch_id"):
            q = q.filter(Submission.batch_id == body["batch_id"])
        if body.get("branch_id"):
            q = q.filter(Submission.branch_id == body["branch_id"])
        if body.get("stage_code"):
            q = q.filter(Submission.stage_code == body["stage_code"])
        if body.get("status"):
            q = q.filter(Submission.status == body["status"])
    ids = [s.id for s in q.all()]
    if not ids:
        raise unprocessable("没有可检查的提交包")
    job = enqueue_job(db, "BATCH_AI_CHECK", actor.id, "batch", body.get("batch_id"), {"submission_ids": ids}, total=len(ids))
    return ok({"job_id": job.id, "total": len(ids)})


@router.get("/submissions/{sid}/reports")
def list_reports(sid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    rows = db.query(AiReport).filter(AiReport.submission_id == sid).order_by(AiReport.report_no.desc()).all()
    from services.workflow import report_is_stale
    out = []
    for r in rows:
        rv = db.query(RuleVersion).filter(RuleVersion.id == r.rule_version_id).first()
        out.append({
            "id": r.id, "report_no": r.report_no, "trigger_type": r.trigger_type, "mode": r.mode, "status": r.status,
            "recommendation": r.recommendation, "summary": r.summary, "rule_version_no": rv.version_no if rv else None,
            "llm_model": r.llm_model, "degrade_reason": r.degrade_reason,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "is_latest": r.id == s.latest_report_id, "is_stale": report_is_stale(db, s, r),
            "handover_status": r.handover_status, "effective_recommendation": r.effective_recommendation,
        })
    return ok(out)


@router.get("/reports/{rid}")
def get_report(rid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    r = db.query(AiReport).filter(AiReport.id == rid).first()
    if not r:
        raise not_found()
    s = ensure_submission_access(db, actor, r.submission_id, request)
    issues = db.query(Issue).filter(Issue.report_id == rid).all()
    grouped = defaultdict(list)
    for i in issues:
        grouped[i.category].append(serialize_issue(i))
    rv = db.query(RuleVersion).filter(RuleVersion.id == r.rule_version_id).first()
    from services.workflow import report_is_stale
    return ok({
        "id": r.id, "submission_id": r.submission_id, "report_no": r.report_no, "trigger_type": r.trigger_type,
        "status": r.status, "mode": r.mode, "degrade_reason": r.degrade_reason, "llm_model": r.llm_model,
        "ocr_engine": r.ocr_engine, "rule_version": {"id": rv.id, "version_no": rv.version_no} if rv else None,
        "is_latest": r.id == s.latest_report_id, "is_stale": report_is_stale(db, s, r),
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        "duration_ms": r.duration_ms, "recommendation": r.recommendation,
        "handover_status": r.handover_status, "handover_reasons": r.handover_reasons,
        "effective_recommendation": r.effective_recommendation, "disclaimer": DISCLAIMER,
        "summary": r.summary, "classification": r.classification, "completeness": r.completeness,
        "timeline_snapshot": r.timeline_snapshot, "rule_results": r.rule_results,
        "issues_by_category": dict(grouped), "recheck_summary": r.recheck_summary,
    })


@router.get("/submissions/{sid}/completeness")
def completeness(sid: int, live: bool = False, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    if not live and s.latest_report_id:
        r = db.query(AiReport).filter(AiReport.id == s.latest_report_id).first()
        if r and r.completeness:
            data = dict(r.completeness)
            data["computed_at"] = r.finished_at.isoformat() if r.finished_at else None
            return ok(data)
    mats = db.query(Material).filter(Material.submission_id == sid, Material.status == "ACTIVE").all()
    from ai.checks.completeness import run_completeness as rc
    from ai.dsl import NodeVal
    from utils import as_date
    nm = node_map_for_archive(db, s.archive_id)
    nodes = {}
    for c, n in nm.items():
        nodes[c] = type("N", (), {"date": as_date(n.get("date")), "end": as_date(n.get("end")), "hours": n.get("hours"), "seq": n.get("seq") or [], "missing": not n.get("date")})()
    comp, _, _ = rc(db, s, mats, nodes)
    comp["computed_at"] = now().isoformat()
    return ok(comp)


@router.post("/submissions/completion-notices")
def completion_notices(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    created, skipped = [], []
    for sid in body.get("submission_ids") or []:
        s = ensure_submission_access(db, actor, sid)
        from ai.checks.completeness import run_completeness as rc
        from utils import as_date
        mats = db.query(Material).filter(Material.submission_id == sid, Material.status == "ACTIVE").all()
        nm = node_map_for_archive(db, s.archive_id)
        nodes = {c: type("N", (), {"date": as_date(n.get("date")), "end": as_date(n.get("end")), "hours": n.get("hours"), "seq": n.get("seq") or [], "missing": not n.get("date")})() for c, n in nm.items()}
        comp, _, _ = rc(db, s, mats, nodes)
        notice = create_completion_notice(db, s, actor, comp, body.get("deadline"), body.get("send", True), body.get("note"))
        if notice:
            created.append({"notice_id": notice.id, "submission_id": sid, "student_name": s.archive.real_name, "missing_total": comp.get("missing_total")})
        else:
            skipped.append({"submission_id": sid, "reason": "材料已齐全"})
    return ok({"created": created, "skipped": skipped})


@router.get("/reports/{rid}/handover")
def get_handover(rid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    r = db.query(AiReport).filter(AiReport.id == rid).first()
    if not r:
        raise not_found()
    ensure_submission_access(db, actor, r.submission_id, request)
    mats = db.query(Material).filter(Material.submission_id == r.submission_id, Material.status == "ACTIVE").all()
    issues = db.query(Issue).filter(Issue.report_id == rid).all()
    recs = db.query(HandoverRecord).filter(HandoverRecord.report_id == rid).order_by(HandoverRecord.decided_at).all()
    reasons = [{"code": c, "detail": c} for c in (r.handover_reasons or [])]
    return ok({
        "required": r.handover_status == "REQUIRED" or bool(r.handover_reasons),
        "status": r.handover_status,
        "reasons": reasons,
        "ai_recommendation": r.recommendation,
        "effective_recommendation": r.effective_recommendation,
        "materials": [{"material_id": m.id, "title": m.title, "type_code": m.type.code if m.type else None, "type_status": m.type_status, "confidence": m.type_confidence} for m in mats],
        "issues": [{"id": i.id, "severity": i.severity, "title": i.title, "confidence": i.confidence, "needs_human_judgement": i.needs_human_judgement} for i in issues],
        "records": [{
            "id": h.id, "assignee_name": h.assignee_name, "assignee_role": h.assignee_role,
            "human_decision": h.human_decision, "effective_recommendation": h.effective_recommendation,
            "handover_reason": h.handover_reason, "issue_ids": h.issue_ids,
            "decided_at": h.decided_at.isoformat() if h.decided_at else None,
        } for h in recs],
    })


@router.post("/reports/{rid}/handover")
def post_handover(rid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    r = db.query(AiReport).filter(AiReport.id == rid).first()
    if not r:
        raise not_found()
    s = ensure_submission_access(db, actor, r.submission_id, request)
    s = db.query(Submission).filter(Submission.id == s.id).with_for_update().populate_existing().one()
    r = db.query(AiReport).filter(AiReport.id == rid).with_for_update().populate_existing().one()
    if not can_review(s, actor, db):
        raise forbidden("仅当前层级审核员可接管")
    from services.workflow import require_current_report
    if s.latest_report_id != r.id:
        raise conflict("仅可接管最新报告")
    require_current_report(db, s, r)
    if r.status != "DONE":
        raise conflict("报告未完成")
    if r.handover_status != "REQUIRED":
        raise conflict("当前报告无需接管或已接管")
    decision = body.get("human_decision")
    if decision not in ("CONFIRM", "OVERRIDE_PASS", "OVERRIDE_RETURN"):
        raise unprocessable("无效的人工结论")
    reason = (body.get("handover_reason") or "").strip()
    issue_ids = body.get("issue_ids") or []
    if not reason:
        raise unprocessable("接管须填写原因")
    if not isinstance(issue_ids, list) or any(type(i) is not int for i in issue_ids):
        raise unprocessable("问题 id 必须为整数列表")
    if issue_ids:
        valid_ids = {i for (i,) in db.query(Issue.id).filter(
            Issue.submission_id == s.id, Issue.is_active.is_(True), Issue.id.in_(issue_ids),
            (Issue.report_id == r.id) | (Issue.source == "MANUAL"),
        ).all()}
        if set(issue_ids) != valid_ids:
            raise unprocessable("只能关联本报告或本提交包的有效人工问题")
    if decision.startswith("OVERRIDE"):
        if len(reason) < 10:
            raise unprocessable("改判须填写不少于 10 字理由")
        if not issue_ids:
            raise unprocessable("改判须标明问题 id")
    mapping = {"CONFIRM": r.recommendation, "OVERRIDE_PASS": "SUGGEST_PASS", "OVERRIDE_RETURN": "SUGGEST_RETURN"}
    eff = mapping[decision]
    rec = HandoverRecord(
        report_id=r.id, submission_id=s.id, assignee_id=actor.id, assignee_name=actor.user.real_name,
        assignee_role=actor.role, reason_codes=r.handover_reasons or [], handover_reason=reason,
        ai_recommendation=r.recommendation, human_decision=decision, effective_recommendation=eff,
        issue_ids=issue_ids, material_ids=[], confidence_snapshot={"degrade_reason": r.degrade_reason},
        decided_at=now(), ip=actor.ip,
    )
    db.add(rec)
    r.handover_status = "DONE"
    r.effective_recommendation = eff
    db.flush()
    log(db, actor, "HANDOVER", "report", r.id, {"decision": decision})
    return ok({
        "id": rec.id, "report_id": r.id, "submission_id": s.id, "assignee_name": rec.assignee_name,
        "assignee_role": rec.assignee_role, "human_decision": rec.human_decision,
        "effective_recommendation": rec.effective_recommendation, "handover_reason": rec.handover_reason,
        "issue_ids": rec.issue_ids, "decided_at": rec.decided_at.isoformat(),
        "ai_recommendation": rec.ai_recommendation, "reason_codes": rec.reason_codes,
    })
