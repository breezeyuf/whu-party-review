from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from config import DEMO_PASSWORD
from models import (
    Archive,
    Batch,
    CrossReviewPair,
    Material,
    MaterialType,
    MaterialVersion,
    Org,
    ParseResult,
    Submission,
    TimeNodeExtraction,
    User,
    UserRole,
)
from security import hash_password
from services.materials import enqueue_job
from services.timeline import merge_archive_nodes
from utils import now

from services import storage as store


def seed_demo(db: Session, actor, reset: bool = False, run_checks: bool = True) -> dict:
    if reset:
        _purge_demo(db)
    if db.query(User).filter(User.is_demo.is_(True)).first() and not reset:
        return {"message": "演示数据已存在", "accounts": _account_list(db)}
    school = db.query(Org).filter(Org.org_type == "SCHOOL").first()
    if not school:
        school = Org(org_type="SCHOOL", name="演示大学", code="DEMO_UNI", is_demo=True, is_active=True, created_at=now(), updated_at=now())
        db.add(school)
        db.flush()
    colleges = []
    branches = []
    for i, cname in enumerate(["演示学院", "示例学院"], start=1):
        col = Org(parent_id=school.id, org_type="COLLEGE", name=cname, code=f"DEMO_C{i}", is_demo=True, is_active=True, sort_order=i, created_at=now(), updated_at=now())
        db.add(col)
        db.flush()
        colleges.append(col)
        for j in range(1, 4):
            br = Org(parent_id=col.id, org_type="BRANCH", name=f"{cname}第{j}党支部", code=f"DEMO_C{i}B{j}", is_demo=True, is_active=True, sort_order=j, created_at=now(), updated_at=now())
            db.add(br)
            db.flush()
            branches.append(br)
    pwd = DEMO_PASSWORD
    accounts = []

    def add_user(username, name, org, roles):
        u = User(
            username=username, password_hash=hash_password(pwd), real_name=name, org_id=org.id,
            is_active=True, must_change_password=False, is_demo=True, created_at=now(), updated_at=now(),
        )
        db.add(u)
        db.flush()
        for role in roles:
            db.add(UserRole(user_id=u.id, role=role, org_id=org.id, created_at=now()))
        accounts.append({"username": username, "real_name": name, "roles": roles})
        return u

    org_admin = add_user("demo_org", "演示组织部管理员", school, ["ORG_ADMIN"])
    for i, col in enumerate(colleges, start=1):
        add_user(f"demo_college{i}", f"演示学院审核员{i:02d}", col, ["COLLEGE_REVIEWER"])
    branch_users = []
    for i, br in enumerate(branches, start=1):
        bu = add_user(f"demo_branch{i}", f"演示支部书记{i:02d}", br, ["BRANCH_REVIEWER", "CROSS_REVIEWER"])
        branch_users.append(bu)
    batch = Batch(
        name="2026 年度发展批次（演示）", year=2026, term="FULL_YEAR", stage_codes=[1, 2, 3, 4, 5],
        start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
        self_deadline=date(2026, 10, 18), branch_deadline=date(2026, 10, 21),
        cross_deadline=date(2026, 10, 25), college_deadline=date(2026, 10, 28),
        org_deadline=date(2026, 11, 5), status="ACTIVE", is_demo=True, created_by=actor.id,
        created_at=now(), updated_at=now(),
    )
    db.add(batch)
    db.flush()
    # pairs within college
    for col in colleges:
        brs = [b for b in branches if b.parent_id == col.id]
        for i, b in enumerate(brs):
            other = brs[(i + 1) % len(brs)]
            db.add(CrossReviewPair(
                batch_id=batch.id, college_id=col.id, target_branch_id=b.id,
                reviewer_branch_id=other.id, created_by=actor.id, created_at=now(),
            ))
    students = []
    idx = 1
    scenarios = _scenarios()
    for br in branches:
        col = next(c for c in colleges if c.id == br.parent_id)
        for k in range(4):
            sc = scenarios[(idx - 1) % len(scenarios)]
            sno = f"D2023{idx:03d}"
            stu = add_user(f"demo_stu{idx:02d}", f"演示学生{idx:02d}", br, ["STUDENT"])
            arch = Archive(
                student_user_id=stu.id, student_no=sno, real_name=stu.real_name, gender="女" if idx % 2 else "男",
                ethnicity="汉族", birth_date=date(2003, 5, 12), native_place="湖北武汉",
                major="计算机科学与技术", class_name=f"计科 230{k+1}",
                college_id=col.id, branch_id=br.id, batch_id=batch.id,
                current_stage=sc["stage"], status="ACTIVE", profile_extra={},
                anon_code=f"ANON{idx:04d}", data_source="DEMO", is_demo=True,
                created_by=actor.id, created_at=now(), updated_at=now(),
            )
            db.add(arch)
            db.flush()
            students.append((arch, sc))
            idx += 1
    jobs_queued = 0
    type_map = {t.code: t for t in db.query(MaterialType).all()}
    for arch, sc in students:
        for stg in range(1, arch.current_stage + 1):
            status = "FILED" if stg < arch.current_stage else sc["status"]
            sub = Submission(
                archive_id=arch.id, stage_code=stg, batch_id=batch.id, college_id=arch.college_id,
                branch_id=arch.branch_id, status=status, round_no=1, ai_status="NONE",
                submitted_at=now() if status != "DRAFT" else None,
                level_entered_at=now() if status not in ("DRAFT",) else None,
                filed_at=now() if status == "FILED" else None,
                created_at=now(), updated_at=now(),
            )
            if status == "RETURNED":
                sub.return_level = "BRANCH"
            db.add(sub)
            db.flush()
            if stg != arch.current_stage:
                continue
            for mat in sc["materials"]:
                jobs_queued += _add_demo_material(db, arch, sub, type_map, mat, actor)
            for code, val in sc.get("nodes", {}).items():
                d = as_date_safe(val)
                if d:
                    db.add(TimeNodeExtraction(
                        archive_id=arch.id, node_code=code, value_date=d, method="IMPORT",
                        is_current=True, created_at=now(),
                    ))
            merge_archive_nodes(db, arch.id)
            if run_checks and status != "DRAFT":
                job = enqueue_job(db, "AI_CHECK", actor.id, "submission", sub.id,
                                  {"submission_id": sub.id, "trigger_type": "REVIEW"})
                sub.ai_status = "QUEUED"
                sub.ai_job_id = job.id
                jobs_queued += 1
    db.flush()
    return {
        "orgs": 1 + len(colleges) + len(branches),
        "users": db.query(User).filter(User.is_demo.is_(True)).count(),
        "archives": len(students),
        "submissions": db.query(Submission).join(Archive).filter(Archive.is_demo.is_(True)).count(),
        "materials": db.query(Material).join(Archive, Archive.id == Material.archive_id).filter(Archive.is_demo.is_(True)).count(),
        "jobs_queued": jobs_queued,
        "accounts": accounts,
    }


def _account_list(db) -> list:
    rows = db.query(User).filter(User.is_demo.is_(True)).all()
    out = []
    for u in rows:
        out.append({"username": u.username, "real_name": u.real_name, "roles": [r.role for r in u.roles]})
    return out


def as_date_safe(v):
    from utils import as_date
    return as_date(v)


def _add_demo_material(db, arch, sub, type_map, spec, actor) -> int:
    code = spec["type"]
    mt = type_map.get(code)
    text = spec["text"]
    rel = _write_pdf(arch.id, f"{code}_{arch.student_no}", text, seal=spec.get("seal"), sign=spec.get("sign", True))
    mat = Material(
        archive_id=arch.id, submission_id=sub.id, stage_code=sub.stage_code,
        title=spec.get("title") or (mt.name if mt else code),
        declared_type_id=mt.id if mt else None, type_id=mt.id if mt else None,
        type_source="DECLARED", type_confidence=1.0, type_status="AUTO",
        version_count=1, status="ACTIVE", uploaded_by=actor.id, created_at=now(), updated_at=now(),
    )
    db.add(mat)
    db.flush()
    data = store.read_bytes(rel)
    import hashlib
    ver = MaterialVersion(
        material_id=mat.id, version_no=1, original_filename=f"{mat.title}.pdf", stored_path=rel,
        file_ext="pdf", mime_type="application/pdf", file_size=len(data),
        sha256=hashlib.sha256(data).hexdigest(), parse_status="PENDING",
        uploaded_by=actor.id, uploaded_at=now(),
    )
    db.add(ver)
    db.flush()
    mat.current_version_id = ver.id
    enqueue_job(db, "PARSE", actor.id, "material_version", ver.id, {"version_id": ver.id})
    return 1


def _write_pdf(archive_id: int, stem: str, text: str, seal=False, sign=True) -> str:
    import fitz
    from services.storage import abs_path
    from config import STORAGE_DIR
    rel = f"materials/{archive_id}/{uuid.uuid4().hex}.pdf"
    path = abs_path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    html = "<div style='font-size:12pt;line-height:1.7'>"
    for line in text.split("\n"):
        esc = line.replace("&", "&amp;").replace("<", "&lt;")
        html += f"<p>{esc or '&nbsp;'}</p>"
    html += "</div>"
    page.insert_htmlbox(page.rect + (48, 48, -48, -80), html)
    if seal:
        r = fitz.Rect(420, 680, 520, 780)
        page.draw_oval(r, color=(0.8, 0.1, 0.1), width=2)
        page.insert_textbox(r, "党支部\n印章", fontsize=9, color=(0.8, 0.1, 0.1), align=1)
    if sign:
        page.insert_text((400, 800), "签名：演示", fontsize=11)
    doc.save(path)
    doc.close()
    return rel


def _scenarios():
    app = (
        "入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、"
        "“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心全意为人民服务的宗旨。"
        "我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日"
    )
    bad_motive = app.replace("为了更好地为人民服务", "入党可以评优评奖，也为了好找工作")
    thought_ok = "思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n{date}"
    auto_ok = (
        "自传\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从小学起接受集体主义教育。"
        "思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，全心全意为人民服务。\n" + ("认识深化。" * 80)
    )
    auto_miss = "自传\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\n签名"
    return [
        {"stage": 3, "status": "BRANCH_REVIEW", "nodes": {"T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T08": "2025-08-30"},
         "materials": [
             {"type": "APPLICATION_LETTER", "text": app, "sign": True},
             {"type": "THOUGHT_REPORT", "text": thought_ok.format(date="2024年12月20日")},
             {"type": "THOUGHT_REPORT", "text": thought_ok.format(date="2025年3月25日")},
             {"type": "THOUGHT_REPORT", "text": thought_ok.format(date="2025年7月1日")},
             {"type": "CANDIDATE_MEETING_RECORD", "text": "支委会确定发展对象记录\n经讨论，确定该同志为发展对象。\n2025年8月30日", "seal": True},
             {"type": "AUTOBIOGRAPHY", "text": auto_ok},
         ]},
        {"stage": 3, "status": "RETURNED", "nodes": {"T01": "2003-05-12", "T02": "2023-03-15", "T04": "2024-09-10", "T08": "2025-08-30"},
         "materials": [
             {"type": "APPLICATION_LETTER", "text": bad_motive},
             {"type": "AUTOBIOGRAPHY", "text": auto_miss},
             {"type": "THOUGHT_REPORT", "text": thought_ok.format(date="2025年8月1日")},
         ]},
        {"stage": 2, "status": "DRAFT", "nodes": {"T02": "2023-03-15", "T04": "2024-09-10"},
         "materials": [{"type": "APPLICATION_LETTER", "text": app}]},
        {"stage": 4, "status": "COLLEGE_REVIEW", "nodes": {"T02": "2022-03-15", "T04": "2023-04-01", "T08": "2024-05-01", "T14": "2025-06-01"},
         "materials": [
             {"type": "APPLICATION_FORM", "text": "入党志愿书\n姓名 演示学生 出生日期 2003年5月12日\n2025年5月20日", "sign": True, "seal": True},
             {"type": "ADMISSION_MEETING_RECORD", "text": "支部大会讨论接收预备党员记录\n2025年6月1日", "seal": True},
             {"type": "POLITICAL_REVIEW", "text": "政治审查材料\n政审合格。\n2024年6月1日", "seal": True},
             {"type": "TRAINING_CERT", "text": "集中培训结业证书\n培训时间 2024年7月1日至2024年7月5日，学时 24。", "seal": True},
             {"type": "CANDIDATE_PUBLICITY", "text": "发展对象公示材料\n公示自 2025年4月20 日至 2025年4月26 日。", "seal": True},
             {"type": "PRE_REVIEW_OPINION", "text": "上级党委预审意见\n同意。\n2025年5月10日", "seal": True},
         ]},
        {"stage": 5, "status": "ORG_FILING", "nodes": {"T14": "2024-10-01", "T16": "2024-10-20", "T18": "2025-09-20", "T20": "2025-10-08"},
         "materials": [
             {"type": "REGULARIZATION_LETTER", "text": "转正申请书\n敬爱的党组织：\n我志愿按期转正。\n此致\n敬礼！\n2025年9月20日", "sign": True},
             {"type": "REGULARIZATION_MEETING_RECORD", "text": "支部大会讨论转正记录\n2025年10月8日", "seal": True},
             {"type": "REGULARIZATION_PUBLICITY", "text": "转正公示材料\n公示 2025年9月25 日至 2025年10月8 日。", "seal": True},
         ]},
        {"stage": 1, "status": "FILED", "nodes": {"T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-28"},
         "materials": [
             {"type": "APPLICATION_LETTER", "text": app, "sign": True},
             {"type": "PARTY_TALK_RECORD", "text": "党组织派人谈话记录\n谈话人已谈话。\n2023年3月28日", "sign": True, "seal": True},
         ]},
    ]


def _purge_demo(db: Session) -> None:
    db.execute(text("SET LOCAL app.allow_purge = 'on'"))
    from models import Archive as A
    ids = [x[0] for x in db.query(A.id).filter(A.is_demo.is_(True)).all()]
    if ids:
        db.query(Submission).filter(Submission.archive_id.in_(ids)).delete(synchronize_session=False)
        db.query(A).filter(A.id.in_(ids)).delete(synchronize_session=False)
    db.query(UserRole).filter(UserRole.user_id.in_(db.query(User.id).filter(User.is_demo.is_(True)))).delete(synchronize_session=False)
    db.query(User).filter(User.is_demo.is_(True), User.username != "admin").delete(synchronize_session=False)
    db.query(CrossReviewPair).filter(CrossReviewPair.batch_id.in_(db.query(Batch.id).filter(Batch.is_demo.is_(True)))).delete(synchronize_session=False)
    db.query(Batch).filter(Batch.is_demo.is_(True)).delete(synchronize_session=False)
    db.query(Org).filter(Org.is_demo.is_(True), Org.org_type == "BRANCH").delete(synchronize_session=False)
    db.query(Org).filter(Org.is_demo.is_(True), Org.org_type == "COLLEGE").delete(synchronize_session=False)
    db.flush()
