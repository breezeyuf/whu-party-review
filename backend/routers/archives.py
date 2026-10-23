from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, not_found, unprocessable
from models import (
    AiReport,
    Archive,
    Batch,
    Issue,
    Material,
    Notice,
    Org,
    ReviewRecord,
    Submission,
    TimeNodeExtraction,
    User,
    UserRole,
)
from schemas.common import ok, page_params
from security import encrypt_field, hash_password, mask_id_card, mask_phone, random_password
from services.audit import log
from services.scope import ensure_archive_access, scoped_archives
from services.timeline import correct_node, timeline_view
from utils import now, stage_name, as_date

router = APIRouter(tags=["archives"])


def _archive_brief(db, a: Archive) -> dict:
    sub = db.query(Submission).filter(Submission.archive_id == a.id, Submission.stage_code == a.current_stage).first()
    report = db.query(AiReport).filter(AiReport.id == sub.latest_report_id).first() if sub and sub.latest_report_id else None
    counts = {"BLOCK": 0, "WARN": 0, "INFO": 0}
    if sub:
        for sev, n in db.query(Issue.severity, func.count(Issue.id)).filter(Issue.submission_id == sub.id, Issue.is_active.is_(True)).group_by(Issue.severity):
            counts[sev] = n
    college = a.college
    branch = a.branch
    batch = a.batch
    return {
        "id": a.id, "student_no": a.student_no, "real_name": a.real_name,
        "college_name": college.name if college else None, "branch_id": a.branch_id,
        "branch_name": branch.name if branch else None, "batch_id": a.batch_id,
        "batch_name": batch.name if batch else None, "current_stage": a.current_stage,
        "stage_name": stage_name(db, a.current_stage), "status": a.status, "is_demo": a.is_demo,
        "submission": {
            "id": sub.id, "status": sub.status, "round_no": sub.round_no, "ai_status": sub.ai_status,
            "recommendation": report.effective_recommendation or report.recommendation if report else None,
            "issue_counts": counts, "days_left": None,
        } if sub else None,
    }


def _archive_detail(db, a: Archive) -> dict:
    subs = db.query(Submission).filter(Submission.archive_id == a.id).order_by(Submission.stage_code).all()
    return {
        "id": a.id, "student_user_id": a.student_user_id, "student_no": a.student_no, "real_name": a.real_name,
        "gender": a.gender, "ethnicity": a.ethnicity,
        "birth_date": a.birth_date.isoformat() if a.birth_date else None,
        "native_place": a.native_place, "id_card_masked": a.id_card_masked, "phone_masked": a.student.phone_masked if a.student else None,
        "major": a.major, "class_name": a.class_name, "college_id": a.college_id, "branch_id": a.branch_id,
        "college_name": a.college.name if a.college else None, "branch_name": a.branch.name if a.branch else None,
        "batch_id": a.batch_id, "batch_name": a.batch.name if a.batch else None,
        "current_stage": a.current_stage, "stage_name": stage_name(db, a.current_stage),
        "status": a.status, "profile_extra": a.profile_extra, "anon_code": a.anon_code,
        "data_source": a.data_source, "is_demo": a.is_demo,
        "submissions": [{"id": s.id, "stage_code": s.stage_code, "status": s.status, "round_no": s.round_no, "latest_report_id": s.latest_report_id} for s in subs],
    }


@router.get("/archives")
def list_archives(
    batch_id: int | None = None, college_id: int | None = None, branch_id: int | None = None,
    stage_code: int | None = None, status: str | None = None, submission_status: str | None = None,
    q: str | None = None, has_block: bool | None = None, is_demo: bool | None = None,
    page: int = 1, page_size: int = 20, sort: str | None = None,
    db: Session = Depends(get_db), actor: Actor = Depends(get_current_user),
):
    if actor.role == "STUDENT":
        raise forbidden()
    query = scoped_archives(db.query(Archive).options(selectinload(Archive.college), selectinload(Archive.branch), selectinload(Archive.batch)), actor, db)
    if batch_id:
        query = query.filter(Archive.batch_id == batch_id)
    if college_id:
        query = query.filter(Archive.college_id == college_id)
    if branch_id:
        query = query.filter(Archive.branch_id == branch_id)
    if stage_code:
        query = query.filter(Archive.current_stage == stage_code)
    if status:
        query = query.filter(Archive.status == status)
    if is_demo is not None:
        query = query.filter(Archive.is_demo.is_(is_demo))
    if q:
        like = f"%{q}%"
        query = query.filter((Archive.real_name.ilike(like)) | (Archive.student_no.ilike(like)))
    if submission_status:
        query = query.join(Submission, (Submission.archive_id == Archive.id) & (Submission.stage_code == Archive.current_stage)).filter(Submission.status == submission_status)
    page, page_size = page_params(page, page_size)
    total = query.count()
    rows = query.order_by(Archive.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ok({"items": [_archive_brief(db, a) for a in rows], "total": total, "page": page, "page_size": page_size})


@router.post("/archives")
def create_archive(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    stu = body.get("student") or {}
    if not stu.get("student_no") or not stu.get("real_name"):
        raise unprocessable("缺少学生学号或姓名")
    branch = db.query(Org).filter(Org.id == body.get("branch_id")).first()
    if not branch or branch.org_type != "BRANCH":
        raise unprocessable("支部无效")
    if actor.role == "BRANCH_REVIEWER" and branch.id != actor.org_id:
        raise forbidden()
    if actor.role == "COLLEGE_REVIEWER" and branch.parent_id != actor.org_id:
        raise forbidden("仅可为本学院下属支部建档案")
    college = db.query(Org).filter(Org.id == branch.parent_id).first()
    username = stu.get("username") or stu.get("student_no")
    user = db.query(User).filter(User.username == username).first() if username else None
    initial = None
    if not user:
        pwd = random_password()
        user = User(
            username=username, password_hash=hash_password(pwd), real_name=stu["real_name"],
            gender=stu.get("gender"), org_id=branch.id, phone_enc=encrypt_field(stu.get("phone")),
            phone_masked=mask_phone(stu.get("phone")), must_change_password=True,
            created_at=now(), updated_at=now(),
        )
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role="STUDENT", org_id=branch.id, created_at=now()))
        initial = pwd
    if db.query(Archive).filter(Archive.student_user_id == user.id).first():
        raise conflict("该学生已有档案")
    try:
        stage = int(body.get("current_stage") or 1)
    except (TypeError, ValueError):
        raise unprocessable("阶段参数无效")
    if stage < 1 or stage > 5:
        raise unprocessable("阶段参数无效")
    arch = Archive(
        student_user_id=user.id, student_no=stu["student_no"], real_name=stu["real_name"],
        gender=stu.get("gender"), ethnicity=stu.get("ethnicity"), birth_date=as_date(stu.get("birth_date")),
        native_place=stu.get("native_place"), id_card_enc=encrypt_field(stu.get("id_card")),
        id_card_masked=mask_id_card(stu.get("id_card")), major=stu.get("major"), class_name=stu.get("class_name"),
        college_id=college.id if college else branch.id, branch_id=branch.id, batch_id=body.get("batch_id"),
        current_stage=stage, status="ACTIVE", anon_code=f"A{stu['student_no']}", data_source="MANUAL",
        created_by=actor.id, created_at=now(), updated_at=now(),
    )
    db.add(arch)
    db.flush()
    db.add(Submission(
        archive_id=arch.id, stage_code=stage, batch_id=arch.batch_id, college_id=arch.college_id,
        branch_id=arch.branch_id, status="DRAFT", round_no=1, ai_status="NONE", created_at=now(), updated_at=now(),
    ))
    for code, val in (body.get("initial_nodes") or {}).items():
        if isinstance(val, dict):
            d, end, hours = as_date(val.get("date")), as_date(val.get("end_date")), val.get("hours")
        else:
            d, end, hours = as_date(val), None, None
        if d:
            db.add(TimeNodeExtraction(
                archive_id=arch.id, node_code=code, value_date=d, value_end_date=end, hours=hours,
                method="IMPORT", is_current=True, created_at=now(),
            ))
    from services.timeline import merge_archive_nodes, lock_stage_nodes
    merge_archive_nodes(db, arch.id)
    for s in range(1, stage):
        lock_stage_nodes(db, arch, s)
    log(db, actor, "ARCHIVE_CREATE", "archive", arch.id, {"student_no": arch.student_no})
    db.refresh(arch)
    data = {"archive": _archive_detail(db, arch)}
    if initial:
        data["initial_password"] = initial
    return ok(data)


@router.get("/archives/{aid}")
def get_archive(aid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    a = ensure_archive_access(db, actor, aid, request)
    return ok(_archive_detail(db, a))


@router.put("/archives/{aid}")
def update_archive(aid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    a = ensure_archive_access(db, actor, aid, request)
    for k in ("real_name", "gender", "ethnicity", "native_place", "major", "class_name", "status", "profile_extra"):
        if k in body and body[k] is not None:
            setattr(a, k, body[k])
    if "birth_date" in body:
        a.birth_date = as_date(body.get("birth_date"))
    if "id_card" in body:
        a.id_card_enc = encrypt_field(body.get("id_card"))
        a.id_card_masked = mask_id_card(body.get("id_card"))
    if "branch_id" in body and body["branch_id"]:
        try:
            new_bid = int(body["branch_id"])
        except (TypeError, ValueError):
            raise unprocessable("支部参数无效")
        if new_bid != a.branch_id:
            new_branch = db.query(Org).filter(Org.id == new_bid, Org.org_type == "BRANCH").first()
            if not new_branch:
                raise unprocessable("支部无效")
            if actor.role == "BRANCH_REVIEWER" and new_branch.id != actor.org_id:
                raise forbidden("无权调整所属支部")
            if actor.role == "COLLEGE_REVIEWER" and new_branch.parent_id != actor.org_id:
                raise forbidden("无权调整所属支部")
            a.branch_id = new_branch.id
            if new_branch.parent_id:
                a.college_id = new_branch.parent_id
            # 未归档提交包同步归属，保证审核作用域与档案一致
            db.query(Submission).filter(Submission.archive_id == a.id, Submission.status != "FILED").update(
                {"branch_id": a.branch_id, "college_id": a.college_id}, synchronize_session=False
            )
    if "batch_id" in body:
        a.batch_id = body["batch_id"]
    a.updated_at = now()
    # Basic profile data is input to identity and cross-material checks.
    a.timeline_updated_at = now()
    safe_detail = dict(body)
    if "id_card" in safe_detail:
        safe_detail["id_card"] = mask_id_card(safe_detail.get("id_card"))
    log(db, actor, "ARCHIVE_UPDATE", "archive", aid, safe_detail)
    return ok(_archive_detail(db, a))


@router.get("/archives/{aid}/timeline")
def get_timeline(aid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    a = ensure_archive_access(db, actor, aid, request)
    return ok(timeline_view(db, a))


@router.put("/archives/{aid}/timeline/{node_code}")
def put_node(aid: int, node_code: str, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    a = ensure_archive_access(db, actor, aid, request)
    n = correct_node(db, a, node_code, body, actor)
    log(db, actor, "NODE_CORRECTION", "archive", aid, {"node": node_code})
    from services.timeline import effective_node
    return ok({"code": n.node_code, "effective": effective_node(n), "locked": n.locked, "has_conflict": n.has_conflict})


@router.get("/archives/{aid}/history")
def history(aid: int, stage_code: int | None = None, request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    a = ensure_archive_access(db, actor, aid, request)
    items = []
    mats = db.query(Material).filter(Material.archive_id == aid)
    if stage_code:
        mats = mats.filter(Material.stage_code == stage_code)
    for m in mats.all():
        items.append({"time": m.created_at.isoformat() if m.created_at else None, "kind": "UPLOAD", "stage_code": m.stage_code,
                      "title": f"上传 {m.title}", "detail": None, "actor_name": None, "link_type": "material", "link_id": m.id})
    recs = db.query(ReviewRecord).join(Submission).filter(Submission.archive_id == aid)
    if stage_code:
        recs = recs.filter(Submission.stage_code == stage_code)
    for r in recs.all():
        items.append({"time": r.created_at.isoformat(), "kind": "REVIEW", "stage_code": None, "title": r.action,
                      "detail": r.comment, "actor_name": r.reviewer_name, "link_type": "submission", "link_id": r.submission_id})
    notices = db.query(Notice).filter(Notice.archive_id == aid)
    for n in notices.all():
        items.append({"time": n.created_at.isoformat(), "kind": "NOTICE", "stage_code": None, "title": n.title,
                      "detail": None, "actor_name": None, "link_type": "notice", "link_id": n.id})
    items.sort(key=lambda x: x["time"] or "", reverse=True)
    return ok(items)


@router.get("/my/archive")
def my_archive(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    a = db.query(Archive).filter(Archive.student_user_id == actor.id).first()
    if not a:
        raise not_found("暂无发展档案")
    data = _archive_detail(db, a)
    sub = db.query(Submission).filter(Submission.archive_id == a.id, Submission.stage_code == a.current_stage).first()
    open_n = 0
    next_action = "请上传材料"
    if sub:
        open_n = db.query(func.count(Issue.id)).filter(Issue.submission_id == sub.id, Issue.is_active.is_(True)).scalar() or 0
        if sub.status == "RETURNED":
            next_action = "请处理整改问题后重新提交"
        elif sub.ai_status in ("NONE", "FAILED"):
            next_action = "请发起 AI 自查"
        elif sub.status == "DRAFT" and sub.ai_status == "DONE":
            next_action = "请提交党支部审核"
        elif sub.status not in ("DRAFT", "RETURNED"):
            next_action = "等待审核"
    data["current_submission"] = {
        "id": sub.id if sub else None, "status": sub.status if sub else None, "round_no": sub.round_no if sub else None,
        "ai_status": sub.ai_status if sub else None, "open_issue_count": open_n, "next_action": next_action,
    }
    return ok(data)
