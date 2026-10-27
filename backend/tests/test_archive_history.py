from datetime import timedelta
from uuid import uuid4

from models import AiReport, AuditLog, Issue, MaterialVersion, Notice, ReviewRecord, Submission
from tests.test_review_regressions import as_client, case, material, pair, test_engine
from utils import now


def notice(c, sub, status, title):
    return c.add(Notice, notice_type="RECTIFICATION", submission_id=sub.id,
                 archive_id=c.arch.id, student_user_id=c.student.id, title=title,
                 status=status, content={}, created_by=c.reviewer.id,
                 created_at=now(), updated_at=now(), sent_at=now() if status == "SENT" else None)


def stage_two(c):
    return c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.sub.batch_id,
                 college_id=c.sub.college_id, branch_id=c.sub.branch_id,
                 status="FILED", ai_status="DONE", filed_at=now(), filed_by=c.org.id,
                 created_at=now(), updated_at=now())


def test_cross_reviewer_history_excludes_unassigned_batch(case, as_client):
    c = case
    pair(c)
    hidden = stage_two(c)
    hidden.batch_id = c.batches[1].id
    c.db.flush()
    visible_notice = notice(c, c.sub, "SENT", "已分配批次的通知")
    hidden_notice = notice(c, hidden, "SENT", "未分配批次的通知")
    response = as_client(c.cross).get(f"/api/archives/{c.arch.id}/history")
    assert response.status_code == 200, response.text
    items = response.json()["data"]
    notice_ids = {i['link_id'] for i in items if i['kind'] == 'NOTICE'}
    assert visible_notice.id in notice_ids and hidden_notice.id not in notice_ids
    assert not any(i.get('link_type') == 'submission' and i['link_id'] == hidden.id for i in items)


def test_history_covers_all_events_versions_and_stage_filters(case, as_client):
    c = case
    m, first = material(c)
    first.uploaded_at = now() - timedelta(days=2)
    first.uploaded_by = c.student.id
    second = c.add(MaterialVersion, material_id=m.id, version_no=2,
                   original_filename="new.pdf", stored_path=uuid4().hex + ".pdf",
                   file_ext="pdf", mime_type="application/pdf", file_size=10,
                   sha256="1" * 64, parse_status="DONE", uploaded_at=now() - timedelta(days=1),
                   uploaded_by=c.student.id, change_note="补充签字")
    m.current_version_id = second.id
    c.report.triggered_by = c.reviewer.id
    for action, to_status in (("PASS", "COLLEGE_REVIEW"), ("FILE", "FILED")):
        c.add(ReviewRecord, submission_id=c.sub.id, level="ORG", action=action,
              from_status="ORG_FILING", to_status=to_status, reviewer_id=c.org.id,
              reviewer_name="组织部审核员", reviewer_role="ORG_ADMIN", round_no=1, created_at=now())
    c.sub.filed_at = now()
    visible = notice(c, c.sub, "SENT", "阶段一整改通知")
    c.add(Issue, submission_id=c.sub.id, source="MANUAL", category="TIME", severity="WARN",
          title="旧整改问题", description="需补充说明", review_status="CONFIRMED",
          response_type="EXPLAINED", response_text="旧版本保存的完整整改说明", responded_at=now(),
          created_at=now(), updated_at=now())
    c.add(AuditLog, action="NODE_CORRECTION", object_type="archive", object_id=str(c.arch.id),
          user_id=c.reviewer.id, detail={"node": "T02", "stage_code": 1, "reason": "核对原件"}, created_at=now())
    other_sub = stage_two(c)
    notice(c, other_sub, "SENT", "阶段二整改通知")
    c.add(AiReport, submission_id=other_sub.id, report_no=1, rule_version_id=c.report.rule_version_id,
          trigger_type="REVIEW", mode="RULE_ONLY", status="FAILED", started_at=now(), error="private upstream details")
    c.db.flush()
    client = as_client(c.reviewer)
    data = client.get(f"/api/archives/{c.arch.id}/history?stage_code=1").json()["data"]
    assert {event["kind"] for event in data} == {
        "UPLOAD", "AI_REPORT", "REVIEW", "NOTICE", "ISSUE_RESPONSE", "NODE_CORRECTION", "FILED"}
    assert all(event["stage_code"] == 1 for event in data)
    uploads = [event for event in data if event["kind"] == "UPLOAD"]
    assert [event["version_id"] for event in uploads] == [second.id, first.id]
    assert all(event["actor_name"] == "student" for event in uploads)
    assert len([event for event in data if event["kind"] == "FILED"]) == 1
    assert [event["link_id"] for event in data if event["kind"] == "NOTICE"] == [visible.id]
    assert [event["time"] for event in data] == sorted([event["time"] for event in data], reverse=True)
    all_events = client.get(f"/api/archives/{c.arch.id}/history").json()["data"]
    assert {event["stage_code"] for event in all_events} == {1, 2}
    assert any(event["kind"] == "FILED" and event["stage_code"] == 2 for event in all_events)
    assert "private upstream details" not in str(all_events)
    assert client.get(f"/api/archives/{c.arch.id}/history?stage_code=6").status_code == 422


def test_student_history_hides_draft_notices_and_out_of_scope_archive(case, as_client):
    c = case
    notice(c, c.sub, "DRAFT", "内部通知草稿")
    visible = notice(c, c.sub, "SENT", "已发送通知")
    data = as_client(c.student).get(f"/api/archives/{c.arch.id}/history").json()["data"]
    assert [item["link_id"] for item in data if item["kind"] == "NOTICE"] == [visible.id]
    assert "内部通知草稿" not in str(data)
    assert as_client(c.cross).get(f"/api/archives/{c.arch.id}/history").status_code == 404


def test_history_preserves_each_reply_without_duplicate_latest_fields(case, as_client):
    c = case
    c.sub.status = "RETURNED"
    c.sub.return_level = "BRANCH"
    issue = c.add(Issue, submission_id=c.sub.id, source="MANUAL", category="TIME", severity="WARN",
                  title="整改问题", description="需补充说明", review_status="CONFIRMED",
                  created_at=now(), updated_at=now())
    client = as_client(c.student)
    responses = ["第一次已对照原件补充完整说明", "第二次已再次对照原件补充完整说明"]
    for reply in responses:
        response = client.put(f"/api/issues/{issue.id}/response", json={"response_type": "EXPLAINED", "response_text": reply})
        assert response.status_code == 200, response.text
    data = client.get(f"/api/archives/{c.arch.id}/history").json()["data"]
    replies = [item for item in data if item["kind"] == "ISSUE_RESPONSE"]
    assert [item["detail"] for item in replies] == list(reversed(responses))
    assert all(item["stage_code"] == 1 and item["actor_name"] == "student" for item in replies)


def test_node_correction_history_preserves_reason_stage_and_clear(case, as_client):
    c = case
    client = as_client(c.reviewer)
    endpoint = f"/api/archives/{c.arch.id}/timeline/T02"
    assert client.put(endpoint, json={"date": "2026-01-02", "reason": "核对申请书原件"}).status_code == 200
    assert client.put(endpoint, json={"clear": True, "reason": "撤销错误校正"}).status_code == 200
    data = client.get(f"/api/archives/{c.arch.id}/history?stage_code=1").json()["data"]
    corrections = [event for event in data if event["kind"] == "NODE_CORRECTION"]
    assert [event["detail"] for event in corrections] == ["撤销错误校正", "核对申请书原件"]
    assert corrections[0]["title"].startswith("撤销校正")
    assert corrections[0]["link_type"] == "archive"


def test_source_node_correction_uses_material_stage_and_version(case, as_client):
    c = case
    m, v = material(c)
    for changes in ([], [{"action": "UPDATE", "after": {"node_code": "T02"}}]):
        c.add(AuditLog, action="PARSE_CORRECT", object_type="material", object_id=str(m.id),
              user_id=c.reviewer.id, detail={"version_id": v.id, "reason": "修正识别日期", "extractions": changes}, created_at=now())
    data = as_client(c.reviewer).get(f"/api/archives/{c.arch.id}/history?stage_code=1").json()["data"]
    corrections = [event for event in data if event["kind"] == "NODE_CORRECTION"]
    assert len(corrections) == 1
    assert corrections[0]["version_id"] == v.id and corrections[0]["link_id"] == m.id
