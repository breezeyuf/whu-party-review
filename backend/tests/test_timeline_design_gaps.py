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


def test_missing_upload_date_does_not_hide_another_sources_proven_invalid_date():
    nodes = {"T06": {"date": "2026-01-03", "sources": [
        {"node_code": "T06", "material_id": 1, "version_id": 11,
         "date": "2026-01-03", "upload_date": "2026-01-02"},
        {"node_code": "T06", "material_id": 2, "version_id": 12,
         "date": "2026-01-04", "upload_date": None},
    ]}}
    _, issues, results = _evaluate("R-T21", [{"op": "valid_date", "nodes": "*"}], nodes)
    assert len(issues) == 1 and issues[0].material_version_id == 11
    assert results[0]['result'] == 'FAIL' and results[0]['skipped_sources'] == 1


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


def test_failed_composite_with_missing_operand_is_skipped():
    checks = [{"op": "before", "a": "T02", "b": "T03"},
              {"op": "before", "a": "T04", "b": "T08"}]
    _, issues, results = _evaluate("R-T99", checks, {
        "T02": {"date": "2026-01-10"}, "T03": {"date": "2026-01-01"}})
    assert not issues and results[0]["result"] == "SKIPPED"


def test_required_nodes_still_report_missing_values():
    _, issues, results = _evaluate("R-T22", [
        {"op": "required", "nodes_by_stage": {"4": ["T04"]}},
        {"op": "before", "a": "T04", "b": "T08"}], {})
    assert issues and results[0]["result"] == "FAIL"


def test_sequence_range_does_not_replace_missing_end_with_today():
    _, issues, results = _evaluate("R-T23", [
        {"op": "seq_in_range", "seq": "T06[*]", "from": "T04", "to": "T08"}],
        {"T04": {"date": "2025-01-01"}, "T06": {"seq": ["2025-02-01"]}})
    assert not issues and results[0]["result"] == "SKIPPED"


def test_order_failure_points_to_the_original_material_page():
    nodes = {
        "T02": {"date": "2026-01-10", "sources": [{"node_code": "T02", "extraction_id": 5,
            "material_id": 20, "version_id": 30, "page_no": 1, "bbox": [1, 2, 3, 4], "date": "2026-01-10"}]},
        "T03": {"date": "2026-01-05", "sources": [{"node_code": "T03", "extraction_id": 6,
            "material_id": 21, "version_id": 31, "page_no": 2, "bbox": [5, 6, 7, 8], "date": "2026-01-05"}]},
    }
    _, issues, results = _evaluate("R-T03", [{"op": "before", "a": "T02", "b": "T03", "strict": False}], nodes)
    assert results[0]["result"] == "FAIL"
    assert issues[0].material_id == 21 and issues[0].material_version_id == 31
    assert issues[0].location["node_code"] == "T03"
    assert issues[0].location["extraction_id"] == 6
    assert issues[0].location["page_no"] == 2 and issues[0].location["bbox"] == [5, 6, 7, 8]
    assert len(issues[0].location["related_sources"]) == 2


def test_conflict_keeps_all_source_locations():
    nodes = {"T04": {"date": "2025-01-01", "has_conflict": True, "sources": [
        {"node_code": "T04", "extraction_id": 7, "material_id": 22, "version_id": 32,
         "page_no": 3, "bbox": [1, 1, 2, 2], "date": "2025-01-01"},
        {"node_code": "T04", "extraction_id": 8, "material_id": 23, "version_id": 33,
         "page_no": 4, "bbox": [3, 3, 4, 4], "date": "2025-02-01"},
    ]}}
    _, issues, _ = _evaluate("R-T20", [{"op": "consistent", "nodes": "*"}], nodes)
    assert issues[0].location["node_code"] == "T04"
    assert {row["extraction_id"] for row in issues[0].location["related_sources"]} == {7, 8}
