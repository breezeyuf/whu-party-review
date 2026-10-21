"""Business regressions against a disposable PostgreSQL schema.

Set TEST_DATABASE_URL explicitly. The configured application database is never
used implicitly; every run creates and drops only its own random test schema.
"""
from datetime import date, timedelta
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from deps import Actor, _pick_role, get_current_user, require_roles
from errors import AppError
from models import (AiReport, Archive, Batch, CrossReviewPair, Issue, Job, Material,
                    MaterialVersion, Org, ParseResult, RuleVersion, Submission, TimeNodeExtraction, User, UserRole)
from services.scope import can_review, scoped_archives, scoped_submissions
from services.workflow import report_is_stale, review_package, file_package
from utils import now


@pytest.fixture(scope="module")
def test_engine():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for isolated PostgreSQL regressions")
    schema = "review_test_" + uuid4().hex
    admin = create_engine(url, connect_args={"connect_timeout": 5})
    with admin.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"connect_timeout": 5, "options": f"-csearch_path={schema}"})
    try:
        from database import _HANDOVER_PATCH
        raw = engine.raw_connection()
        try:
            with raw.cursor() as cur:
                cur.execute((Path(__file__).parents[1] / "schema.sql").read_text(encoding="utf-8"))
                cur.execute(_HANDOVER_PATCH)
            raw.commit()
        finally:
            raw.close()
        from seed_rules import seed_rules
        with Session(engine) as db:
            seed_rules(db)
            db.commit()
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def case(test_engine):
    conn = test_engine.connect()
    tx = conn.begin()
    db = Session(bind=conn, expire_on_commit=False)

    def add(model, **kwargs):
        row = model(**kwargs)
        db.add(row)
        db.flush()
        return row

    school = add(Org, name="学校", org_type="SCHOOL", created_at=now(), updated_at=now())
    college = add(Org, name="学院", org_type="COLLEGE", parent_id=school.id, created_at=now(), updated_at=now())
    branches = [add(Org, name=f"支部{i}", org_type="BRANCH", parent_id=college.id,
                    created_at=now(), updated_at=now()) for i in range(2)]
    batches = [add(Batch, name=f"批次{i}", year=2026, start_date=date(2026, 1, 1),
                   end_date=date(2026, 12, 31), created_at=now(), updated_at=now()) for i in range(2)]

    def actor(name, role, org):
        user = add(User, username=name, password_hash="unused", real_name=name, org_id=org.id,
                   is_active=True, must_change_password=False, created_at=now(), updated_at=now())
        grant = add(UserRole, user_id=user.id, role=role, org_id=org.id, created_at=now())
        return Actor(user, role, org.id, [grant], "127.0.0.1", "pytest")

    student = actor("student", "STUDENT", branches[0])
    reviewer = actor("branch", "BRANCH_REVIEWER", branches[0])
    cross = actor("cross", "CROSS_REVIEWER", branches[1])
    col = actor("college", "COLLEGE_REVIEWER", college)
    org = actor("org", "ORG_ADMIN", school)
    arch = add(Archive, student_user_id=student.id, student_no="2026001", real_name="学生",
               college_id=college.id, branch_id=branches[0].id, batch_id=batches[0].id,
               current_stage=1, status="ACTIVE", anon_code="test-2026001", created_at=now(), updated_at=now())
    sub = add(Submission, archive_id=arch.id, stage_code=1, batch_id=batches[0].id,
              college_id=college.id, branch_id=branches[0].id, status="BRANCH_REVIEW",
              ai_status="DONE", created_at=now(), updated_at=now())
    rv = db.query(RuleVersion).first()
    report = add(AiReport, submission_id=sub.id, report_no=1, rule_version_id=rv.id,
                 trigger_type="REVIEW", mode="RULE_ONLY", status="DONE", started_at=now(),
                 finished_at=now(), recommendation="SUGGEST_PASS", handover_status="REQUIRED",
                 handover_reasons=["KEY_STAGE"], material_versions=[])
    sub.latest_report_id = report.id
    db.flush()
    ctx = SimpleNamespace(**locals())
    try:
        yield ctx
    finally:
        db.close()
        if tx.is_active:
            tx.rollback()
        conn.close()


@pytest.fixture
def as_client(case):
    from database import get_db
    from main import app
    def factory(actor):
        app.dependency_overrides[get_db] = lambda: case.db
        app.dependency_overrides[get_current_user] = lambda: actor
        return TestClient(app)
    yield factory
    app.dependency_overrides.clear()


def material(c):
    m = c.add(Material, archive_id=c.arch.id, submission_id=c.sub.id, stage_code=1,
              title="材料", status="ACTIVE", created_at=now(), updated_at=now())
    v = c.add(MaterialVersion, material_id=m.id, version_no=1, original_filename="a.pdf",
              stored_path=uuid4().hex + ".pdf", file_ext="pdf", mime_type="application/pdf",
              file_size=10, sha256="0" * 64, parse_status="DONE", uploaded_at=now())
    m.current_version_id = v.id
    c.db.flush()
    return m, v


def pair(c, batch=0, user=None):
    return c.add(CrossReviewPair, batch_id=c.batches[batch].id, college_id=c.college.id,
                 target_branch_id=c.branches[0].id, reviewer_branch_id=c.branches[1].id,
                 reviewer_user_id=user, created_at=now())


def test_cross_scope_requires_matching_batch(case):
    c = case
    pair(c, batch=1)
    assert scoped_submissions(c.db.query(Submission), c.cross, c.db).count() == 0
    assert scoped_archives(c.db.query(Archive), c.cross, c.db).count() == 0
    pair(c)
    assert scoped_submissions(c.db.query(Submission), c.cross, c.db).one().id == c.sub.id
    assert scoped_archives(c.db.query(Archive), c.cross, c.db).one().id == c.arch.id


def test_cross_scope_requires_assignee(case):
    c = case
    pair(c, user=c.reviewer.id)
    c.sub.status = "CROSS_REVIEW"
    assert not can_review(c.sub, c.cross, c.db)
    assert scoped_submissions(c.db.query(Submission), c.cross, c.db).count() == 0


def test_cross_pair_api_rejects_assigning_one_reviewer_to_multiple_branches(case, as_client):
    c = case
    response = as_client(c.org).put(f"/api/batches/{c.batches[0].id}/cross-review-pairs", json={
        "college_id": c.college.id,
        "pairs": [
            {"target_branch_id": c.branches[0].id, "reviewer_branch_id": c.branches[1].id, "reviewer_user_id": c.cross.id},
            {"target_branch_id": c.branches[1].id, "reviewer_branch_id": c.branches[0].id, "reviewer_user_id": c.cross.id},
        ],
    })
    assert response.status_code == 422
    assert "不能分配给多个支部" in response.json()["detail"]["message"]


def test_role_header_must_be_explicit_and_valid(case):
    with pytest.raises(AppError):
        _pick_role(case.student.roles, "ORG_ADMIN")
    assert _pick_role(case.student.roles, f"STUDENT@{case.student.org_id}")[0] == "STUDENT"


def test_role_dependency_does_not_switch_roles(case):
    c = case
    c.student.roles.append(SimpleNamespace(role="ORG_ADMIN", org_id=c.school.id))
    with pytest.raises(AppError):
        require_roles("ORG_ADMIN")(c.student)
    assert c.student.role == "STUDENT"


def test_removed_material_invalidates_report(case):
    c = case
    m, v = material(c)
    c.report.material_versions = [{"material_id": m.id, "version_id": v.id}]
    c.report.finished_at = now() + timedelta(seconds=1)
    assert not report_is_stale(c.db, c.sub, c.report)
    m.status = "DELETED"
    c.db.flush()
    assert report_is_stale(c.db, c.sub, c.report)


def test_timeline_updates_during_parsing_are_included(case):
    c = case
    c.arch.timeline_updated_at = c.report.started_at + timedelta(seconds=1)
    c.report.finished_at = c.report.started_at + timedelta(seconds=2)
    assert not report_is_stale(c.db, c.sub, c.report)
    c.arch.timeline_updated_at = c.report.finished_at + timedelta(seconds=1)
    assert report_is_stale(c.db, c.sub, c.report)


def test_formal_review_reads_published_snapshot_and_persists_context(case, as_client):
    """Real PostgreSQL coverage, enabled with the existing TEST_DATABASE_URL fixture."""
    from copy import deepcopy
    from ai.pipeline import run_check
    from models import ChecklistItem
    from seed_rules import snapshot_rules

    c = case
    item = c.db.query(ChecklistItem).filter(ChecklistItem.stage_code == 1, ChecklistItem.is_active.is_(True)).first()
    m, _ = material(c)
    m.type_id, m.type_status = item.material_type_id, "CONFIRMED"
    item.quantity_mode, item.fixed_count = "FIXED", 1
    c.db.flush()
    old = snapshot_rules(c.db, "checklists", "UPDATE", "测试 V1：一份")
    item.fixed_count = 2
    c.db.flush()
    new = snapshot_rules(c.db, "checklists", "UPDATE", "测试 V2：两份")
    old_snapshot = deepcopy(old.snapshot)
    first = run_check(c.db, c.sub.id, use_llm=False, rule_version_id=old.id)
    second = run_check(c.db, c.sub.id, use_llm=False)
    c.db.expire(first)
    c.db.expire(second)
    find = lambda report: next(i for i in report.completeness["items"] if i["checklist_item_id"] == item.id)
    assert find(first)["expected"] == 1 and find(second)["expected"] == 2
    assert first.rule_version_id == old.id and second.rule_version_id == new.id
    assert old.snapshot == old_snapshot
    assert len(first.timeline_snapshot["evaluation_context"]["snapshot_sha256"]) == 64
    assert "node_inputs" in first.timeline_snapshot
    client = as_client(c.student)
    # The fixture's historical report lacks evaluation_context, but remains readable.
    for report in (c.report, first, second):
        response = client.get(f"/api/reports/{report.id}")
        assert response.status_code == 200
        assert response.json()["data"]["timeline_snapshot"] == report.timeline_snapshot


@pytest.mark.parametrize("ai_status", ["QUEUED", "RUNNING", "FAILED"])
def test_pending_or_failed_check_blocks_pass(case, ai_status):
    c = case
    c.sub.ai_status = ai_status
    c.report.handover_status = "DONE"
    c.db.flush()
    with pytest.raises(AppError, match="409"):
        review_package(c.db, c.sub, c.reviewer, "BRANCH", "pass")
    assert c.sub.status == "BRANCH_REVIEW"


def test_reject_unknown_review_decision(case):
    with pytest.raises(AppError) as exc:
        review_package(case.db, case.sub, case.reviewer, "BRANCH", "typo", comment="x")
    assert exc.value.status_code == 422


def test_reject_unrelated_report_and_issue_ids(case):
    c = case
    with pytest.raises(AppError):
        review_package(c.db, c.sub, c.reviewer, "BRANCH", "return", report_id=c.report.id + 1000, comment="退回")
    with pytest.raises(AppError):
        review_package(c.db, c.sub, c.reviewer, "BRANCH", "return", issue_ids=[999999], comment="退回")


def test_handover_rejects_other_level_and_empty_reason(case, as_client):
    c = case
    body = {"human_decision": "CONFIRM", "handover_reason": "已核查材料"}
    assert as_client(c.col).post(f"/api/reports/{c.report.id}/handover", json=body).status_code == 403
    body["handover_reason"] = ""
    assert as_client(c.reviewer).post(f"/api/reports/{c.report.id}/handover", json=body).status_code == 422
    assert c.report.handover_status == "REQUIRED"


def test_handover_validates_ids_and_updates_actions(case, as_client):
    c = case
    client = as_client(c.reviewer)
    bad = client.post(f"/api/reports/{c.report.id}/handover", json={
        "human_decision": "OVERRIDE_PASS", "handover_reason": "已逐项核实相关材料及原始记录", "issue_ids": [999999]})
    assert bad.status_code == 422
    response = client.post(f"/api/reports/{c.report.id}/handover", json={
        "human_decision": "CONFIRM", "handover_reason": "已核查原始材料和时间节点"})
    assert response.status_code == 200, response.text
    assert not client.get(f"/api/submissions/{c.sub.id}").json()["data"]["can"]["handover"]


def test_filing_rejects_stale_report(case):
    c = case
    c.sub.status = "ORG_FILING"
    c.report.handover_status = "DONE"
    c.arch.timeline_updated_at = now() + timedelta(seconds=10)
    c.db.flush()
    with pytest.raises(AppError):
        file_package(c.db, c.sub, c.org)


def test_read_only_roles_cannot_modify_material(case, as_client):
    c = case
    m, _ = material(c)
    c.sub.status = "DRAFT"
    c.db.flush()
    pair(c)
    client = as_client(c.cross)
    assert client.delete(f"/api/materials/{m.id}").status_code == 403
    assert client.post(f"/api/materials/{m.id}/versions", files={"file": ("x.pdf", b"%PDF-test")}).status_code == 403
    assert client.post(f"/api/archives/{c.arch.id}/submissions", json={"stage_code": 1}).status_code == 403


def test_filed_material_type_cannot_be_changed(case, as_client):
    c = case
    m, _ = material(c)
    c.sub.status = "FILED"
    c.db.flush()
    assert as_client(c.org).put(f"/api/materials/{m.id}/type", json={"material_type_id": 1}).status_code == 403


def test_ai_check_cannot_run_on_filed_submission(case, as_client):
    c = case
    c.sub.status = "FILED"
    c.db.flush()
    assert as_client(c.student).post(f"/api/submissions/{c.sub.id}/ai-check", json={}).status_code == 403


def test_branch_can_run_self_check_for_delegated_submission(case, as_client):
    c = case
    c.sub.status = "DRAFT"
    c.db.flush()
    assert as_client(c.reviewer).post(f"/api/submissions/{c.sub.id}/ai-check", json={}).status_code == 200


def test_historical_parse_does_not_replace_current_nodes(case, monkeypatch):
    import ai.pipeline as pipeline
    from models import MaterialType
    c = case
    m, old = material(c)
    current = c.add(MaterialVersion, material_id=m.id, version_no=2, original_filename="b.pdf",
                    stored_path=uuid4().hex + ".pdf", file_ext="pdf", mime_type="application/pdf",
                    file_size=10, sha256="1" * 64, parse_status="DONE", uploaded_at=now())
    m.current_version_id = current.id
    m.type_id = c.db.query(MaterialType.id).first()[0]
    m.type_status = "AUTO"
    original_type = m.type_id
    ex = c.add(TimeNodeExtraction, archive_id=c.arch.id, node_code="T02", material_id=m.id,
               material_version_id=current.id, value_date=date(2025, 1, 1), method="RULE", is_current=True, created_at=now())
    monkeypatch.setattr(pipeline, "parse_version_file", lambda *args: {"parser": "PDF_TEXT", "full_text": "旧材料"})
    monkeypatch.setattr(pipeline, "classify_material", lambda *args: {"type_id": None, "type_source": "AUTO", "type_confidence": 0.1, "type_status": "NEEDS_CONFIRM"})
    monkeypatch.setattr(pipeline, "extract_nodes", lambda *args: [{"node_code": "T02", "value_date": date(2024, 1, 1)}])
    pipeline.parse_version(c.db, old.id)
    c.db.refresh(ex)
    assert ex.is_current
    assert m.type_id == original_type
    assert not c.db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_version_id == old.id).one().is_current


def test_batch_review_continues_after_one_item_fails(case, as_client):
    c = case
    c.report.handover_status = "DONE"
    c.report.effective_recommendation = "SUGGEST_PASS"
    c.db.flush()
    result = as_client(c.reviewer).post("/api/submissions/batch-review", json={
        "submission_ids": [999999, c.sub.id], "level": "BRANCH"})
    assert result.status_code == 200, result.text
    assert result.json()["data"]["passed"] == [c.sub.id]
    assert len(result.json()["data"]["failed"]) == 1


def test_comment_only_return_generates_visible_exportable_notice(case, as_client):
    from io import BytesIO
    from docx import Document
    from models import Notice
    from services.exporter import export_notice_file
    c = case
    comment = "请补充完整的个人经历说明并重新提交"
    response = as_client(c.reviewer).post(f"/api/submissions/{c.sub.id}/review", json={
        "level": "BRANCH", "decision": "return", "comment": comment})
    assert response.status_code == 200, response.text
    notice = c.db.get(Notice, response.json()["data"]["notice_id"])
    assert notice.content["note"] == comment
    exported = export_notice_file(notice, "docx")
    assert comment in "\n".join(p.text for p in Document(BytesIO(exported.body)).paragraphs)


def test_node_merge_preserves_filed_locked_value(case):
    from models import ArchiveTimeNode
    from services.timeline import merge_archive_nodes
    c = case
    m, v = material(c)
    node = c.add(ArchiveTimeNode, archive_id=c.arch.id, node_code="T02",
                 value_date=date(2023, 1, 1), locked=True, updated_at=now())
    c.add(TimeNodeExtraction, archive_id=c.arch.id, node_code="T02", material_id=m.id, material_version_id=v.id, value_date=date(2025, 1, 1),
          method="RULE", is_current=True, created_at=now())
    merge_archive_nodes(c.db, c.arch.id)
    assert node.value_date == date(2023, 1, 1)


def test_manual_extraction_wins_over_automatic_value(case):
    from models import ArchiveTimeNode
    from services.timeline import merge_archive_nodes
    c = case
    m, v = material(c)
    for method, value in [("RULE", date(2023, 1, 1)), ("MANUAL", date(2024, 1, 1))]:
        c.add(TimeNodeExtraction, archive_id=c.arch.id, node_code="T02", material_id=m.id, material_version_id=v.id, value_date=value,
              method=method, is_current=True, created_at=now())
    merge_archive_nodes(c.db, c.arch.id)
    node = c.db.query(ArchiveTimeNode).filter_by(archive_id=c.arch.id, node_code="T02").one()
    assert node.value_date == date(2024, 1, 1)
    assert not node.has_conflict


def test_jobs_do_not_leak_other_branch(case, as_client):
    c = case
    j = c.add(Job, job_type="AI_CHECK", status="QUEUED", target_type="submission",
              target_id=c.sub.id, created_by=c.student.id, created_at=now())
    client = as_client(c.cross)
    assert client.get(f"/api/jobs/{j.id}").status_code == 404
    assert client.get("/api/jobs").json()["data"]["total"] == 0
    pair(c)
    assert client.get(f"/api/jobs/{j.id}").status_code == 200


def test_issue_actions_require_current_level(case, as_client):
    c = case
    issue = c.add(Issue, submission_id=c.sub.id, report_id=c.report.id, source="AI_RULE",
                  category="FORMAT", severity="BLOCK", title="缺少签名", description="请补全签名",
                  is_active=True, review_status="PENDING", created_at=now(), updated_at=now())
    assert as_client(c.col).put(f"/api/issues/{issue.id}", json={"action": "confirm"}).status_code == 403
    assert as_client(c.reviewer).put(f"/api/issues/{issue.id}", json={"action": "confirm"}).status_code == 200


def test_issue_response_rejects_foreign_version_and_filed_state(case, as_client):
    c = case
    issue = c.add(Issue, submission_id=c.sub.id, source="MANUAL", category="FORMAT", severity="WARN",
                  title="缺少签名", description="请补全签名", is_active=True, review_status="CONFIRMED",
                  created_at=now(), updated_at=now())
    c.sub.status = "DRAFT"
    c.db.flush()
    client = as_client(c.student)
    assert client.put(f"/api/issues/{issue.id}/response", json={"response_type": "MODIFIED", "version_id": 999999}).status_code == 422
    c.sub.status = "FILED"
    c.db.flush()
    assert client.put(f"/api/issues/{issue.id}/response", json={"response_type": "MODIFIED"}).status_code == 403


def test_version_upload_issue_ids_must_belong_to_material(case, as_client, monkeypatch):
    c = case
    from services import storage as store
    monkeypatch.setattr(store, "save_bytes", lambda data, aid, ext: (f"materials/{aid}/t.pdf", "0" * 64, len(data)))
    m1, _ = material(c)
    m2, _ = material(c)
    m1.version_count = 1
    m2.version_count = 1
    own = c.add(Issue, submission_id=c.sub.id, source="MANUAL", category="FORMAT", severity="WARN",
                title="签名缺失", description="请补签", material_id=m1.id,
                is_active=True, review_status="CONFIRMED", created_at=now(), updated_at=now())
    other = c.add(Issue, submission_id=c.sub.id, source="MANUAL", category="FORMAT", severity="WARN",
                  title="日期有误", description="请修正", material_id=m2.id,
                  is_active=True, review_status="CONFIRMED", created_at=now(), updated_at=now())
    c.sub.status = "RETURNED"
    c.sub.return_level = "BRANCH"
    c.db.flush()
    client = as_client(c.student)
    # 关联其他材料的问题或不存在的问题 → 422
    for bad_ids in (str(other.id), "999999"):
        r = client.post(f"/api/materials/{m1.id}/versions", files={"file": ("v2.pdf", b"%PDF-1.4 test")},
                        data={"change_note": "整改", "issue_ids": bad_ids})
        assert r.status_code == 422, (bad_ids, r.text)
    # 关联本材料的问题 → 正常记为已修改
    r = client.post(f"/api/materials/{m1.id}/versions", files={"file": ("v2.pdf", b"%PDF-1.4 test")},
                    data={"change_note": "整改", "issue_ids": str(own.id)})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["responded_issue_ids"] == [own.id]


def test_spa_fallback_preserves_api_and_asset_errors():
    from main import app
    client = TestClient(app)
    assert client.get("/review/tasks").status_code == 200
    assert client.get("/api/does-not-exist").status_code == 404
    assert client.get("/assets/does-not-exist.js").status_code == 404
    assert client.get("/storage/.secret").status_code == 404
