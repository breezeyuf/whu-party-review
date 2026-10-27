"""Publication rejects malformed DSL before it reaches formal reports."""
from copy import deepcopy
from datetime import date
from io import BytesIO
import json
from types import SimpleNamespace

from openpyxl import Workbook
import pytest

from ai.dsl import DSLContext, NodeVal, run_checks
from errors import AppError
from models import RuleVersion, TimeNodeDef, TimeRule
from schemas.time_rules import validate_time_params
from services.rules import import_kind
from tests.test_review_regressions import test_engine, case, as_client


CODES = {"A", "B", "S", "D"}


@pytest.mark.parametrize("check", [
    {"op": "age_at_least", "birth": "A", "at": "B", "years": 18},
    {"op": "before", "a": "A", "b": "B"},
    {"op": "between", "x": "A", "lower": "B.end", "upper": "$today"},
    {"op": "within", "a": "A", "b": "B", "max": {"value": 3, "unit": "MONTH"}},
    {"op": "at_least", "a": "A", "b": "$upload_date", "min": {"value": 1, "unit": "YEAR"}},
    {"op": "duration_min", "node": "A", "min": {"value": 3, "unit": "DAY"}, "or_hours": 24},
    {"op": "seq_max_gap", "seq": "S[*]", "from": "A", "to": "B", "max": {"value": 5, "unit": "WORKDAY"}},
    {"op": "seq_period_count", "seq": "S", "from": "A", "to": "B", "period_months": 3},
    {"op": "seq_in_range", "seq": "S[*]", "from": "A", "to": "B"},
    {"op": "consistent", "nodes": "*"},
    {"op": "valid_date", "nodes": ["A", "B"]},
    {"op": "required", "nodes_by_stage": {"1": ["A"], "2": []}},
    {"op": "monotonic", "nodes": ["A", "B"]},
    {"op": "derive", "name": "D", "base": "A", "offset": {"value": 1, "unit": "YEAR"}},
])
def test_every_supported_operator_is_validated(check):
    result = validate_time_params({"checks": [check]}, CODES)
    assert result["checks"][0]["op"] == check["op"]


@pytest.mark.parametrize("params", [
    None, {}, {"checks": []}, {"checks": ["before"]}, {"checks": [{"op": "unknown"}]},
    {"checks": [{"op": "before"}]},
    {"checks": [{"op": "before", "a": "A", "b": "MISSING"}]},
    {"checks": [{"op": "before", "a": "A.hours", "b": "B"}]},
    {"checks": [{"op": "before", "a": "A", "b": "B", "strict": "false"}]},
    {"checks": [{"op": "before", "a": "A", "b": "B", "typo": 1}]},
    {"checks": [{"op": "within", "a": "A", "b": "B", "max": {"value": -1, "unit": "DAY"}}]},
    {"checks": [{"op": "within", "a": "A", "b": "B", "max": {"value": True, "unit": "DAY"}}]},
    {"checks": [{"op": "within", "a": "A", "b": "B", "max": {"value": 1, "unit": "WEEK"}}]},
    {"checks": [{"op": "within", "a": "A", "b": "B", "max": {"value": 10**100, "unit": "YEAR"}}]},
    {"checks": [{"op": "seq_period_count", "seq": "S[*]", "from": "A", "to": "B", "period_months": 0}]},
    {"checks": [{"op": "required", "nodes_by_stage": {"6": ["A"]}}]},
    {"checks": [{"op": "required", "nodes_by_stage": {"1": ["MISSING"]}}]},
    {"checks": [{"op": "derive", "name": "UNKNOWN", "base": "A", "offset": {"value": 1, "unit": "YEAR"}}]},
])
def test_invalid_shape_parameters_and_references_are_422(params):
    with pytest.raises(AppError) as error:
        validate_time_params(params, CODES)
    assert error.value.status_code == 422


@pytest.mark.parametrize("check", [
    {"op": "before"},
    {"op": "derive", "name": "D", "base": "A", "offset": {"value": 10**100, "unit": "YEAR"}},
    {"op": "within", "a": "A", "b": "B", "max": {"value": 10000, "unit": "YEAR"}},
])
def test_legacy_invalid_or_overflowing_rule_skips_without_crashing(check):
    ctx = DSLContext({"A": NodeVal("A", date(2026, 1, 1), missing=False),
                      "B": NodeVal("B", date(2026, 2, 1), missing=False)}, date(2026, 3, 1), None)
    result = run_checks(ctx, [check])[0]
    assert result.skipped and not result.ok


@pytest.mark.parametrize("params", [
    "broken", {"checks": "broken"}, {"checks": ["broken"]},
    {"checks": [{"op": "required", "nodes_by_stage": "broken"}]},
    {"checks": [{"op": "required", "nodes_by_stage": {"1": "T01"}}]},
    {"checks": [{"op": "valid_date", "nodes": 42}]},
])
def test_legacy_malformed_rule_does_not_break_other_timeline_rules(params):
    from ai.checks.timeline import run_timeline
    from ai.rule_snapshot import EvaluationContext, RuleSet
    from tests.snapshot_fixtures import version, time_rule
    rv = version()
    rv.snapshot["time_rules"] = [time_rule([], params=params), time_rule([
        {"op": "before", "a": "A", "b": "B"}], code="VALID", id=2)]
    rules = RuleSet.from_version(rv)
    _, drafts, results = run_timeline(None, SimpleNamespace(stage_code=1),
        {"A": {"date": "2026-01-01"}, "B": {"date": "2026-01-02"}},
        rule_set=rules, context=EvaluationContext.capture(rules, {}, None))
    assert results[0]["result"] == "SKIPPED"
    assert results[0]["reason"].startswith("时间规则参数无效")
    assert results[1]["result"] == "PASS" and not drafts


@pytest.mark.parametrize("unit,value,end,expected", [
    ("YEAR", 1, date(2027, 1, 2), False),
    ("YEAR", 1, date(2027, 1, 1), True),
    ("WORKDAY", 1, date(2026, 1, 5), True),
    ("WORKDAY", 0, date(2026, 1, 5), False),
])
def test_sequence_gap_honors_years_and_configured_workdays(unit, value, end, expected):
    ctx = DSLContext({"A": NodeVal("A", date(2026, 1, 1), missing=False),
                      "B": NodeVal("B", end, missing=False)}, date(2027, 2, 1), None,
                     holidays={date(2026, 1, 2)})
    result = run_checks(ctx, [{"op": "seq_max_gap", "seq": "S[*]", "from": "A", "to": "B",
                               "max": {"value": value, "unit": unit}}])[0]
    assert result.ok is expected and not result.skipped


def test_derived_workdays_use_configured_holidays():
    ctx = DSLContext({"A": NodeVal("A", date(2026, 1, 1), missing=False)}, date(2026, 2, 1), None,
                     holidays={date(2026, 1, 2)})
    run_checks(ctx, [{"op": "derive", "name": "D", "base": "A", "offset": {"value": 1, "unit": "WORKDAY"}}])
    assert ctx.derived["D"] == date(2026, 1, 5)


def test_seeded_rules_still_validate(case):
    codes = [row.code for row in case.db.query(TimeNodeDef).all()]
    rules = case.db.query(TimeRule).all()
    assert len(rules) >= 23
    for rule in rules:
        validate_time_params(rule.params, codes)


def test_invalid_create_update_and_trial_do_not_publish(case, as_client):
    c = case
    client = as_client(c.org)
    before = c.db.query(RuleVersion).count()
    existing = c.db.query(TimeRule).filter(TimeRule.code == "R-T01").one()
    old_params = deepcopy(existing.params)
    invalid = {"checks": [{"op": "before", "a": "T01", "b": "UNKNOWN"}]}
    body = {"code": "R-T99", "name": "测试", "rule_type": "ORDER", "params": invalid,
            "severity": "WARN", "message_template": "测试"}
    assert client.post("/api/rules/time-rules", json=body).status_code == 422
    assert client.put(f"/api/rules/time-rules/{existing.id}", json={"params": invalid}).status_code == 422
    assert client.post("/api/rules/dry-run", json={"submission_ids": [c.sub.id],
        "overrides": {"time_rules": [{"code": "R-T01", "params": invalid}]}}).status_code == 422
    assert existing.params == old_params
    assert c.db.query(TimeRule).filter(TimeRule.code == "R-T99").count() == 0
    assert c.db.query(RuleVersion).count() == before


def test_valid_create_and_update_publish_validated_params(case, as_client):
    c = case
    client = as_client(c.org)
    params = {"checks": [{"op": "before", "a": "T01", "b": "T02"}]}
    created = client.post("/api/rules/time-rules", json={"code": "R-T99", "name": "测试",
        "rule_type": "ORDER", "params": params, "severity": "WARN", "message_template": "测试"})
    assert created.status_code == 200, created.text
    row = created.json()["data"]
    updated = client.put(f"/api/rules/time-rules/{row['id']}", json={"params": {
        "checks": [{"op": "before", "a": "T01", "b": "$today", "strict": False}]}})
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["params"]["checks"][0]["strict"] is False


def workbook(params):
    wb = Workbook()
    wb.active.append(["code", "name", "rule_type", "params", "severity", "message_template"])
    wb.active.append(["R-T01", "测试", "ORDER", json.dumps(params), "WARN", "测试"])
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize("mode", ["upsert", "replace"])
def test_import_preview_and_write_reject_same_invalid_row(case, mode):
    c = case
    before = c.db.query(TimeRule).count()
    before_versions = c.db.query(RuleVersion).count()
    data = workbook({"checks": [{"op": "before"}]})
    preview = import_kind(c.db, c.org, "time-rules", data, mode, True)
    assert preview["errors"][0]["row"] == 2
    assert preview["created"] == preview["updated"] == 0
    with pytest.raises(AppError) as error:
        import_kind(c.db, c.org, "time-rules", data, mode, False)
    assert error.value.status_code == 422
    assert c.db.query(TimeRule).count() == before
    assert c.db.query(RuleVersion).count() == before_versions


def test_valid_import_publishes_and_append_preview_matches_write(case):
    c = case
    data = workbook({"checks": [{"op": "before", "a": "T01", "b": "T02"}]})
    preview = import_kind(c.db, c.org, "time-rules", data, "append", True)
    assert preview["skipped"] == 1 and preview["updated"] == 0
    actual = import_kind(c.db, c.org, "time-rules", data, "upsert", False)
    assert actual["updated"] == 1 and not actual["errors"] and actual["rule_version_no"]
