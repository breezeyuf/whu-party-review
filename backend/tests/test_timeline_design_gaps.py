from datetime import date
from types import SimpleNamespace as N

from ai.checks.timeline import run_timeline
from ai.dsl import DSLContext, NodeVal, run_checks


def _evaluate(code, checks, nodes, stage=4):
    rule = N(code=code, name=code, applies_stages=[stage], params={"checks": checks},
             severity="WARN", message_template="", basis="")
    rules = N(rows=lambda group: [rule])
    context = N(calendar={}, today=date(2026, 1, 12))
    return run_timeline(None, N(stage_code=stage), nodes, rule_set=rules, context=context)


def test_composite_rule_skips_when_one_operand_is_missing():
    checks = [
        {"op": "before", "a": "T11.end", "b": "T12", "strict": False},
        {"op": "duration_min", "node": "T11", "min": {"value": 5, "unit": "WORKDAY"}},
    ]
    _, issues, results = _evaluate("R-T10", checks, {"T11": {"date": "2026-01-01", "end_date": "2026-01-10"}})
    assert not issues
    assert results[0]["result"] == "SKIPPED"


def test_derive_rule_skips_without_base_node():
    _, issues, results = _evaluate("R-T16", [
        {"op": "derive", "name": "D01", "base": "T14", "offset": {"value": 1, "unit": "YEAR"}}
    ], {})
    assert not issues
    assert results[0]["result"] == "SKIPPED"


def test_sequence_gap_skips_when_period_boundary_is_missing():
    context = DSLContext({
        "T04": NodeVal("T04", date=date(2025, 1, 1), missing=False),
        "T06": NodeVal("T06", seq=[date(2025, 2, 1), date(2025, 3, 1)]),
    }, date(2025, 4, 1), None)
    result = run_checks(context, [{"op": "seq_max_gap", "seq": "T06[*]", "from": "T04", "to": "T08",
                                   "max": {"value": 3, "unit": "MONTH"}}])[0]
    assert result.skipped


def test_empty_rule_is_not_reported_as_passed():
    _, issues, results = _evaluate("R-T99", [], {})
    assert not issues
    assert results[0]["result"] == "SKIPPED"
