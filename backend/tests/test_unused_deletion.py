"""Deletion must remove mistakes, not history or out-of-scope records."""
import pytest
from models import Archive, ArchiveTimeNode, AuditLog, Job, Material, Submission, User, UserRole
from tests.pg_fixtures import pg_schema, case, as_client
from utils import now


def new_user(c, name="delete_test"):
    u = c.add(User, username=name, real_name="误建测试", password_hash="unused",
              org_id=c.branches[0].id, is_active=True, created_at=now(), updated_at=now())
    c.add(UserRole, user_id=u.id, role="STUDENT", org_id=u.org_id, created_at=now())
    return u


def empty_archive(c, client):
    response = client.post("/api/archives", json={
        "student": {"student_no": "2099990001", "real_name": "误建测试"},
        "branch_id": c.branches[0].id, "current_stage": 1,
    })
    assert response.status_code == 200, response.text
    return response.json()["data"]["archive"]


def test_delete_unused_user_preserves_creation_audit_and_removes_grants(case, as_client):
    u = new_user(case)
    case.add(AuditLog, user_id=case.org_admin.id, username="org_admin", role="ORG_ADMIN",
             action="USER_CREATE", object_type="user", object_id=str(u.id), detail={}, created_at=now())
    client = as_client(case.org_admin)
    assert client.delete(f"/api/users/{u.id}").status_code == 200
    assert case.db.query(User).filter(User.id == u.id).count() == 0
    assert case.db.query(UserRole).filter(UserRole.user_id == u.id).count() == 0
    assert case.db.query(AuditLog).filter(AuditLog.object_id == str(u.id)).count() == 2
    assert client.delete(f"/api/users/{u.id}").status_code == 404


@pytest.mark.parametrize("used", ["login", "audit", "job", "archive"])
def test_used_account_not_deleted(case, as_client, used):
    u = new_user(case) if used != "archive" else case.student.user
    if used == "login":
        u.last_login_at = now()
    elif used == "audit":
        case.add(AuditLog, user_id=u.id, action="LOGIN", detail={}, created_at=now())
    elif used == "job":
        case.add(Job, job_type="AI_CHECK", status="FAILED", created_by=u.id,
                 created_at=now())
    case.db.flush()
    assert as_client(case.org_admin).delete(f"/api/users/{u.id}").status_code == 409
    assert case.db.query(User).filter(User.id == u.id).count() == 1


def test_user_deletion_permissions(case, as_client):
    u = new_user(case)
    assert as_client(case.student).delete(f"/api/users/{u.id}").status_code == 403
    case.add(UserRole, user_id=u.id, role="SYS_ADMIN", org_id=case.school.id, created_at=now())
    assert as_client(case.college_admin).delete(f"/api/users/{u.id}").status_code == 403
    assert as_client(case.org_admin).delete(f"/api/users/{case.org_admin.id}").status_code == 409
    case.db.query(UserRole).filter(UserRole.user_id == u.id, UserRole.role == "SYS_ADMIN").delete()
    assert as_client(case.org_admin).delete(f"/api/users/{case.sys_admin.id}").status_code == 409


def test_delete_empty_archive_keeps_account_allows_recreate(case, as_client):
    client = as_client(case.org_admin)
    a = empty_archive(case, client)
    uid = case.db.query(Archive).filter(Archive.id == a["id"]).one().student_user_id
    assert as_client(case.org_admin).delete(f"/api/users/{uid}").status_code == 409
    assert client.delete(f"/api/archives/{a['id']}").status_code == 200
    assert case.db.query(Submission).filter(Submission.archive_id == a["id"]).count() == 0
    assert case.db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == a["id"]).count() == 0
    assert case.db.query(User).filter(User.id == uid).count() == 1
    assert client.delete(f"/api/archives/{a['id']}").status_code == 404
    b = empty_archive(case, client)
    assert b["id"] != a["id"]
    assert client.delete(f"/api/archives/{b['id']}").status_code == 200
    assert client.delete(f"/api/users/{uid}").status_code == 200


@pytest.mark.parametrize("used", ["material", "deleted_material", "job", "batch_job", "date", "reviewing", "filed"])
def test_archive_history_not_deleted(case, as_client, used):
    client = as_client(case.org_admin)
    a = empty_archive(case, client)
    aid = a["id"]
    sub = case.db.query(Submission).filter(Submission.archive_id == aid).one()
    if "material" in used:
        case.add(Material, archive_id=aid, submission_id=sub.id, stage_code=1,
                 title="test", status="DELETED" if used == "deleted_material" else "ACTIVE",
                 uploaded_by=case.student.id, created_at=now(), updated_at=now())
    elif used == "job":
        case.add(Job, job_type="AI_CHECK", target_type="submission", target_id=sub.id,
                 status="FAILED", created_at=now())
    elif used == "batch_job":
        case.add(Job, job_type="AI_CHECK", params={"submission_ids": [sub.id]},
                 status="QUEUED", created_at=now())
    elif used == "date":
        n = case.db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == aid).first()
        n.corrected_date = now().date()
    else:
        sub.status = "FILED" if used == "filed" else "BRANCH_REVIEW"
    case.db.flush()
    assert client.delete(f"/api/archives/{aid}").status_code == 409
    assert case.db.query(Archive).filter(Archive.id == aid).count() == 1


@pytest.mark.parametrize("who,expected", [("student",403),("cross",403),("sys_admin",403),("reviewer",200)])
def test_archive_delete_role_and_scope(case, as_client, who, expected):
    a = empty_archive(case, as_client(case.org_admin))
    assert as_client(getattr(case, who)).delete(f"/api/archives/{a['id']}").status_code == expected


def test_archive_other_branch_cannot_delete(case, as_client):
    a = empty_archive(case, as_client(case.org_admin))
    case.db.query(Archive).filter(Archive.id == a["id"]).update({"branch_id": case.branches[1].id})
    assert as_client(case.reviewer).delete(f"/api/archives/{a['id']}").status_code == 404


def test_named_cross_assignment_cannot_be_broadened_by_user_deletion(case, as_client):
    from models import CrossReviewPair
    u = new_user(case)
    pair = case.add(CrossReviewPair, batch_id=case.batches[0].id, college_id=case.college.id,
        target_branch_id=case.branches[0].id, reviewer_branch_id=case.branches[1].id,
        reviewer_user_id=u.id, created_at=now())
    assert as_client(case.org_admin).delete(f"/api/users/{u.id}").status_code == 409
    case.db.refresh(pair)
    assert pair.reviewer_user_id == u.id
