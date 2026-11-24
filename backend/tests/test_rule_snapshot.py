"""No live rule query is allowed in these tests of formal review inputs."""
import json
from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timezone, timedelta
from types import SimpleNamespace as NS

import pytest

from ai import llm, pipeline, rule_snapshot
from ai.checks.completeness import run_completeness
from ai.checks.content import run_content
from ai.checks.format import run_format
from ai.checks.timeline import run_timeline
from ai.rule_snapshot import EvaluationContext, RULE_GROUPS, RuleSet
from ai.suggest import fill_suggestions
from models import (AiReport, ArchiveTimeNode, CheckRule, ChecklistItem, Material, MaterialType,
                    MaterialVersion, ParseResult, PoliticalTerm, PromptTemplate, RuleVersion,
                    SensitivePhrase, Submission, SuggestionTemplate, TimeNodeDef, TimeNodeExtraction, TimeRule)
from services.timeline import merge_archive_nodes, node_map_for_archive
from tests.snapshot_fixtures import check_rule, checklist, material_type, time_rule, version
from tests.test_llm_output import DB, content, endpoint
from tests.test_llm_pipeline import ReportSession


class NoQueries:
    def query(self, entity):
        raise AssertionError(f"unexpected live query: {entity}")


class RuleDenySession(ReportSession):
    def query(self, entity):
        if any(entity is model for model in (CheckRule, ChecklistItem, MaterialType, PoliticalTerm, PromptTemplate,
                                             SensitivePhrase, SuggestionTemplate, TimeNodeDef, TimeRule)):
            raise AssertionError(f"unexpected live rule query: {entity}")
        return super().query(entity)


def inputs():
    sub = NS(id=1, archive_id=1, archive=NS(batch=None), stage_code=1)
    mat = NS(id=1, type_id=1, current_version_id=10, status="ACTIVE", title="思想汇报")
    ver = NS(id=10, sha256="file-hash")
    pr = NS(corrected_text=None, full_text="思想汇报：错词、关注词", corrected_fields=None,
            extracted_fields={}, pages=[], visual_marks={}, format_features={}, char_count=12)
    return sub, [mat], {1: ver}, {10: pr}


def rules_version(number=1):
    rv = version(number=number)
    rv.snapshot["material_types"] = [material_type()]
    rv.snapshot["checklist_items"] = [checklist(number)]
    return rv


def context(rules, calendar=None):
    return replace(EvaluationContext.capture(rules, calendar or {}, None), today=date(2026, 1, 9))


def test_v1_and_v2_execute_their_own_counts_after_live_change():
    sub, mats, vers, _ = inputs()
    first = rules_version()
    rules1 = RuleSet.from_version(first)
    # Simulate publication of V2 and mutation of the original ORM JSON reference.
    first.snapshot["checklist_items"][0]["fixed_count"] = 99
    rules2 = RuleSet.from_version(rules_version(2))
    a, _, _ = run_completeness(NoQueries(), sub, mats, {}, rule_set=rules1,
                               context=context(rules1), versions=vers)
    b, _, _ = run_completeness(NoQueries(), sub, mats, {}, rule_set=rules2,
                               context=context(rules2), versions=vers)
    assert a["items"][0]["expected"] == 1 and a["is_complete"]
    assert b["items"][0]["expected"] == 2 and not b["is_complete"]


def test_live_completeness_preview_still_uses_current_configuration(monkeypatch):
    from ai.checks import completeness
    sub, mats, vers, _ = inputs()
    item = NS(**checklist(2), material_type=NS(**material_type()))
    db = DB({ChecklistItem: [item], MaterialVersion: list(vers.values())})
    monkeypatch.setattr(completeness, "get_setting", lambda *a: {})
    result, _, _ = run_completeness(db, sub, mats, {})
    assert result["items"][0]["expected"] == 2


def test_time_rule_parameters_and_check_date_stay_pinned():
    rv = rules_version()
    rv.snapshot["time_rules"] = [time_rule([dict(op="within", a="A", b="B", max={"value": 1, "unit": "DAY"})])]
    rules = RuleSet.from_version(rv)
    rv.snapshot["time_rules"][0]["params"]["checks"][0]["max"]["value"] = 0
    sub, *_ = inputs()
    nodes = {"A": {"date": "2026-01-08"}, "B": {"date": "2026-01-09"}}
    _, old, _ = run_timeline(NoQueries(), sub, nodes, rule_set=rules, context=context(rules))
    updated = RuleSet.from_version(rv)
    _, new, _ = run_timeline(NoQueries(), sub, nodes, rule_set=updated, context=context(updated))
    assert not old and new


def test_nested_snapshot_is_detached_and_immutable():
    rv = rules_version()
    rv.snapshot["check_rules"] = [check_rule("R-F06", "FORMAT", params={"min_chars": {"THOUGHT_REPORT": 100}})]
    rules = RuleSet.from_version(rv)
    row = rules.rows("check_rules")[0]
    rv.snapshot["check_rules"][0]["params"]["min_chars"]["THOUGHT_REPORT"] = 1
    assert row.params["min_chars"]["THOUGHT_REPORT"] == 100
    with pytest.raises(TypeError):
        row.params["min_chars"]["THOUGHT_REPORT"] = 0
    with pytest.raises(FrozenInstanceError):
        row.values = {}
    assert rules.digest != RuleSet.from_version(rv).digest


@pytest.mark.parametrize("group", RULE_GROUPS)
def test_incomplete_historical_snapshot_is_rejected_without_live_fallback(group):
    rv = rules_version()
    del rv.snapshot[group]
    with pytest.raises(ValueError, match="快照不完整"):
        RuleSet.from_version(rv)


def test_invalid_checklist_reference_is_rejected():
    rv = rules_version()
    rv.snapshot["material_types"] = []
    with pytest.raises(ValueError, match="材料类型"):
        RuleSet.from_version(rv)


def test_format_content_terms_phrases_and_suggestions_use_snapshot():
    rv = rules_version()
    rv.snapshot["check_rules"] = [
        check_rule("R-F06", "FORMAT", params={"min_chars": {"THOUGHT_REPORT": 100}}),
        check_rule("R-C01", id=2), check_rule("R-C03", id=3),
    ]
    rv.snapshot["political_terms"] = [dict(id=1, is_active=True, term_type="VARIANT",
                                           wrong_variants=["错词"], standard_text="规范词")]
    rv.snapshot["sensitive_phrases"] = [dict(id=1, is_active=True, phrase="关注词", match_type="EXACT",
                                             category="IDEOLOGY", risk_note="请人工核实")]
    rv.snapshot["suggestion_templates"] = [dict(id=1, is_active=True, rule_code="R-F06", code="SUG_FORMAT",
                                                template_text="V1建议：{要求值}", example_text="V1例子")]
    rules = RuleSet.from_version(rv)
    rv.snapshot["check_rules"].clear()
    rv.snapshot["political_terms"].clear()
    rv.snapshot["sensitive_phrases"].clear()
    rv.snapshot["suggestion_templates"].clear()
    sub, mats, vers, parses = inputs()
    fmt, _ = run_format(NoQueries(), mats, vers, parses, rules.types, rule_set=rules)
    drafts, _ = run_content(NoQueries(), sub, mats, vers, parses, rules.types, False, rule_set=rules)
    fill_suggestions(NoQueries(), fmt, rule_set=rules)
    assert fmt[0].expected_value == "100" and fmt[0].suggestion == "V1建议：100"
    assert fmt[0].suggestion_example == "V1例子"
    assert [d.rule_code for d in drafts] == ["R-C01", "R-C03"]
    assert drafts[0].expected_value == "规范词" and drafts[1].needs_human_judgement


def test_calendar_date_and_batch_end_are_captured_once(monkeypatch):
    rv = rules_version()
    rv.snapshot["checklist_items"] = [checklist(quantity_mode="PER_PERIOD")]
    rv.snapshot["time_rules"] = [time_rule([dict(op="within", a="A", b="B", max={"value": 0, "unit": "WORKDAY"})])]
    rules = RuleSet.from_version(rv)
    calendar = {"holidays": ["2026-01-09"], "period_min_tail_days": 30}
    frozen = context(rules, calendar)
    calendar["holidays"].clear()
    calendar["period_min_tail_days"] = 0
    # Capturing a context under a later clock must not alter the previous one.
    monkeypatch.setattr(rule_snapshot, "now", lambda: datetime(2027, 1, 9, tzinfo=timezone(timedelta(hours=8))))
    later = EvaluationContext.capture(rules, calendar, date(2026, 12, 31))
    sub, mats, vers, _ = inputs()
    nodes = {"A": {"date": "2026-01-08"}, "B": {"date": "2026-01-09"}}
    _, old, _ = run_timeline(NoQueries(), sub, nodes, rule_set=rules, context=frozen)
    _, new, _ = run_timeline(NoQueries(), sub, nodes, rule_set=rules, context=later)
    assert not old and new
    period_nodes = {"T01": NS(date=date(2025, 10, 10))}
    comp, _, _ = run_completeness(NoQueries(), sub, mats, period_nodes, rule_set=rules, context=frozen, versions=vers)
    assert comp["items"][0]["expected"] == 1
    assert frozen.today == date(2026, 1, 9) and frozen.batch_end is None
    saved = json.loads(json.dumps(frozen.to_dict()))
    assert saved["calendar"]["holidays"] == ["2026-01-09"]
    assert saved["calendar_source"] == "CHECK_START_SETTINGS"
    assert "api_key" not in json.dumps(saved)
    with pytest.raises(ValueError, match="不匹配"):
        frozen.validate(RuleSet.from_version(rules_version(2)))


@pytest.mark.parametrize("has_template", [True, False])
def test_prompt_template_is_pinned_even_when_missing_in_snapshot(endpoint, has_template):
    requests = endpoint(content())
    rv = rules_version()
    if has_template:
        rv.snapshot["prompt_templates"] = [dict(id=1, code="CONTENT_CHECK", is_active=True,
                                                 system_prompt="V1系统", user_prompt="V1正文 {text}")]
    rules = RuleSet.from_version(rv)
    rv.snapshot["prompt_templates"].clear()
    parsed, err, _ = llm.chat_json(NoQueries(), "CONTENT_CHECK", {"text": "样例"}, rule_set=rules)
    assert err is None and parsed == {"issues": []}
    sent = json.loads(requests[0].content)["messages"]
    assert sent[0]["content"] == ("V1系统" if has_template else "只输出 JSON。")


def test_pipeline_pins_one_snapshot_through_live_change_and_saves_context(monkeypatch):
    rv = rules_version()
    sub, mats, vers, parses = inputs()
    sub.archive.real_name = "虚构学生"
    sub.archive.student_no = "T2026001"
    mats[0].type_status = "CONFIRMED"
    mats[0].type_source = "MANUAL"
    mats[0].type_confidence = 1
    vers[1].parse_status, vers[1].version_no = "DONE", 1
    db = RuleDenySession({Submission: [sub], RuleVersion: [rv], Material: mats,
                        MaterialVersion: [vers[1]], ParseResult: [parses[10]]})
    monkeypatch.setattr(pipeline, "llm_enabled", lambda db: False)
    monkeypatch.setattr(pipeline, "get_setting", lambda db, key, default: {})

    def concurrent_change(db, archive_id, *, node_defs, material_types):
        assert material_types[1].code == 'THOUGHT_REPORT'
        # An administrator publishes V2 after this check captured V1.
        rv.snapshot["checklist_items"][0]["fixed_count"] = 2
        db.rows[RuleVersion] = [rules_version(2)]
        return {}

    monkeypatch.setattr(pipeline, "node_map_for_archive", concurrent_change)
    report = pipeline.run_check(db, sub.id, use_llm=False)
    assert report.status == "DONE" and report.rule_version_id == 1
    assert report.completeness["is_complete"] and report.completeness["items"][0]["expected"] == 1
    saved = report.timeline_snapshot["evaluation_context"]
    assert saved["rule_version_id"] == 1 and len(saved["snapshot_sha256"]) == 64
    assert saved["today"] and saved["checked_at"]
    # The next check sees the newly published version.
    report2 = pipeline.run_check(db, sub.id, use_llm=False)
    assert report2.rule_version_id == 2 and not report2.completeness["is_complete"]


def test_node_merging_and_mapping_use_supplied_definitions():
    extraction = NS(id=1, node_code="T06", value_date=date(2026, 1, 1), value_end_date=None,
                    hours=None, method="RULE", invalid_reason=None)
    other = NS(**{**vars(extraction), "id": 2, "value_date": date(2026, 2, 1)})
    node = NS(node_code="T06", locked=False, corrected_date=None, corrected_end_date=None, corrected_hours=None)
    db = RuleDenySession({TimeNodeExtraction: [extraction, other], ArchiveTimeNode: [node]})
    defs = [NS(code="T06", value_kind="DATE_SEQ")]
    merge_archive_nodes(db, 1, node_defs=defs)
    assert node.value_date == date(2026, 1, 1) and node.value_end_date == date(2026, 2, 1)
    assert not node.has_conflict
    mapped = node_map_for_archive(db, 1, node_defs=defs)
    assert mapped["T06"]["value_kind"] == "DATE_SEQ" and len(mapped["T06"]["seq"]) == 2


def test_inline_parse_uses_snapshot_types_nodes_and_threshold(monkeypatch):
    rv = rules_version()
    rv.snapshot["time_node_defs"] = [dict(id=1, code="T06", is_active=True, value_kind="DATE_SEQ", extract_keywords=["思想汇报"])]
    rules = RuleSet.from_version(rv)
    ctx = replace(context(rules), classify_confidence_threshold=0.9)
    ver = NS(id=10, material_id=1, stored_path="unused", file_ext="txt")
    mat = NS(id=1, submission_id=1, archive_id=1, current_version_id=10, status="ACTIVE",
             type_id=1, declared_type_id=1, type_status="CONFIRMED")
    db = RuleDenySession({MaterialVersion: [ver], Material: [mat], Submission: [NS()]})
    db.refresh = lambda row: None
    # SQLAlchemy .one() is used only to acquire the submission lock.
    monkeypatch.setattr(type(db.query(Submission)), "one", lambda self: self.first(), raising=False)
    monkeypatch.setattr(pipeline, "parse_version_file", lambda *args: {"full_text": "思想汇报 2026年1月1日", "pages": []})
    seen = {}

    def classify(text, declared, types, threshold):
        seen.update(declared=declared, types=types, threshold=threshold)
        return {}

    def extract(text, pages, material_type, nodes):
        seen.update(material_type=material_type, nodes=nodes)
        return []

    monkeypatch.setattr(pipeline, "classify_material", classify)
    monkeypatch.setattr(pipeline, "extract_nodes", extract)
    monkeypatch.setattr(pipeline, "merge_archive_nodes", lambda db, aid, **kw: seen.update(merge=kw["node_defs"], merge_types=kw['material_types']))
    result = pipeline.parse_version(db, 10, rule_set=rules, context=ctx)
    assert result.full_text and ver.parse_status == "DONE"
    assert seen["declared"].code == "THOUGHT_REPORT" and seen["threshold"] == 0.9
    assert seen["material_type"] == rules.types[1]
    assert seen["nodes"] == seen["merge"] == rules.rows("time_node_defs")
    assert seen['merge_types'] == rules.types


def test_content_pipeline_sends_pinned_prompt_and_rule_to_model(endpoint):
    requests = endpoint(content())
    rv = rules_version()
    rv.snapshot["check_rules"] = [check_rule("R-C02", engine="LLM", basis="V1依据")]
    rv.snapshot["prompt_templates"] = [dict(id=1, code="CONTENT_CHECK", is_active=True,
                                             system_prompt="V1系统", user_prompt="{rules}\n{text}")]
    rules = RuleSet.from_version(rv)
    rv.snapshot["prompt_templates"][0]["system_prompt"] = "V2系统"
    sub, mats, vers, parses = inputs()
    sub.archive = NS(real_name=None, student_no=None)
    drafts, results = run_content(NoQueries(), sub, mats, vers, parses, rules.types, True, rule_set=rules)
    assert not drafts and results[0]["result"] == "PASS"
    sent = json.loads(requests[0].content)["messages"]
    assert sent[0]["content"] == "V1系统" and "V1依据" in sent[1]["content"]


@pytest.mark.parametrize("payload", [{"nodes": {"T01": "2026-01-01"}, "derived": {}},
                                     {"nodes": {}, "evaluation_context": {"format_version": 1}}])
def test_report_detail_accepts_old_and_new_snapshot_shapes(monkeypatch, payload):
    from routers import ai_check
    from services import workflow
    report = AiReport(id=12, submission_id=1, rule_version_id=1, timeline_snapshot=payload)
    db = ReportSession({AiReport: [report], RuleVersion: [NS(id=1, version_no=1)]})
    monkeypatch.setattr(ai_check, "ensure_submission_access", lambda *a: NS(latest_report_id=12))
    monkeypatch.setattr(workflow, "report_is_stale", lambda *a: False)
    result = ai_check.get_report(12, request=None, db=db, actor=None)
    assert result["code"] == 0 and result["data"]["timeline_snapshot"] == payload
