from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased, selectinload

from database import get_db
from deps import Actor, get_current_user
from errors import AppError, conflict, forbidden, not_found, unprocessable
from models import AiReport, Archive, Batch, Issue, Material, MaterialVersion, ReviewRecord, Submission
from schemas.common import ok, page_params
from services.audit import log
from services.scope import can_review, current_level, ensure_archive_access, ensure_submission_access, scoped_submissions
from services.workflow import can_actions, file_package, review_package, submit_package
from utils import LEVEL_BY_STATUS, now, stage_name

router = APIRouter(tags=["submissions"])


def _deadline_expr(db):
    """当前层级截止日的相关标量子查询：排序（days_left）与筛选（due_within_days）共用同一口径。"""
    from sqlalchemy import case
    from sqlalchemy.orm import aliased

    s2, a2, b2 = aliased(Submission), aliased(Archive), aliased(Batch)
    return (
        db.query(
            case(
                (s2.status.in_(("DRAFT", "RETURNED")), b2.self_deadline),
                (s2.status == "BRANCH_REVIEW", b2.branch_deadline),
                (s2.status == "CROSS_REVIEW", b2.cross_deadline),
                (s2.status == "COLLEGE_REVIEW", b2.college_deadline),
                (s2.status == "ORG_FILING", b2.org_deadline),
                else_=None,
            )
        )
        .select_from(s2)
        .join(a2, a2.id == s2.archive_id)
        .join(b2, b2.id == a2.batch_id)
        .filter(s2.id == Submission.id)
        .scalar_subquery()
    )


def _deadline_of(sub: Submission):
    b = sub.archive.batch if sub.archive else None
    if not b:
        return None
    mapping = {
        "DRAFT": b.self_deadline, "RETURNED": b.self_deadline, "BRANCH_REVIEW": b.branch_deadline,
        "CROSS_REVIEW": b.cross_deadline, "COLLEGE_REVIEW": b.college_deadline, "ORG_FILING": b.org_deadline,
    }
    return mapping.get(sub.status)


@router.get("/submissions")
def list_submissions(
    todo: bool = False, level: str | None = None, batch_id: int | None = None, branch_id: int | None = None,
    stage_code: int | None = None, status: str | None = None, recommendation: str | None = None,
    has_block: bool | None = None, min_issues: int | None = None, q: str | None = None,
    due_within_days: int | None = Query(None, ge=0, le=3650),
    page: int = 1, page_size: int = 20, sort: str | None = None,
    db: Session = Depends(get_db), actor: Actor = Depends(get_current_user),
):
    query = scoped_submissions(
        db.query(Submission).options(selectinload(Submission.archive).selectinload(Archive.branch), selectinload(Submission.archive).selectinload(Archive.batch)),
        actor, db,
    )
    if actor.role == "STUDENT":
        pass
    if batch_id:
        query = query.filter(Submission.batch_id == batch_id)
    if branch_id:
        query = query.filter(Submission.branch_id == branch_id)
    if stage_code:
        query = query.filter(Submission.stage_code == stage_code)
    if status:
        query = query.filter(Submission.status == status)
    if todo:
        mapping = {
            "BRANCH_REVIEWER": "BRANCH_REVIEW", "CROSS_REVIEWER": "CROSS_REVIEW",
            "COLLEGE_REVIEWER": "COLLEGE_REVIEW", "ORG_ADMIN": "ORG_FILING",
        }
        if actor.role in mapping:
            query = query.filter(Submission.status == mapping[actor.role])
    if level:
        mapping = {"BRANCH": "BRANCH_REVIEW", "CROSS": "CROSS_REVIEW", "COLLEGE": "COLLEGE_REVIEW", "ORG": "ORG_FILING"}
        if level in mapping:
            query = query.filter(Submission.status == mapping[level])
    if q:
        # 用 EXISTS 而不是 JOIN：学生角色的范围查询本身已 JOIN archives，再 JOIN 会重复/冲突；
        # 子查询用别名，避免外层已有 archives 时被自动相关掉
        like = f"%{q}%"
        a2 = aliased(Archive)
        query = query.filter(
            db.query(a2.id)
            .filter(a2.id == Submission.archive_id, a2.real_name.ilike(like) | a2.student_no.ilike(like))
            .exists()
        )
    # 过滤条件下推到 SQL，保证分页条数与 total 一致
    issue_active_cnt = (
        db.query(func.count(Issue.id))
        .filter(Issue.submission_id == Submission.id, Issue.is_active.is_(True))
        .scalar_subquery()
    )
    if min_issues:
        query = query.filter(issue_active_cnt >= int(min_issues))
    if has_block is not None:
        # 与列表 issue_counts.BLOCK 同源：只看 is_active + severity='BLOCK'，不看审核状态
        block_exists = (
            db.query(Issue.id)
            .filter(Issue.submission_id == Submission.id, Issue.is_active.is_(True), Issue.severity == "BLOCK")
            .exists()
        )
        query = query.filter(block_exists if has_block else ~block_exists)
    if due_within_days is not None:
        # 与 days_left 同一截止日表达式和同一个“今天”：截止日不为空且 <= 今天 + N（含已逾期）
        deadline_expr = _deadline_expr(db)
        query = query.filter(deadline_expr.is_not(None), deadline_expr <= now().date() + timedelta(days=due_within_days))
    if recommendation:
        query = query.join(AiReport, AiReport.id == Submission.latest_report_id).filter(
            func.coalesce(AiReport.effective_recommendation, AiReport.recommendation) == recommendation
        )
    page, page_size = page_params(page, page_size)
    total = query.count()
    # 排序（白名单）：submitted_at / issue_count / days_left / id
    sort_key = (sort or "-submitted_at").strip()
    desc_order = sort_key.startswith("-")
    key = sort_key.lstrip("-")
    if key == "issue_count":
        order_expr = issue_active_cnt
    elif key in ("days_left", "deadline"):
        order_expr = _deadline_expr(db)
    elif key == "id":
        order_expr = Submission.id
    else:
        order_expr = Submission.submitted_at
    if key not in ("issue_count", "id"):
        order_expr = order_expr.desc().nullslast() if desc_order else order_expr.asc().nullslast()
    elif desc_order:
        order_expr = order_expr.desc()
    rows = query.order_by(order_expr, Submission.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    # 批量装配报告与问题计数，避免逐行查询
    ids = [s.id for s in rows]
    rep_map = {}
    rep_ids = [s.latest_report_id for s in rows if s.latest_report_id]
    if rep_ids:
        rep_map = {r.id: r for r in db.query(AiReport).filter(AiReport.id.in_(rep_ids)).all()}
    sev_map: dict[int, dict] = {}
    pend_map: dict[int, int] = {}
    if ids:
        for sid, sev, n in (
            db.query(Issue.submission_id, Issue.severity, func.count(Issue.id))
            .filter(Issue.submission_id.in_(ids), Issue.is_active.is_(True))
            .group_by(Issue.submission_id, Issue.severity)
        ):
            sev_map.setdefault(sid, {})[sev] = n
        for sid, n in (
            db.query(Issue.submission_id, func.count(Issue.id))
            .filter(Issue.submission_id.in_(ids), Issue.is_active.is_(True), Issue.review_status == "PENDING")
            .group_by(Issue.submission_id)
        ):
            pend_map[sid] = n
    items = []
    today = now().date()
    for s in rows:
        a = s.archive
        report = rep_map.get(s.latest_report_id) if s.latest_report_id else None
        dl = _deadline_of(s)
        days_left = (dl - today).days if dl else None
        rec = (report.effective_recommendation or report.recommendation) if report else None
        counts = {"BLOCK": 0, "WARN": 0, "INFO": 0}
        counts.update(sev_map.get(s.id) or {})
        pending = pend_map.get(s.id, 0)
        items.append({
            "id": s.id, "archive_id": s.archive_id, "student_no": a.student_no if a else None,
            "student_name": a.real_name if a else None,
            "branch_name": a.branch.name if a and a.branch else None,
            "batch_name": a.batch.name if a and a.batch else None,
            "stage_code": s.stage_code, "stage_name": stage_name(db, s.stage_code),
            "status": s.status, "level": LEVEL_BY_STATUS.get(s.status) or s.return_level,
            "round_no": s.round_no, "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "deadline": dl.isoformat() if dl else None, "days_left": days_left,
            "ai_status": s.ai_status, "recommendation": rec,
            "handover_status": report.handover_status if report else None,
            "effective_recommendation": report.effective_recommendation if report else None,
            "issue_counts": counts, "pending_count": pending,
            "needs_judgement": (report.summary or {}).get("needs_judgement") if report else 0,
            "is_demo": a.is_demo if a else False,
        })
    return ok({"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/archives/{aid}/submissions")
def create_submission(aid: int, body: dict | None = None, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    a = ensure_archive_access(db, actor, aid, request)
    if actor.role not in ("STUDENT", "BRANCH_REVIEWER"):
        raise forbidden("仅学生本人或本支部可创建提交包")
    body = body or {}
    try:
        stage = int(body.get("stage_code") or a.current_stage)
    except (TypeError, ValueError):
        raise unprocessable("阶段参数无效")
    if stage < 1 or stage > 5:
        raise unprocessable("阶段参数无效")
    if stage > a.current_stage:
        raise unprocessable("不能创建超过当前发展阶段的提交包")
    existing = db.query(Submission).filter(Submission.archive_id == aid, Submission.stage_code == stage).first()
    if existing:
        raise conflict("该阶段提交包已存在", data={"id": existing.id})
    s = Submission(
        archive_id=aid, stage_code=stage, batch_id=a.batch_id, college_id=a.college_id, branch_id=a.branch_id,
        status="DRAFT", round_no=1, ai_status="NONE", created_at=now(), updated_at=now(),
    )
    db.add(s)
    db.flush()
    return ok(_sub_detail(db, s, actor))


@router.get("/submissions/{sid}")
def get_submission(sid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    return ok(_sub_detail(db, s, actor))


def _sub_detail(db, s: Submission, actor) -> dict:
    a = s.archive
    report = db.query(AiReport).filter(AiReport.id == s.latest_report_id).first() if s.latest_report_id else None
    mats = db.query(Material).filter(Material.submission_id == s.id, Material.status == "ACTIVE").all()
    mlist = []
    for m in mats:
        ver = db.query(MaterialVersion).filter(MaterialVersion.id == m.current_version_id).first() if m.current_version_id else None
        open_n = db.query(func.count(Issue.id)).filter(Issue.material_id == m.id, Issue.is_active.is_(True)).scalar() or 0
        mlist.append({
            "id": m.id, "title": m.title, "type_name": m.type.name if m.type else None,
            "current_version_id": m.current_version_id, "version_no": ver.version_no if ver else None,
            "page_count": ver.page_count if ver else None, "open_issue_count": open_n,
        })
    dl = _deadline_of(s)
    today = now().date()
    from services.workflow import report_is_stale
    stale = report_is_stale(db, s, report) if report else False
    return {
        "id": s.id,
        "archive": {"id": a.id, "real_name": a.real_name, "student_no": a.student_no, "branch_name": a.branch.name if a.branch else None} if a else None,
        "stage_code": s.stage_code, "stage_name": stage_name(db, s.stage_code),
        "status": s.status, "level": LEVEL_BY_STATUS.get(s.status) or s.return_level, "return_level": s.return_level,
        "round_no": s.round_no, "ai_status": s.ai_status, "ai_job_id": s.ai_job_id,
        "latest_report": {
            "id": report.id, "report_no": report.report_no, "recommendation": report.recommendation,
            "handover_status": report.handover_status, "effective_recommendation": report.effective_recommendation,
            "is_stale": stale, "summary": report.summary,
        } if report else None,
        "materials": mlist,
        "completeness": (report.completeness if report else None) or {},
        "can": can_actions(db, s, actor),
        "deadline": dl.isoformat() if dl else None,
        "days_left": (dl - today).days if dl else None,
    }


@router.post("/submissions/{sid}/submit")
def submit(sid: int, body: dict | None = None, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    if actor.role not in ("STUDENT", "BRANCH_REVIEWER"):
        raise forbidden()
    result = submit_package(db, s, actor, (body or {}).get("comment"))
    log(db, actor, "SUBMIT", "submission", sid, {})
    return ok({"submission": _sub_detail(db, result["submission"], actor), "recheck_job_id": result.get("recheck_job_id")})


@router.post("/submissions/{sid}/review")
def review(sid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    result = review_package(
        db, s, actor, body.get("level"), body.get("decision"), body.get("comment"),
        body.get("issue_ids"), body.get("deadline"), False, body.get("report_id"),
    )
    log(db, actor, "REVIEW_PASS" if body.get("decision") == "pass" else "REVIEW_RETURN", "submission", sid, body)
    return ok({
        "submission": _sub_detail(db, result["submission"], actor),
        "review_record_id": result.get("review_record_id"),
        "notice_id": result.get("notice_id"),
    })


@router.post("/submissions/batch-review")
def batch_review(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    raw = body.get("submission_ids")
    if not isinstance(raw, list):
        raise unprocessable("submission_ids 须为提交包编号列表")
    # 逐个规范化（整数字符串也接受），按首次出现的顺序去重，其余记为无效项
    targets: list[tuple[object, int | None]] = []
    seen: set[int] = set()
    for value in raw:
        sid = _normalize_submission_id(value)
        if sid is None:
            targets.append((value, None))
        elif sid not in seen:
            seen.add(sid)
            targets.append((value, sid))
    passed, failed = [], []
    for value, sid in targets:
        if sid is None:
            failed.append({"submission_id": value, "code": 42200, "reason": "提交包编号无效"})
            continue
        try:
            # 每份独立保存点：单份失败只回滚该份的写入
            with db.begin_nested():
                s = ensure_submission_access(db, actor, sid)
                # 与单份通过走同一条路径，ensure_passable() 的阻断口径因此完全一致
                review_package(db, s, actor, body.get("level"), "pass", body.get("comment"), is_batch=True)
            passed.append(sid)
        except AppError as e:
            if e.status_code == 404:
                failed.append({"submission_id": sid, "code": 40400, "reason": "提交包不存在或无权访问"})
            else:
                failed.append({"submission_id": sid, "code": e.biz_code, "reason": e.biz_message})
        except Exception:
            failed.append({"submission_id": sid, "code": 50000, "reason": "审核失败"})
    log(db, actor, "BATCH_REVIEW", "submission", None, {
        "passed": passed,
        "failed": [{"submission_id": f["submission_id"], "code": f["code"]} for f in failed],
    })
    return ok({"passed": passed, "failed": failed})


def _normalize_submission_id(value) -> int | None:
    """整数（布尔值除外）或纯数字字符串转成提交包编号；其他返回 None。"""
    if type(value) is int:
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


@router.post("/submissions/{sid}/filing")
def filing(sid: int, body: dict | None = None, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    result = file_package(db, s, actor, (body or {}).get("comment"))
    log(db, actor, "FILE", "submission", sid, {})
    a = result["archive"]
    return ok({
        "submission": _sub_detail(db, result["submission"], actor),
        "archive": {"id": a.id, "current_stage": a.current_stage, "status": a.status},
        "next_submission_id": result.get("next_submission_id"),
    })


@router.get("/submissions/{sid}/review-records")
def records(sid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    s = ensure_submission_access(db, actor, sid, request)
    rows = db.query(ReviewRecord).filter(ReviewRecord.submission_id == sid).order_by(ReviewRecord.created_at).all()
    out = []
    for r in rows:
        report = db.query(AiReport).filter(AiReport.id == r.report_id).first() if r.report_id else None
        out.append({
            "id": r.id, "level": r.level, "action": r.action, "from_status": r.from_status, "to_status": r.to_status,
            "reviewer_name": r.reviewer_name, "reviewer_role": r.reviewer_role, "comment": r.comment,
            "report_id": r.report_id, "report_no": report.report_no if report else None,
            "issue_ids": r.issue_ids, "round_no": r.round_no, "is_batch": r.is_batch,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return ok(out)
