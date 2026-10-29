"""Global aggregate filters do not grant system administrators material access."""
from models import Archive, Org, Submission
from tests.test_review_regressions import case, test_engine, as_client, parsed_material
from utils import now


def test_sysadmin_can_select_returned_organizations_for_aggregates_only(case, as_client):
    c = case
    other_college = c.add(Org, name="另一学院", org_type="COLLEGE", parent_id=c.school.id,
                          created_at=now(), updated_at=now())
    other_branch = c.add(Org, name="另一支部", org_type="BRANCH", parent_id=other_college.id,
                         created_at=now(), updated_at=now())
    other_student = c.actor("other-student", "STUDENT", other_branch)
    other_archive = c.add(
        Archive, student_user_id=other_student.id, student_no="2026002", real_name="另一学生",
        college_id=other_college.id, branch_id=other_branch.id, batch_id=c.batches[0].id,
        current_stage=1, status="ACTIVE", anon_code="test-2026002", created_at=now(), updated_at=now(),
    )
    c.add(Submission, archive_id=other_archive.id, stage_code=1, batch_id=c.batches[0].id,
          college_id=other_college.id, branch_id=other_branch.id, status="BRANCH_REVIEW",
          ai_status="DONE", created_at=now(), updated_at=now())
    actor = c.actor("sysadmin", "SYS_ADMIN", c.school)
    client = as_client(actor)
    organizations = client.get("/api/orgs", params={"flat": "true"})
    assert organizations.status_code == 200
    ids = {row["id"] for row in organizations.json()["data"]}
    assert {c.college.id, c.branches[0].id, other_college.id, other_branch.id} <= ids
    own = client.get("/api/stats/overview", params={"college_id": c.college.id, "branch_id": c.branches[0].id})
    assert own.status_code == 200 and own.json()["data"]["archives"] == 1
    other = client.get("/api/stats/overview", params={"college_id": other_college.id, "branch_id": other_branch.id})
    assert other.status_code == 200 and other.json()["data"]["archives"] == 1
    assert other.json()["data"]["submissions"] == 1
    global_stats = client.get("/api/stats/overview")
    assert global_stats.status_code == 200 and global_stats.json()["data"]["archives"] == 2
    assert global_stats.json()["data"]["submissions"] == 2
    m, _ = parsed_material(c)
    assert client.get(f"/api/archives/{c.arch.id}").status_code == 404
    assert client.get(f"/api/materials/{m.id}").status_code == 404
    assert client.post("/api/stats/export", json={"export_type": "STATS_REPORT"}).status_code == 403

    for restricted_actor in (c.col, c.reviewer):
        restricted_client = as_client(restricted_actor)
        outside = restricted_client.get("/api/stats/overview", params={"college_id": other_college.id})
        assert outside.status_code == 200 and outside.json()["data"]["archives"] == 0
        assert outside.json()["data"]["submissions"] == 0
        allowed = restricted_client.get("/api/stats/overview")
        assert allowed.status_code == 200 and allowed.json()["data"]["archives"] == 1
        assert allowed.json()["data"]["submissions"] == 1
