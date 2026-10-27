"""Permission, rejection-audit durability and rectification regressions."""
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session, sessionmaker

from errors import AppError, not_found
from models import AuditLog, Issue, Message, Notice, Org, Submission
from services.audit import log
from tests.test_review_regressions import case, test_engine, as_client
from utils import now


def issue(c, **changes):
    values = dict(submission_id=c.sub.id, report_id=c.report.id, source="AI_RULE", category="TIME",
                  severity="WARN", title="核对日期", description="日期需核对", review_status="CONFIRMED",
                  resolution="OPEN", is_active=True, created_at=now(), updated_at=now())
    values.update(changes)
    return c.add(Issue, **values)


def notice(c, **changes):
    values = dict(notice_type="RECTIFICATION", submission_id=c.sub.id, archive_id=c.arch.id,
                  student_user_id=c.student.id, round_no=1, title="整改通知", content={},
                  status="SENT", created_by=c.reviewer.id, created_at=now(), updated_at=now())
    values.update(changes)
    return c.add(Notice, **values)


@pytest.mark.parametrize("role", ["STUDENT", "SYS_ADMIN"])
@pytest.mark.parametrize("path", ["time-rules", "time-nodes", "prompt-templates", "versions", "time-rules/export"])
def test_rule_library_requires_active_reviewer_role(case, as_client, role, path):
    actor = SimpleNamespace(**{**vars(case.student), "role": role})
    actor.id, actor.username = case.student.id, case.student.username
    response = as_client(actor).get("/api/rules/" + path)
    assert response.status_code == 403


def test_reviewer_can_read_but_not_write_and_student_has_safe_catalog(case, as_client):
    assert as_client(case.reviewer).get("/api/rules/time-rules").status_code == 200
    assert as_client(case.reviewer).post("/api/rules/time-rules", json={}).status_code == 403
    response = as_client(case.student).get("/api/meta")
    assert response.status_code == 200
    nodes = response.json()["data"]["time_nodes"]
    assert nodes and set(nodes[0]) == {"code", "name", "value_kind", "has_hours", "is_active"}


def test_out_of_scope_user_and_notice_are_indistinguishable(case, as_client):
    c = case
    own = notice(c)
    for path in (f"/api/users/{c.student.id}", "/api/users/999999",
                 f"/api/notices/{own.id}", f"/api/notices/{own.id}/export"):
        response = as_client(c.cross).get(path)
        assert response.status_code == 404, response.text
    assert len(c.db.info["access_denials"]) == 4
    assert as_client(c.cross).get(f"/api/users/{c.cross.id}").status_code == 200


def test_denial_audit_survives_business_rollback(test_engine, monkeypatch):
    import database
    monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=test_engine, expire_on_commit=False))
    marker = "denied-" + uuid4().hex
    request = database.get_db()
    db = next(request)
    db.add(Org(name=marker, org_type="SCHOOL", created_at=now(), updated_at=now()))
    db.flush()
    log(db, None, "ACCESS_DENIED", "archive", marker, {"reason": "scope"})
    with pytest.raises(AppError):
        request.throw(not_found())
    with Session(test_engine) as check:
        assert check.query(Org).filter(Org.name == marker).count() == 0
        assert check.query(AuditLog).filter(AuditLog.object_id == marker).count() == 1


def test_caught_denial_commits_once_after_nested_rollback(test_engine, monkeypatch):
    import database
    monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=test_engine, expire_on_commit=False))
    marker = "caught-" + uuid4().hex
    request = database.get_db()
    db = next(request)
    with pytest.raises(AppError):
        with db.begin_nested():
            log(db, None, "ACCESS_DENIED", "submission", marker)
            raise not_found()
    with pytest.raises(StopIteration):
        next(request)
    with Session(test_engine) as check:
        assert check.query(AuditLog).filter(AuditLog.object_id == marker).count() == 1


@pytest.mark.parametrize("changes", [{"review_status": "PENDING"}, {"review_status": "REJECTED"},
                                     {"resolution": "RESOLVED"}, {"is_active": False}])
def test_notice_rejects_unconfirmed_resolved_or_inactive_selection(case, as_client, changes):
    row = issue(case, **changes)
    response = as_client(case.reviewer).post(f"/api/submissions/{case.sub.id}/rectification-notice",
                                           json={"issue_ids": [row.id], "note": "备注"})
    assert response.status_code == 422
    assert case.db.query(Notice).count() == 0


def test_direct_notice_requires_current_reviewer_and_confirmed_issue(case, as_client):
    url = f"/api/submissions/{case.sub.id}/rectification-notice"
    assert as_client(case.col).post(url, json={"note": "上级不能提前生成"}).status_code == 403
    assert as_client(case.reviewer).post(url, json={"note": "备注不能代替问题"}).status_code == 422
    valid = issue(case)
    issue(case, resolution="RESOLVED")
    response = as_client(case.reviewer).post(url, json={"send": False})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert [i["issue_id"] for i in data["content"]["items"]] == [valid.id]
    assert data["status"] == "DRAFT"
    assert as_client(case.student).get(f'/api/notices/{data["id"]}').status_code == 404
    sent = as_client(case.reviewer).post(f'/api/notices/{data["id"]}/send')
    assert sent.status_code == 200
    assert as_client(case.reviewer).post(f'/api/notices/{data["id"]}/send').status_code == 409
    assert case.db.query(Message).filter(Message.link_type == "notice", Message.link_id == data["id"]).count() == 1


def test_review_return_still_allows_comment_without_issues(case, as_client):
    response = as_client(case.reviewer).post(f"/api/submissions/{case.sub.id}/review",
        json={"level": "BRANCH", "decision": "return", "comment": "请按本次要求补充说明"})
    assert response.status_code == 200, response.text
    row = case.db.query(Notice).one()
    assert row.status == "SENT" and row.content["items"] == []


def test_student_notice_filters_use_own_submission_and_hide_drafts(case, as_client):
    sent = notice(case)
    notice(case, status="DRAFT")
    # A different batch exists, but none of this student's notices belongs to it.
    other = case.add(Submission, archive_id=case.arch.id, stage_code=2, batch_id=case.batches[1].id,
                     college_id=case.college.id, branch_id=case.branches[1].id, status="DRAFT",
                     created_at=now(), updated_at=now())
    client = as_client(case.student)
    assert client.get(f"/api/notices?batch_id={other.batch_id}").json()["data"]["total"] == 0
    assert client.get(f"/api/notices?branch_id={other.branch_id}").json()["data"]["total"] == 0
    data = client.get(f"/api/notices?batch_id={case.sub.batch_id}").json()["data"]
    assert data["total"] == 1 and data["items"][0]["id"] == sent.id
