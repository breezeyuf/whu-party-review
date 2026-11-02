from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from models import Job, Issue, UserRole
from tests.test_review_regressions import case, test_engine, as_client
from utils import now
from services.ai_job_policy import actor_params


def job(c, actor=None, **kw):
    actor = actor or c.student
    params = {"submission_id": c.sub.id, "trigger_type": "SELF_CHECK" if actor.role == "STUDENT" else "REVIEW", **actor_params(actor)}
    return c.add(Job, job_type="AI_CHECK", target_type="submission", target_id=c.sub.id,
                 created_by=actor.id, params=params, status=kw.pop("status", "FAILED"),
                 created_at=now(), attempts=3, max_attempts=3, **kw)


@pytest.mark.parametrize("status", ["BRANCH_REVIEW", "CROSS_REVIEW", "COLLEGE_REVIEW", "ORG_FILING", "FILED"])
def test_student_old_job_cannot_bypass_state(case, as_client, status):
    c=case; c.sub.status=status; j=job(c); c.db.flush()
    before=c.sub.latest_report_id
    response=as_client(c.student).post(f"/api/jobs/{j.id}/retry")
    assert response.status_code==403, response.text
    assert j.status=="FAILED" and c.sub.latest_report_id==before and c.sub.ai_status=="DONE"


@pytest.mark.parametrize("change", ["inactive", "grant_removed", "moved_branch", "filed", "cross_assignment_removed"])
def test_worker_rechecks_after_enqueue_without_mutating_evidence(case, monkeypatch, change):
    import worker
    from ai import pipeline
    c=case; c.sub.status="BRANCH_REVIEW"
    actor=c.reviewer
    if change=="cross_assignment_removed":
        from tests.test_review_regressions import pair
        pair(c,user=c.cross.id);c.sub.status="CROSS_REVIEW";actor=c.cross
    j=job(c,actor,status="RUNNING");j.started_at=now()
    issue=c.add(Issue,submission_id=c.sub.id,report_id=c.report.id,source="AI_RULE",category="CONTENT",severity="WARN",title="原审核依据",description="虚构问题",is_active=True,created_at=now(),updated_at=now())
    if change=="inactive":actor.user.is_active=False
    elif change=="grant_removed":c.db.query(UserRole).filter(UserRole.user_id==actor.id).delete(synchronize_session=False)
    elif change=="moved_branch":c.sub.branch_id=c.branches[1].id
    elif change=="filed":c.sub.status="FILED"
    else:
        from models import CrossReviewPair
        c.db.query(CrossReviewPair).delete(synchronize_session=False)
    c.db.flush();old=(c.sub.latest_report_id,c.sub.ai_status)
    run=Mock();monkeypatch.setattr(pipeline,"run_check",run);monkeypatch.setattr(worker,"_pulse",lambda *a,**k:None)
    worker._run(c.db,j)
    assert not run.called and j.status=="FAILED" and "检查已停止" in j.stage_text
    assert (c.sub.latest_report_id,c.sub.ai_status)==old and issue.is_active


def test_legal_retry_and_two_old_jobs_deduplicate(case, as_client):
    c=case;c.sub.status="DRAFT";a=job(c);b=job(c);c.db.flush();client=as_client(c.student)
    assert client.post(f"/api/jobs/{a.id}/retry").status_code==200
    assert client.post(f"/api/jobs/{b.id}/retry").status_code==409
    assert a.status=="QUEUED" and b.status=="FAILED"
    assert client.post(f"/api/submissions/{c.sub.id}/ai-check").json()["data"]["job_id"]==a.id


def test_revoked_identity_cannot_retry_under_other_grant(case, as_client):
    c=case;c.sub.status="DRAFT";j=job(c);c.db.query(UserRole).filter(UserRole.user_id==c.student.id).delete(synchronize_session=False);c.db.flush()
    assert as_client(c.student).post(f"/api/jobs/{j.id}/retry").status_code==403


def test_retry_manager_also_needs_current_review_permission(case, as_client):
    c=case;c.sub.status="DRAFT";j=job(c);c.db.flush()
    assert as_client(c.org).post(f"/api/jobs/{j.id}/retry").status_code==403


def test_valid_legacy_self_check_job_is_supported(case, as_client):
    c=case;c.sub.status="RETURNED";c.sub.return_level="BRANCH";j=job(c);j.params={"submission_id":c.sub.id,"trigger_type":"SELF_CHECK"};c.db.flush()
    assert as_client(c.student).post(f"/api/jobs/{j.id}/retry").status_code==200


def test_new_jobs_keep_identity_and_batches_reserve_submission(case, as_client):
    c=case;c.sub.status="BRANCH_REVIEW";client=as_client(c.reviewer)
    response=client.post("/api/ai-check/batch",json={"submission_ids":[c.sub.id]})
    assert response.status_code==200,response.text
    parent=c.db.get(Job,response.json()["data"]["job_id"])
    assert parent.params["actor_role"]==c.reviewer.role
    assert client.post(f"/api/submissions/{c.sub.id}/ai-check").status_code==409
    assert client.post("/api/ai-check/batch",json={"submission_ids":[c.sub.id]}).status_code==409


def test_batch_retry_validates_all_children_before_any_requeue(case, as_client):
    c=case;c.sub.status="FILED"
    parent=c.add(Job,job_type="BATCH_AI_CHECK",status="PARTIAL",created_by=c.reviewer.id,params={"submission_ids":[c.sub.id],**actor_params(c.reviewer)},created_at=now())
    child=job(c,c.reviewer,parent_id=parent.id);c.db.flush()
    assert as_client(c.reviewer).post(f"/api/jobs/{parent.id}/retry").status_code==403
    assert parent.status=="PARTIAL" and child.status=="FAILED"


def test_non_ai_retry_is_unchanged(case, as_client):
    c=case;j=c.add(Job,job_type="EXPORT",status="FAILED",created_by=c.student.id,created_at=now());c.db.flush()
    assert as_client(c.student).post(f"/api/jobs/{j.id}/retry").status_code==200
