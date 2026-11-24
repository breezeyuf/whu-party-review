"""Match reviewer dashboards to their task lists and deliver resubmission notices."""
from datetime import timedelta
import pytest
from models import CrossReviewPair, Message
from services.dashboard import dashboard
from services.workflow import submit_package
from tests.pg_fixtures import pg_schema, case, as_client
from utils import now


@pytest.mark.parametrize("role,state", [("reviewer","BRANCH_REVIEW"),("college_admin","COLLEGE_REVIEW"),("org_admin","ORG_FILING")])
def test_priority_count_and_rows_match_current_level_deadline_list(case, as_client, role, state):
    for b in case.batches:
        b.self_deadline = now().date() - timedelta(days=2)
        b.branch_deadline = b.cross_deadline = b.college_deadline = b.org_deadline = now().date() - timedelta(days=1)
    case.sub_branch.status = state
    case.db.flush()
    actor = getattr(case,role)
    data = dashboard(case.db, actor)
    expected = as_client(actor).get("/api/submissions?todo=true&due_within_days=7").json()["data"]
    assert data["todo"]["due_soon"] == expected["total"]
    assert {row["submission_id"] for row in data["deadlines"]} == {row["id"] for row in expected["items"]}
    assert case.sub_draft.id not in {row["submission_id"] for row in data["deadlines"]}


@pytest.mark.parametrize("level,state,recipient", [("BRANCH","BRANCH_REVIEW","reviewer"),
    ("COLLEGE","COLLEGE_REVIEW","college_admin"),("ORG","ORG_FILING","org_admin"),
    ("CROSS","CROSS_REVIEW","cross")])
def test_resubmission_notifies_receiving_level_instead_of_always_branch(case, level, state, recipient):
    s=case.sub_branch
    s.status="RETURNED"
    s.return_level=level
    case.db.flush()
    if level == "CROSS":
        case.add(CrossReviewPair,batch_id=s.batch_id,college_id=s.college_id,
                 target_branch_id=s.branch_id,reviewer_branch_id=case.branches[1].id,
                 reviewer_user_id=case.cross.id,created_at=now())
    result=submit_package(case.db,s,case.student,"仅用于隔离测试的整改重新提交")
    assert result["submission"].status == state
    assert result["recheck_job_id"]
    messages=case.db.query(Message).filter(Message.link_type=="submission",Message.link_id==s.id,Message.msg_type=="TASK").all()
    assert {m.user_id for m in messages} == {getattr(case,recipient).id}


def test_reply_saved_before_return_is_retained_but_requires_a_new_response(case, as_client):
    from models import Issue
    s=case.sub_branch
    s.status="RETURNED"
    s.return_level="BRANCH"
    s.level_entered_at=now()
    old_text="这是退回之前保存的自查说明，不能代替本次整改回复。"
    issue=case.add(Issue,submission_id=s.id,report_id=s.latest_report_id,source="AI_RULE",category="FORMAT",severity="WARN",
        title="检查样例签名",description="仅用于测试",is_active=True,review_status="CONFIRMED",
        response_type="EXPLAINED",response_text=old_text,responded_at=now()-timedelta(minutes=5),
        created_at=now(),updated_at=now())
    client=as_client(case.student)
    row=client.get(f"/api/submissions/{s.id}/issues").json()["data"]["items"][0]
    assert row["requires_response"] and row["response_text"]==old_text
    assert client.post(f"/api/submissions/{s.id}/submit",json={}).status_code==409
    response=client.put(f"/api/issues/{issue.id}/response",json={"response_type":"EXPLAINED",
        "response_text":"本次根据退回意见补充新的整改说明，供审核人员核对。"})
    assert response.status_code==200
    assert not client.get(f"/api/submissions/{s.id}/issues").json()["data"]["items"][0]["requires_response"]
    assert client.post(f"/api/submissions/{s.id}/submit",json={}).status_code==200
