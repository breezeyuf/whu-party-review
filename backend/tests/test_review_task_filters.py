"""G2：审核待办的 has_block、due_within_days 下推到 SQL，total 与分页同源。

截止日按提交包状态取批次的对应列，与列表 deadline / days_left 同一口径；
today + N 里的“今天”取 utils.now()（UTC+8）。
"""
from __future__ import annotations

from datetime import date, timedelta

from models import Batch
from tests.pg_fixtures import (  # noqa: F401  夹具由 import 引入
    add_archive,
    add_issue,
    add_submission,
    as_client,
    case,
    pg_schema,
)
from utils import now


def add_branch_case(case, *, student_no: str, days: int | None, block: bool = False):
    """一个支部初审的提交包，截止日为 今天 + days（None 表示该层级没有截止日）。"""
    today = now().date()
    batch = case.add(
        Batch, name=f"批次-{student_no}", year=2026, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
        branch_deadline=None if days is None else today + timedelta(days=days),
        created_at=now(), updated_at=now(),
    )
    arch = add_archive(case.db, case, student_no=student_no, branch=0, current_stage=2)
    arch.batch_id = batch.id
    case.db.flush()
    sub = add_submission(case.db, arch, 1, "BRANCH_REVIEW", report=True)
    if block:
        add_issue(case.db, sub)
    return sub


def listing(client, **params):
    response = client.get("/api/submissions", params=params)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_has_block_true_and_false_are_complementary(case, as_client):
    blocked = add_branch_case(case, student_no="2026002001", days=5, block=True)
    add_branch_case(case, student_no="2026002002", days=5)
    client = as_client(case.reviewer)
    every = listing(client, todo="true", page_size=200)
    with_block = listing(client, todo="true", has_block="true", page_size=200)
    without = listing(client, todo="true", has_block="false", page_size=200)
    assert with_block["total"] + without["total"] == every["total"]
    assert [row["id"] for row in with_block["items"]] == [blocked.id]
    assert blocked.id not in {row["id"] for row in without["items"]}
    # 与列表 issue_counts.BLOCK 同源
    assert with_block["items"][0]["issue_counts"]["BLOCK"] == 1


def test_due_within_days_covers_overdue_today_exact_and_excludes_beyond(case, as_client):
    overdue = add_branch_case(case, student_no="2026002011", days=-2)
    today_case = add_branch_case(case, student_no="2026002012", days=0)
    exact = add_branch_case(case, student_no="2026002013", days=3)
    beyond = add_branch_case(case, student_no="2026002014", days=4)
    no_deadline = add_branch_case(case, student_no="2026002015", days=None)
    client = as_client(case.reviewer)
    data = listing(client, todo="true", due_within_days=3, page_size=200)
    ids = {row["id"] for row in data["items"]}
    # case.sub_branch 的截止日也是“今天”，同样命中
    assert {overdue.id, today_case.id, exact.id, case.sub_branch.id} <= ids
    assert beyond.id not in ids
    assert no_deadline.id not in ids
    assert all(row["deadline"] is not None for row in data["items"])
    assert all(row["days_left"] <= 3 for row in data["items"])


def test_due_zero_returns_overdue_and_today(case, as_client):
    overdue = add_branch_case(case, student_no="2026002021", days=-5)
    today_case = add_branch_case(case, student_no="2026002022", days=0)
    tomorrow = add_branch_case(case, student_no="2026002023", days=1)
    data = listing(as_client(case.reviewer), todo="true", due_within_days=0, page_size=200)
    ids = {row["id"] for row in data["items"]}
    assert overdue.id in ids and today_case.id in ids
    assert tomorrow.id not in ids


def test_invalid_filters_return_422(case, as_client):
    client = as_client(case.reviewer)
    for params in ({"due_within_days": -1}, {"due_within_days": 3651}, {"due_within_days": "abc"},
                   {"has_block": "maybe"}):
        response = client.get("/api/submissions", params=params)
        assert response.status_code == 422, (params, response.text)
        body = response.json()
        assert body["code"] == 42200
        assert body["message"] == "参数校验失败"
        assert body["data"]["errors"]


def test_pagination_matches_one_shot_listing(case, as_client):
    for index in range(4):
        add_branch_case(case, student_no=f"20260021{index:02d}", days=index, block=index % 2 == 0)
    client = as_client(case.reviewer)
    everything = listing(client, todo="true", page_size=200, sort="days_left")
    assert everything["total"] > 4
    collected = []
    page = 1
    while True:
        chunk = listing(client, todo="true", page_size=1, page=page, sort="days_left")
        assert chunk["total"] == everything["total"]
        collected.extend(row["id"] for row in chunk["items"])
        if len(collected) >= chunk["total"]:
            break
        page += 1
    assert collected == [row["id"] for row in everything["items"]]


def test_filters_combine_with_recommendation_and_query(case, as_client):
    add_branch_case(case, student_no="2026002031", days=2, block=True)
    client = as_client(case.reviewer)
    data = listing(client, todo="true", has_block="true", due_within_days=7,
                   recommendation="SUGGEST_PASS", q="学生", sort="days_left", page_size=200)
    assert all(row["issue_counts"]["BLOCK"] > 0 for row in data["items"])
    assert all("学生" in (row["student_name"] or "") for row in data["items"])
    assert data["total"] == len(data["items"])


def test_student_query_does_not_duplicate_or_fail(case, as_client):
    response = as_client(case.student).get("/api/submissions", params={"q": "学生", "page_size": 200})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    ids = [row["id"] for row in data["items"]]
    assert len(ids) == len(set(ids))
    assert {case.sub_branch.id, case.sub_draft.id} <= set(ids)
    # 学号同样可查
    by_no = listing(as_client(case.student), q="2026001001")
    assert {row["id"] for row in by_no["items"]} == {case.sub_branch.id, case.sub_draft.id}
