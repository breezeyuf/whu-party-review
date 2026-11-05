from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from models import AiReport, Job, Issue, ReviewRecord, Submission, UserRole
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
    c=case;c.sub.status="DRAFT";j=job(c);j.params={"submission_id":c.sub.id,"trigger_type":"SELF_CHECK"};c.db.flush()
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



def confirmed_issue(c):
    return c.add(
        Issue, submission_id=c.sub.id, report_id=c.report.id, source="AI_RULE",
        category="CONTENT", severity="BLOCK", title="已确认问题", description="请整改",
        review_status="CONFIRMED", review_level="BRANCH", reviewed_by=c.reviewer.id,
        reviewed_at=now(), is_active=True, response_type="EXPLAINED",
        response_text="已核对并补充说明", responded_at=now(), created_at=now(), updated_at=now(),
    )


def evidence(c, issue):
    c.db.flush()
    c.db.refresh(c.sub)
    c.db.refresh(issue)
    return (
        c.sub.status, c.sub.return_level, c.sub.round_no, c.sub.latest_report_id,
        c.sub.ai_status, c.sub.ai_job_id,
        tuple(getattr(issue, column.name) for column in Issue.__table__.columns),
        c.db.query(AiReport).filter_by(submission_id=c.sub.id).count(),
    )


def resubmit(c, level="BRANCH"):
    from services.workflow import submit_package

    c.sub.status = "RETURNED"
    c.sub.return_level = level
    issue = confirmed_issue(c)
    result = submit_package(c.db, c.sub, c.student, "已完成整改，请复核")
    c.db.flush()
    return (c.db.get(Job, result["recheck_job_id"]),
            c.db.get(ReviewRecord, result["review_record_id"]), issue)


@pytest.mark.parametrize("status", [
    "DRAFT", "RETURNED", "BRANCH_REVIEW", "CROSS_REVIEW",
    "COLLEGE_REVIEW", "ORG_FILING", "FILED",
])
@pytest.mark.parametrize("identity", ["student", "reviewer", "cross", "col", "org", "sys", "other"])
def test_can_actions_check_permissions(case, status, identity):
    from services.workflow import can_actions
    from tests.test_review_regressions import pair

    c = case
    pair(c, user=c.cross.id)
    actor = (c.actor("system", "SYS_ADMIN", c.school) if identity == "sys" else
             c.actor("other", "STUDENT", c.branches[0]) if identity == "other" else
             getattr(c, identity))
    c.sub.status = status
    c.sub.return_level = "BRANCH" if status == "RETURNED" else None
    c.db.flush()
    actions = can_actions(c.db, c.sub, actor)
    assert actions["self_check"] == (identity == "student" and status == "DRAFT")
    expected = ((status == "DRAFT" and identity in ("student", "reviewer")) or
                (status, identity) in {("BRANCH_REVIEW", "reviewer"),
                                       ("CROSS_REVIEW", "cross"),
                                       ("COLLEGE_REVIEW", "col"), ("ORG_FILING", "org")})
    assert actions["ai_check"] == expected


@pytest.mark.parametrize("identity", ["student", "reviewer", "cross", "col", "org", "sys"])
def test_returned_direct_check_and_retry_preserve_confirmed_issues(case, as_client, identity):
    from services.ai_job_policy import AiJobRejected, validate_ai_job
    from tests.test_review_regressions import pair

    c = case
    pair(c, user=c.cross.id)
    actor = c.actor("system", "SYS_ADMIN", c.school) if identity == "sys" else getattr(c, identity)
    c.sub.status = "RETURNED"
    c.sub.return_level = "BRANCH"
    issue = confirmed_issue(c)
    j = job(c, actor)
    before = evidence(c, issue)
    jobs_before = c.db.query(Job).count()
    client = as_client(actor)
    response = client.post(f"/api/submissions/{c.sub.id}/ai-check")
    # SYS_ADMIN has no material scope; all scoped identities reach the policy denial.
    assert response.status_code == (404 if identity == "sys" else 403), response.text
    assert evidence(c, issue) == before
    response = client.post(f"/api/jobs/{j.id}/retry")
    assert response.status_code == 403, response.text
    assert j.status == "FAILED" and j.attempts == 3
    with pytest.raises(AiJobRejected):
        validate_ai_job(c.db, j)
    assert evidence(c, issue) == before
    assert c.db.query(Job).count() == jobs_before


@pytest.mark.parametrize("level, expected_status", [
    ("BRANCH", "BRANCH_REVIEW"), ("CROSS", "CROSS_REVIEW"),
    ("COLLEGE", "COLLEGE_REVIEW"), ("ORG", "ORG_FILING"),
])
def test_real_resubmit_recheck_validates_and_worker_succeeds(case, monkeypatch, level, expected_status):
    import worker
    from ai import pipeline
    from services.ai_job_policy import validate_ai_job
    from services.workflow import can_actions

    c = case
    old_round = c.sub.round_no
    j, record, issue = resubmit(c, level)
    assert j.status == "QUEUED" and j.created_by == c.student.id
    assert j.params["trigger_type"] == "RECHECK"
    assert j.params["submission_id"] == c.sub.id
    assert j.params["actor_role"] == c.student.role
    assert j.params["actor_org_id"] == c.student.org_id
    assert j.params["resubmit_record_id"] == record.id
    assert (record.action, record.from_status, record.to_status) == ("RESUBMIT", "RETURNED", expected_status)
    assert record.submission_id == c.sub.id and record.reviewer_id == c.student.id
    assert c.sub.round_no == record.round_no == old_round + 1
    assert c.sub.status == expected_status and c.sub.return_level is None
    assert c.sub.ai_job_id == j.id and c.sub.ai_status == "QUEUED"
    assert not can_actions(c.db, c.sub, c.student)["ai_check"]
    assert validate_ai_job(c.db, j).id == c.sub.id

    def run_check(db, sid, trigger, user_id, job_id, *, use_llm):
        assert db is c.db
        assert (sid, trigger, user_id, job_id, use_llm) == (c.sub.id, "RECHECK", c.student.id, j.id, True)
        assert c.sub.ai_status == "RUNNING"
        c.sub.ai_status = "DONE"
        return SimpleNamespace(id=c.report.id, report_no=c.report.report_no)

    run = Mock(side_effect=run_check)
    monkeypatch.setattr(pipeline, "run_check", run)
    monkeypatch.setattr(worker, "_pulse", lambda *a, **k: None)
    j.status = "RUNNING"
    j.started_at = now()
    j.attempts = 1
    c.db.flush()
    j._worker_attempt = (j.id, j.attempts, j.started_at)
    worker._run(c.db, j)
    run.assert_called_once()
    assert j.status == "SUCCEEDED" and j.error is None
    assert j.result == {"report_id": c.report.id, "report_no": c.report.report_no}
    assert c.sub.ai_status == "DONE" and issue.is_active


@pytest.mark.parametrize("identity, level, expected_code", [
    ("student", "BRANCH", 200), ("org", "BRANCH", 403), ("org", "ORG", 200),
    ("sys", "BRANCH", 403),
])
def test_automatic_recheck_retry_owner_exception_and_admin_permission(case, as_client, identity, level, expected_code):
    c = case
    j, _, issue = resubmit(c, level)
    j.status = "FAILED"
    j.attempts = 3
    c.sub.ai_status = "FAILED"
    before = evidence(c, issue)
    actor = c.actor("system", "SYS_ADMIN", c.school) if identity == "sys" else getattr(c, identity)
    response = as_client(actor).post(f"/api/jobs/{j.id}/retry")
    assert response.status_code == expected_code, response.text
    assert j.status == ("QUEUED" if expected_code == 200 else "FAILED")
    assert j.attempts == (0 if expected_code == 200 else 3)
    if expected_code == 403:
        assert evidence(c, issue) == before


@pytest.mark.parametrize("change", [
    "missing_record", "unknown_record", "wrong_job", "old_round", "wrong_state",
    "wrong_reviewer", "wrong_action", "wrong_submission", "wrong_source",
    "unexpected_review_state", "wrong_trigger", "wrong_owner", "inactive_user",
    "grant_removed", "grant_replaced", "inactive_org", "wrong_actor_org",
    "returned_again",
])
def test_outdated_or_forged_recheck_denied_without_changing_evidence(case, as_client, monkeypatch, change):
    import worker
    from ai import pipeline
    from services.ai_job_policy import AiJobRejected, validate_ai_job

    c = case
    j, record, issue = resubmit(c)
    params = dict(j.params)
    forged_record = change in {"wrong_reviewer", "wrong_action", "wrong_submission", "wrong_source", "unexpected_review_state"}
    if forged_record:
        # Audit records are immutable even in tests. Append a deliberately invalid
        # reference rather than trying to rewrite the real resubmission evidence.
        record = ReviewRecord(**{column.name: getattr(record, column.name)
                                 for column in ReviewRecord.__table__.columns if column.name != "id"})
    if change == "missing_record":
        params.pop("resubmit_record_id", None)
    elif change == "unknown_record":
        params["resubmit_record_id"] = -1
    elif change == "wrong_job":
        c.sub.ai_job_id = job(c).id
    elif change == "old_round":
        c.sub.round_no += 1
    elif change == "wrong_state":
        c.sub.status = "COLLEGE_REVIEW"
    elif change == "wrong_reviewer":
        record.reviewer_id = c.reviewer.id
    elif change == "wrong_action":
        record.action = "SUBMIT"
    elif change == "wrong_submission":
        other = c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.sub.batch_id,
                      college_id=c.sub.college_id, branch_id=c.sub.branch_id, status="DRAFT",
                      ai_status="NONE", created_at=now(), updated_at=now())
        record.submission_id = other.id
    elif change == "wrong_source":
        record.from_status = "DRAFT"
    elif change == "unexpected_review_state":
        record.to_status = c.sub.status = "DRAFT"
    elif change == "wrong_trigger":
        params["trigger_type"] = "SELF_CHECK"
    elif change == "wrong_owner":
        c.arch.student_user_id = c.reviewer.id
    elif change == "inactive_user":
        c.student.user.is_active = False
    elif change in ("grant_removed", "grant_replaced"):
        c.db.query(UserRole).filter(UserRole.user_id == c.student.id).delete(synchronize_session=False)
        if change == "grant_replaced":
            c.add(UserRole, user_id=c.student.id, role="STUDENT", org_id=c.branches[1].id, created_at=now())
    elif change == "inactive_org":
        c.branches[0].is_active = False
    elif change == "wrong_actor_org":
        params["actor_org_id"] = c.branches[1].id
    elif change == "returned_again":
        c.sub.status = "RETURNED"
        c.sub.return_level = "BRANCH"
    if forged_record:
        c.db.add(record)
        c.db.flush()
        params["resubmit_record_id"] = record.id
    j.params = params
    j.status = "FAILED"
    j.attempts = 3
    before = evidence(c, issue)
    with pytest.raises(AiJobRejected):
        validate_ai_job(c.db, j)
    assert evidence(c, issue) == before
    response = as_client(c.student).post(f"/api/jobs/{j.id}/retry")
    assert response.status_code == 403, response.text
    assert j.status == "FAILED" and j.attempts == 3
    assert evidence(c, issue) == before

    run = Mock()
    monkeypatch.setattr(pipeline, "run_check", run)
    monkeypatch.setattr(worker, "_pulse", lambda *a, **k: None)
    j.status = "RUNNING"
    j.started_at = now()
    c.db.flush()
    worker._run(c.db, j)
    run.assert_not_called()
    assert j.status == "FAILED" and "检查已停止" in j.stage_text
    after = evidence(c, issue)
    expected = list(before)
    if c.sub.ai_job_id == j.id and before[4] in ("QUEUED", "RUNNING"):
        expected[4] = "FAILED"
    assert after == tuple(expected)


@pytest.mark.parametrize("status,expected", [("BRANCH_REVIEW", 200), ("RETURNED", 403)])
def test_corrected_text_recheck_uses_current_policy_and_identity(case, as_client, status, expected):
    from models import ParseResult
    from tests.test_review_regressions import material
    c = case
    c.sub.status = status
    c.sub.return_level = "BRANCH" if status == "RETURNED" else None
    m, v = material(c)
    pr = c.add(ParseResult, version_id=v.id, parser="PDF_TEXT", full_text="原始文字",
               created_at=now(), updated_at=now())
    before = c.db.query(Job).count()
    client = as_client(c.reviewer)
    response = client.put(f"/api/materials/{m.id}/parsed", json={"corrected_text":"核对后的文字", "recheck":True})
    assert response.status_code == expected, response.text
    if expected == 403:
        assert pr.corrected_text is None and c.db.query(Job).count() == before
        assert client.put(f"/api/materials/{m.id}/parsed", json={"corrected_text":"仅保存人工校正", "recheck":False}).status_code == 200
    else:
        j = c.db.get(Job, response.json()["data"]["job_id"])
        assert j.params["actor_role"] == c.reviewer.role
        assert c.sub.ai_job_id == j.id and c.sub.ai_status == "QUEUED"
        assert client.put(f"/api/materials/{m.id}/parsed", json={"corrected_text":"不应覆盖", "recheck":True}).status_code == 409
        assert pr.corrected_text == "核对后的文字"
