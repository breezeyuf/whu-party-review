"""Exercise report orchestration with actual model HTTP handling and a session double."""
from contextlib import nullcontext
from types import SimpleNamespace as NS

import pytest

from ai import pipeline
from ai.types import IssueDraft
from models import AiReport, CheckRule, Issue, Material, MaterialType, MaterialVersion, ParseResult, RuleVersion, Submission
from tests.test_llm_output import DB, Query, content, endpoint, issue, rule_db, semantic_rule
from tests.snapshot_fixtures import check_rule, material_type, version


class ReportSession(DB):
    def __init__(self, rows):
        super().__init__(rows)
        self.added = []

    def query(self, entity):
        if entity is AiReport.report_no:
            return Query([])
        return ReportQuery(self.rows.get(entity, []))

    def add(self, row):
        row.id = len(self.added) + 100
        self.added.append(row)

    def flush(self):
        pass

    def begin_nested(self):
        return nullcontext()


class ReportQuery(Query):
    def with_for_update(self):
        return self

    def update(self, *args):
        return 0


@pytest.fixture
def report_case(monkeypatch):
    def create(texts=("普通正文",), configured=True, rules=None):
        base = rule_db(*(rules if rules is not None else [semantic_rule()]))
        archive = NS(real_name="虚构学生", student_no="T2026001", batch=None)
        sub = NS(id=1, archive_id=1, archive=archive, stage_code=1,
                 latest_report_id=None, ai_status="QUEUED")
        materials = [NS(id=i, type_id=1, current_version_id=10, status="ACTIVE", title="样例",
                        type_status="CONFIRMED", type_source="MANUAL", type_confidence=1)
                     for i in range(1, len(texts) + 1)]
        # Each material query uses the same parsed version; distinct texts are used in content tests.
        rv = version()
        rv.snapshot["material_types"] = [material_type()]
        rv.snapshot["check_rules"] = [check_rule(r.code, **{k: v for k, v in vars(r).items() if k != "code"}, id=i)
                                      for i, r in enumerate(base.rows[CheckRule], 1)]
        base.rows.update({
            Submission: [sub], RuleVersion: [rv], Material: materials,
            MaterialType: [NS(id=1, code="THOUGHT_REPORT", name="思想汇报")],
            MaterialVersion: [NS(id=10, version_no=1, parse_status="DONE")],
            ParseResult: [NS(corrected_text=None, full_text=texts[0])],
        })
        db = ReportSession(base.rows)
        local_issue = IssueDraft(category="COMPLETENESS", severity="BLOCK", title="缺材料",
                                 description="固定规则缺项", rule_code="COMPLETENESS")
        monkeypatch.setattr(pipeline, "llm_enabled", lambda db: configured)
        monkeypatch.setattr(pipeline, "get_setting", lambda *args: {"model": "test-model"})
        monkeypatch.setattr(pipeline, "node_map_for_archive", lambda *args, **kw: {})
        monkeypatch.setattr(pipeline, "run_completeness", lambda *args, **kw: (
            {"missing_total": 1}, [local_issue], [{"rule_code": "COMPLETENESS", "result": "FAIL"}]))
        monkeypatch.setattr(pipeline, "run_timeline", lambda *args, **kw: ({}, [], []))
        monkeypatch.setattr(pipeline, "run_format", lambda *args, **kw: ([], []))
        monkeypatch.setattr(pipeline, "fill_suggestions", lambda *args, **kw: None)
        return db, sub

    return create


@pytest.mark.parametrize("failure", [503, "not JSON", content(issue("0.8"))])
def test_failed_semantics_produce_completed_rule_only_report(endpoint, report_case, failure):
    endpoint(failure)
    db, sub = report_case()
    report = pipeline.run_check(db, sub.id)

    assert report.status == "DONE" and report.mode == "RULE_ONLY"
    assert report.degrade_reason and "仅规则" in report.degrade_reason
    assert report.llm_model == "test-model"  # Record the model that was attempted.
    assert report.recommendation == "SUGGEST_RETURN"
    assert report.summary["by_severity"] == {"BLOCK": 1}
    assert "LOW_CONFIDENCE" in report.handover_reasons
    assert sub.ai_status == "DONE" and sub.latest_report_id == report.id
    assert [row.source for row in db.added if isinstance(row, Issue)] == ["AI_RULE"]
    semantic = next(r for r in report.rule_results if r.get("engine") == "LLM")
    assert semantic["result"] == "SKIPPED" and semantic["error"]


@pytest.mark.parametrize("model_result", [content(), content(issue(0)), content(issue(0.5))])
def test_valid_output_keeps_mixed_mode_and_filters_persisted_issues(endpoint, report_case, model_result):
    endpoint(model_result)
    db, sub = report_case()
    report = pipeline.run_check(db, sub.id)
    issues = [row for row in db.added if isinstance(row, Issue)]

    assert report.status == "DONE" and report.mode == "RULE_LLM"
    assert report.degrade_reason is None
    semantic_issues = [row for row in issues if row.source == "AI_LLM"]
    assert len(semantic_issues) == (1 if "0.5" in model_result else 0)
    assert all(row.confidence >= 0.5 and row.needs_human_judgement for row in semantic_issues)


@pytest.mark.parametrize("configured,use_llm,reason", [
    (True, False, "本次未启用大模型"), (False, True, "未配置大模型"),
])
def test_disabled_and_unconfigured_have_distinct_reasons(endpoint, report_case, configured, use_llm, reason):
    requests = endpoint(content())
    db, sub = report_case(configured=configured)
    report = pipeline.run_check(db, sub.id, use_llm=use_llm)
    assert report.mode == "RULE_ONLY" and report.degrade_reason == reason
    assert report.llm_model is None and not requests


@pytest.mark.parametrize("texts,rules", [
    (("",), None), (("普通正文",), []),
])
def test_model_not_executed_is_not_reported_as_mixed_mode(endpoint, report_case, texts, rules):
    requests = endpoint(content())
    db, sub = report_case(texts=texts, rules=rules)
    report = pipeline.run_check(db, sub.id)
    assert report.status == "DONE" and report.mode == "RULE_ONLY"
    assert report.degrade_reason == "无适用材料或语义规则，未执行大模型检查"
    assert report.llm_model is None and not requests


def test_later_failure_cannot_leave_semantic_issues_in_rule_only_report(endpoint, report_case):
    requests = endpoint(content(issue()), 503)
    db, sub = report_case(rules=[semantic_rule(), semantic_rule("R-C07")])
    report = pipeline.run_check(db, sub.id)
    assert report.mode == "RULE_ONLY" and len(requests) == 4
    assert all(row.source == "AI_RULE" for row in db.added if isinstance(row, Issue))
    assert all(r["result"] == "SKIPPED" for r in report.rule_results if r.get("engine") == "LLM")


@pytest.mark.parametrize("model_result,review_status,mode,resolution,resolved", [
    (503, "CONFIRMED", "RULE_ONLY", "OPEN", 0),
    (content(), "CONFIRMED", "RULE_LLM", "RESOLVED", 1),
    (503, "REJECTED", "RULE_ONLY", "RESOLVED", 1),
])
def test_failed_recheck_does_not_claim_old_semantic_issue_resolved(
        endpoint, report_case, model_result, review_status, mode, resolution, resolved):
    endpoint(model_result)
    db, sub = report_case()
    old = NS(id=50, source="AI_LLM", fingerprint="old-semantic-finding", resolution="OPEN", review_status=review_status,
             resolved_by_report_id=None)
    db.rows[AiReport] = [NS(id=90, material_versions=[])]
    db.rows[Issue] = [old]

    report = pipeline.run_check(db, sub.id, trigger_type="RECHECK")

    assert report.mode == mode and old.resolution == resolution
    assert report.recheck_summary["resolved"] == resolved
    assert report.recheck_summary["unresolved"] == 1 - resolved
    assert report.recheck_summary.get("not_rechecked", 0) == 1 - resolved
    assert old.resolved_by_report_id == (report.id if resolved else None)
