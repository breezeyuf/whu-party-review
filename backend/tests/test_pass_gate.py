"""G1：单份通过、批量通过、组织部备案共用同一套通过前校验。

阻断口径只由 services/workflow.BLOCKING_REVIEW_STATUSES 定义一次：有效（is_active）、
severity=BLOCK 且 review_status=PENDING 才拦截；CONFIRMED/MODIFIED/REJECTED 与失效问题不拦截。
"""
from __future__ import annotations

import pytest

from models import AuditLog, ReviewRecord
from services.workflow import BLOCKING_REVIEW_STATUSES
from tests.pg_fixtures import (  # noqa: F401  夹具由 import 引入
    add_issue,
    add_report,
    as_client,
    case,
    pg_schema,
)

BLOCK_CASES = [
    # (review_status, is_active, 是否应拦截)
    ("PENDING", True, True),
    ("CONFIRMED", True, False),
    ("MODIFIED", True, False),
    ("REJECTED", True, False),
    ("PENDING", False, False),
]


def review_body(level="BRANCH"):
    return {"level": level, "decision": "pass"}


def assert_gate(response, blocked: bool):
    if blocked:
        assert response.status_code == 409, response.text
        assert response.json()["code"] == 40903, response.text
        assert response.json()["message"] == "仍有未处理的阻断问题"
    else:
        assert response.status_code == 200, response.text


def test_blocking_review_statuses_has_a_single_definition():
    assert BLOCKING_REVIEW_STATUSES == ("PENDING",)


@pytest.mark.parametrize("review_status,active,blocked", BLOCK_CASES)
def test_single_pass_uses_the_shared_gate(case, as_client, review_status, active, blocked):
    add_issue(case.db, case.sub_branch, review_status=review_status, active=active)
    response = as_client(case.reviewer).post(
        f"/api/submissions/{case.sub_branch.id}/review", json=review_body()
    )
    assert_gate(response, blocked)


@pytest.mark.parametrize("review_status,active,blocked", BLOCK_CASES)
def test_batch_pass_uses_the_same_gate(case, as_client, review_status, active, blocked):
    add_issue(case.db, case.sub_branch, review_status=review_status, active=active)
    response = as_client(case.reviewer).post(
        "/api/submissions/batch-review",
        json={"level": "BRANCH", "submission_ids": [case.sub_branch.id]},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    if blocked:
        assert data["passed"] == []
        assert data["failed"] == [
            {"submission_id": case.sub_branch.id, "code": 40903, "reason": "仍有未处理的阻断问题"}
        ]
    else:
        assert data["passed"] == [case.sub_branch.id]
        assert data["failed"] == []


@pytest.mark.parametrize("review_status,active,blocked", BLOCK_CASES)
def test_filing_uses_the_same_gate(case, as_client, review_status, active, blocked):
    add_issue(case.db, case.sub_filing, review_status=review_status, active=active)
    response = as_client(case.org_admin).post(
        f"/api/submissions/{case.sub_filing.id}/filing", json={}
    )
    if blocked:
        assert response.status_code == 409, response.text
        assert response.json()["code"] == 40903
    else:
        assert response.status_code == 200, response.text
        assert response.json()["data"]["submission"]["status"] == "FILED"


@pytest.mark.parametrize("path", ["review", "batch", "filing"])
def test_handover_required_blocks_every_path(case, as_client, path):
    sub = case.sub_filing if path == "filing" else case.sub_branch
    report = add_report(case.db, sub, handover_status="REQUIRED", handover_reasons=["KEY_STAGE"])
    sub.latest_report_id = report.id
    case.db.flush()
    client = as_client(case.org_admin if path == "filing" else case.reviewer)
    if path == "review":
        response = client.post(f"/api/submissions/{sub.id}/review", json=review_body())
        assert response.status_code == 409 and response.json()["code"] == 40904
    elif path == "batch":
        response = client.post(
            "/api/submissions/batch-review", json={"level": "BRANCH", "submission_ids": [sub.id]}
        )
        assert response.json()["data"]["failed"] == [
            {"submission_id": sub.id, "code": 40904, "reason": "待人工审核"}
        ]
    else:
        response = client.post(f"/api/submissions/{sub.id}/filing", json={})
        assert response.status_code == 409 and response.json()["code"] == 40904


@pytest.mark.parametrize("path", ["review", "batch", "filing"])
def test_stale_or_running_report_blocks_every_path(case, as_client, path):
    sub = case.sub_filing if path == "filing" else case.sub_branch
    sub.ai_status = "RUNNING"
    case.db.flush()
    client = as_client(case.org_admin if path == "filing" else case.reviewer)
    if path == "review":
        response = client.post(f"/api/submissions/{sub.id}/review", json=review_body())
        assert response.status_code == 409 and response.json()["code"] == 40901
    elif path == "batch":
        response = client.post(
            "/api/submissions/batch-review", json={"level": "BRANCH", "submission_ids": [sub.id]}
        )
        assert response.json()["data"]["failed"] == [
            {"submission_id": sub.id, "code": 40901, "reason": "AI 报告已过期或检查未完成，请重新检查"}
        ]
    else:
        response = client.post(f"/api/submissions/{sub.id}/filing", json={})
        assert response.status_code == 409 and response.json()["code"] == 40901


def test_org_level_is_rejected_before_report_checks(case, as_client):
    case.sub_filing.ai_status = "RUNNING"
    case.db.flush()
    response = as_client(case.org_admin).post(
        f"/api/submissions/{case.sub_filing.id}/review", json={"level": "ORG", "decision": "pass"}
    )
    assert response.status_code == 409
    assert response.json()["message"] == "组织部通过请调用备案接口"


def test_batch_normalizes_dedupes_and_keeps_input_order(case, as_client):
    sid = case.sub_branch.id
    other = case.sub_other_branch.id
    response = as_client(case.reviewer).post("/api/submissions/batch-review", json={
        "level": "BRANCH",
        "submission_ids": [sid, str(sid), "abc", other, 999999, True],
    })
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["passed"] == [sid]  # 去重且保持首次出现的顺序
    assert data["failed"] == [
        {"submission_id": "abc", "code": 42200, "reason": "提交包编号无效"},
        {"submission_id": other, "code": 40400, "reason": "提交包不存在或无权访问"},
        {"submission_id": 999999, "code": 40400, "reason": "提交包不存在或无权访问"},
        {"submission_id": True, "code": 42200, "reason": "提交包编号无效"},
    ]


def test_batch_requires_a_list(case, as_client):
    response = as_client(case.reviewer).post(
        "/api/submissions/batch-review", json={"level": "BRANCH", "submission_ids": "1,2"}
    )
    assert response.status_code == 422
    assert response.json()["message"] == "submission_ids 须为提交包编号列表"


def test_batch_partial_failure_keeps_other_items(case, as_client):
    ok_id = case.sub_branch.id
    add_issue(case.db, case.sub_other_branch)
    response = as_client(case.reviewer).post("/api/submissions/batch-review", json={
        "level": "BRANCH", "submission_ids": [ok_id, case.sub_other_branch.id],
    })
    data = response.json()["data"]
    assert data["passed"] == [ok_id]
    assert [row["code"] for row in data["failed"]] == [40400]


def test_batch_writes_is_batch_record_and_audit(case, as_client):
    sid = case.sub_branch.id
    response = as_client(case.reviewer).post(
        "/api/submissions/batch-review", json={"level": "BRANCH", "submission_ids": [sid, "abc"]}
    )
    assert response.status_code == 200
    record = (
        case.db.query(ReviewRecord)
        .filter(ReviewRecord.submission_id == sid, ReviewRecord.action == "PASS")
        .order_by(ReviewRecord.id.desc())
        .first()
    )
    assert record is not None and record.is_batch is True
    audit = case.db.query(AuditLog).filter(AuditLog.action == "BATCH_REVIEW").order_by(AuditLog.id.desc()).first()
    assert audit is not None
    assert audit.detail["passed"] == [sid]
    assert audit.detail["failed"] == [{"submission_id": "abc", "code": 42200}]


def test_single_pass_record_is_not_batch(case, as_client):
    response = as_client(case.reviewer).post(
        f"/api/submissions/{case.sub_branch.id}/review", json=review_body()
    )
    assert response.status_code == 200
    record = (
        case.db.query(ReviewRecord)
        .filter(ReviewRecord.submission_id == case.sub_branch.id, ReviewRecord.action == "PASS")
        .order_by(ReviewRecord.id.desc())
        .first()
    )
    assert record.is_batch is False
