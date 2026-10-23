"""临时 PostgreSQL schema 与通用造数工具。

文件名不以 test_ 开头，不会被 pytest 收集为用例；由各测试模块显式 import 使用。
数据库用例只读 TEST_DATABASE_URL，每个模块建一个随机 schema，测试在事务里跑完即回滚，
结束后 DROP SCHEMA，从不连接应用库。
"""
from __future__ import annotations

import os
import zipfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from deps import Actor
from models import (
    AiReport,
    Archive,
    Batch,
    BatchUploadItem,
    Issue,
    Job,
    Material,
    MaterialType,
    MaterialVersion,
    Org,
    RuleVersion,
    Submission,
    User,
    UserRole,
)
from utils import now


class SchemaDatabase:
    """独立的随机 schema：建结构 + 写默认规则，用完 DROP。"""

    def __init__(self, url: str, prefix: str):
        self.url = url
        self.name = f"{prefix}_{uuid4().hex[:12]}"
        self._admin = create_engine(url, connect_args={"connect_timeout": 5})
        with self._admin.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{self.name}"'))
        self.engine = create_engine(
            url, connect_args={"connect_timeout": 5, "options": f"-csearch_path={self.name}"}
        )
        try:
            from database import _HANDOVER_PATCH

            raw = self.engine.raw_connection()
            try:
                with raw.cursor() as cur:
                    cur.execute((Path(__file__).parents[1] / "schema.sql").read_text(encoding="utf-8"))
                    cur.execute(_HANDOVER_PATCH)
                raw.commit()
            finally:
                raw.close()
            from seed_rules import seed_rules

            with Session(self.engine) as db:
                seed_rules(db)
                db.commit()
        except Exception:
            self.drop()
            raise

    def drop(self) -> None:
        self.engine.dispose()
        with self._admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{self.name}" CASCADE'))
        self._admin.dispose()


def make_schema_engine(prefix: str = "pytest") -> SchemaDatabase:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL 未设置：数据库用例需要可写的临时 PostgreSQL")
    return SchemaDatabase(url, prefix)


@pytest.fixture(scope="module")
def pg_schema():
    schema = make_schema_engine()
    try:
        yield schema
    finally:
        schema.drop()


@pytest.fixture
def case(pg_schema):
    conn = pg_schema.engine.connect()
    tx = conn.begin()
    db = Session(bind=conn, expire_on_commit=False)
    ctx = build_case(db)
    try:
        yield ctx
    finally:
        db.close()
        if tx.is_active:
            tx.rollback()
        conn.close()


@pytest.fixture
def as_client(case):
    """把依赖覆盖成 case 里的会话/身份，不经过真实登录。"""
    from fastapi.testclient import TestClient

    from database import get_db
    from deps import get_current_user
    from main import app

    def factory(actor):
        app.dependency_overrides[get_db] = lambda: case.db
        app.dependency_overrides[get_current_user] = lambda: actor
        return TestClient(app)

    yield factory
    app.dependency_overrides.clear()


@pytest.fixture
def storage_tmp(tmp_path, monkeypatch):
    """把 storage 根目录指到 tmp_path，测试不碰 backend/storage。"""
    from config import ensure_storage
    from services import storage as store

    monkeypatch.setattr(store, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr("config.STORAGE_DIR", tmp_path)
    ensure_storage()
    return tmp_path


# ---------------------------------------------------------------- 造数


def build_case(db: Session) -> SimpleNamespace:
    """学校—学院—两个支部、两个批次、五类账号、三个档案与六个提交包。"""

    def add(model, **kwargs):
        row = model(**kwargs)
        db.add(row)
        db.flush()
        return row

    school = add(Org, name="学校", org_type="SCHOOL", created_at=now(), updated_at=now())
    college = add(Org, name="学院", org_type="COLLEGE", parent_id=school.id, created_at=now(), updated_at=now())
    branches = [
        add(Org, name=f"支部{i}", org_type="BRANCH", parent_id=college.id, created_at=now(), updated_at=now())
        for i in range(2)
    ]
    today = now().date()
    batches = [
        add(Batch, name=f"批次{i}", year=2026, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            self_deadline=today, branch_deadline=today,
            cross_deadline=today, college_deadline=today, org_deadline=today,
            created_at=now(), updated_at=now())
        for i in range(2)
    ]

    def actor(username, role, org):
        user = add(User, username=username, password_hash="unused", real_name=username, org_id=org.id,
                   is_active=True, must_change_password=False, created_at=now(), updated_at=now())
        grant = add(UserRole, user_id=user.id, role=role, org_id=org.id, created_at=now())
        return Actor(user, role, org.id, [grant], "127.0.0.1", "pytest")

    student_a = actor("student_a", "STUDENT", branches[0])
    student_b = actor("student_b", "STUDENT", branches[0])
    student_c = actor("student_c", "STUDENT", branches[1])
    reviewer = actor("branch_reviewer", "BRANCH_REVIEWER", branches[0])
    cross = actor("cross_reviewer", "CROSS_REVIEWER", branches[1])
    college_admin = actor("college_reviewer", "COLLEGE_REVIEWER", college)
    org_admin = actor("org_admin", "ORG_ADMIN", school)
    sys_admin = actor("sys_admin", "SYS_ADMIN", school)

    rule_version = db.query(RuleVersion).first()

    def archive(student, username, branch, number, stage=2):
        # 学号用 10 位数字：ZIP 识别按 (D\d{7}|\d{10,12}|[A-Z]\d{6,10}) 解析
        return add(Archive, student_user_id=student.id, student_no=f"20260010{number:02d}",
                   real_name=f"学生{username[-1].upper()}", college_id=college.id, branch_id=branch.id,
                   batch_id=batches[0].id, current_stage=stage, status="ACTIVE",
                   anon_code=f"anon-{username}", created_at=now(), updated_at=now())

    def submission(arch, stage, status):
        return add(Submission, archive_id=arch.id, stage_code=stage, batch_id=arch.batch_id,
                   college_id=college.id, branch_id=arch.branch_id, status=status, round_no=1,
                   ai_status="DONE", submitted_at=now(), level_entered_at=now(),
                   created_at=now(), updated_at=now())

    arch_a = archive(student_a, "student_a", branches[0], 1)
    arch_b = archive(student_b, "student_b", branches[0], 2)
    arch_c = archive(student_c, "student_c", branches[1], 3)

    sub_branch = submission(arch_a, 1, "BRANCH_REVIEW")
    sub_draft = submission(arch_a, 2, "DRAFT")
    sub_filing = submission(arch_b, 1, "ORG_FILING")
    sub_draft_b = submission(arch_b, 2, "DRAFT")
    sub_other_branch = submission(arch_c, 1, "BRANCH_REVIEW")
    sub_draft_c = submission(arch_c, 2, "DRAFT")
    for sub in (sub_branch, sub_filing, sub_other_branch):
        add_report(db, sub, rule_version)
    db.flush()

    ctx = SimpleNamespace(
        db=db, add=add, school=school, college=college, branches=branches, batches=batches,
        student=student_a, student_b=student_b, student_c=student_c,
        reviewer=reviewer, cross=cross, college_admin=college_admin, org_admin=org_admin, sys_admin=sys_admin,
        archives=[arch_a, arch_b, arch_c], arch_a=arch_a, arch_b=arch_b, arch_c=arch_c,
        sub_branch=sub_branch, sub_draft=sub_draft, sub_filing=sub_filing,
        sub_draft_b=sub_draft_b, sub_other_branch=sub_other_branch, sub_draft_c=sub_draft_c,
        rule_version=rule_version, today=today,
    )
    return ctx


def add_report(db: Session, sub: Submission, rule_version: RuleVersion | None = None, **kwargs) -> AiReport:
    """给提交包挂一份“有效、未过期、无需人工接管”的最新报告。"""
    rule_version = rule_version or db.query(RuleVersion).first()
    report_no = (db.query(AiReport).filter(AiReport.submission_id == sub.id).count()) + 1
    report = AiReport(
        submission_id=sub.id, report_no=report_no, rule_version_id=rule_version.id,
        trigger_type="REVIEW", mode="RULE_ONLY", status="DONE", material_versions=[],
        recommendation="SUGGEST_PASS", handover_status="NOT_REQUIRED", effective_recommendation=None,
        started_at=now(), finished_at=now(),
    )
    for key, value in kwargs.items():
        setattr(report, key, value)
    db.add(report)
    db.flush()
    sub.latest_report_id = report.id
    db.flush()
    return report


def add_issue(db: Session, sub: Submission, *, severity="BLOCK", review_status="PENDING",
              active=True, source="AI_RULE", **kwargs) -> Issue:
    # ck_issues_manual: (source='MANUAL') = (report_id IS NULL)
    report_id = kwargs.pop("report_id", None)
    if report_id is None and source != "MANUAL":
        report_id = sub.latest_report_id
    issue = Issue(
        submission_id=sub.id, report_id=report_id, source=source, category=kwargs.pop("category", "CONTENT"),
        severity=severity, title=kwargs.pop("title", "问题"), description=kwargs.pop("description", "说明"),
        review_status=review_status, is_active=active, location=kwargs.pop("location", {}),
        created_at=kwargs.pop("created_at", now()), updated_at=kwargs.pop("updated_at", now()),
    )
    for key, value in kwargs.items():
        setattr(issue, key, value)
    db.add(issue)
    db.flush()
    return issue


def add_archive(db: Session, case: SimpleNamespace, *, student_no="2026001999", branch=0,
                batch=0, current_stage=2) -> Archive:
    """新增一个档案（含学生账号），用于需要独立截止日/独立范围的场景。"""
    user = User(username=f"u{student_no}", password_hash="unused", real_name=f"学生{student_no[-3:]}",
                org_id=case.branches[branch].id, is_active=True, must_change_password=False,
                created_at=now(), updated_at=now())
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.id, role="STUDENT", org_id=case.branches[branch].id, created_at=now()))
    db.flush()
    arch = Archive(
        student_user_id=user.id, student_no=student_no, real_name=f"学生{student_no[-3:]}",
        college_id=case.college.id, branch_id=case.branches[branch].id, batch_id=case.batches[batch].id,
        current_stage=current_stage, status="ACTIVE", anon_code=f"anon-{student_no}",
        created_at=now(), updated_at=now(),
    )
    db.add(arch)
    db.flush()
    return arch


def add_submission(db: Session, arch: Archive, stage: int, status: str, *, report=False) -> Submission:
    sub = Submission(
        archive_id=arch.id, stage_code=stage, batch_id=arch.batch_id, college_id=arch.college_id,
        branch_id=arch.branch_id, status=status, round_no=1, ai_status="DONE",
        submitted_at=now(), level_entered_at=now(), created_at=now(), updated_at=now(),
    )
    db.add(sub)
    db.flush()
    if report:
        add_report(db, sub)
    return sub


def add_job(db: Session, *, job_type="BATCH_UPLOAD", status="SUCCEEDED", params=None,
            created_by=None, **kwargs) -> Job:
    job = Job(
        job_type=job_type, status=status, params=params or {}, total=kwargs.pop("total", 1),
        done_count=kwargs.pop("done_count", 1), created_by=created_by, created_at=now(),
        started_at=now(), finished_at=now(), result=kwargs.pop("result", None),
    )
    for key, value in kwargs.items():
        setattr(job, key, value)
    db.add(job)
    db.flush()
    return job


def add_upload_item(db: Session, job: Job, *, entry_path="2026001_申请书.pdf", temp_path=None,
                    status="MATCHED", archive_id=None, material_type_id=None, **kwargs) -> BatchUploadItem:
    item = BatchUploadItem(
        job_id=job.id, entry_path=entry_path, temp_path=temp_path, file_size=kwargs.pop("file_size", 10),
        parsed_student_no=kwargs.pop("parsed_student_no", None), parsed_type_hint=kwargs.pop("parsed_type_hint", None),
        matched_archive_id=archive_id, match_method=kwargs.pop("match_method", "FILENAME"),
        material_type_id=material_type_id, status=status, material_id=kwargs.pop("material_id", None),
        error=kwargs.pop("error", None), created_at=now(), updated_at=now(),
    )
    for key, value in kwargs.items():
        setattr(item, key, value)
    db.add(item)
    db.flush()
    return item


def add_material(db: Session, sub: Submission, *, stage=None, sha="0" * 64, content=b"%PDF-1.4 test",
                 stored_path=None, status="ACTIVE") -> tuple[Material, MaterialVersion]:
    """提交包里已有的一份材料（用于内容查重用例），文件同时落盘。"""
    from services import storage as store

    rel = stored_path
    if rel is None:
        rel, sha_calc, size = store.save_bytes(content, sub.archive_id, "pdf")
        sha = sha_calc
    material = Material(
        archive_id=sub.archive_id, submission_id=sub.id, stage_code=stage or sub.stage_code,
        title="已有材料", status=status, version_count=1, created_at=now(), updated_at=now(),
    )
    db.add(material)
    db.flush()
    version = MaterialVersion(
        material_id=material.id, version_no=1, original_filename="a.pdf", stored_path=rel,
        file_ext="pdf", mime_type="application/pdf", file_size=len(content), sha256=sha,
        parse_status="DONE", uploaded_at=now(),
    )
    db.add(version)
    db.flush()
    material.current_version_id = version.id
    db.flush()
    return material, version


def zip_bytes(entries: dict[str, bytes | str]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content if isinstance(content, bytes) else content.encode("utf-8"))
    return buffer.getvalue()


def pdf_bytes(marker: str = "pdf") -> bytes:
    """内容不同的“PDF”（上传校验只看扩展名与 %PDF 头）。"""
    return b"%PDF-1.4\n" + marker.encode("utf-8") * 8


def scoped_actor(actor: Actor, role: str, org_id: int) -> Actor:
    """同一账号切换激活角色（多角色用户用 X-Active-Role 指定身份的场景）。"""
    return Actor(actor.user, role, org_id, actor.roles, actor.ip, actor.user_agent)
