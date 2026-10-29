"""Validate actual HTTP responses; no external model or database is used."""
import json
from types import SimpleNamespace as NS

import httpx
import pytest

from ai import llm
from ai.checks.content import run_content
from models import CheckRule, PoliticalTerm


class Query:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def all(self):
        return self.rows

    def first(self):
        return next(iter(self.rows), None)


class DB:
    def __init__(self, rows=None):
        self.rows = rows or {}

    def query(self, entity):
        return Query(self.rows.get(entity, []))


def issue(confidence=0.8, **changes):
    return dict(snippet="示例原文", reason="疑似需要核对", confidence=confidence, **changes)


def content(*issues):
    return json.dumps({"issues": list(issues)}, ensure_ascii=False)


@pytest.fixture
def endpoint(monkeypatch):
    from services import model_network
    monkeypatch.setattr(model_network, "_resolve", lambda *args: ["10.2.3.4"])
    requests = []
    responses = []
    settings = {"base_url": "https://model.test/v1", "model": "test-model", "max_attempts": 3,
                "api_key_enc": "synthetic-encrypted-key"}
    real_client = httpx.Client

    def respond(request):
        requests.append(request)
        item = responses.pop(0) if len(responses) > 1 else responses[0]
        if isinstance(item, Exception):
            raise item
        if isinstance(item, int):
            return httpx.Response(item, text="external-response-secret")
        if isinstance(item, str):
            item = {"choices": [{"message": {"content": item}}]}
        return httpx.Response(200, json=item)

    monkeypatch.setattr(llm.httpx, "Client", lambda **kw: real_client(transport=httpx.MockTransport(respond), **{k:v for k,v in kw.items() if k != "transport"}))
    monkeypatch.setattr(llm, "llm_config", lambda db: settings)
    monkeypatch.setattr(llm, "decrypt_field", lambda encrypted: "test-key")
    monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)

    def configure(*items, **config):
        responses[:] = items
        settings.update(config)
        return requests

    return configure


@pytest.mark.parametrize("bad", [
    "not JSON", "", "[]", "null", '"text"', "{}", '{"issues": null}',
    '{"issues": {}}', '{"issues": ["bad"]}',
    content({"reason": "缺少原文", "confidence": 0.8}),
    content({"snippet": "原文", "reason": "说明"}),
    content({"snippet": 123, "reason": "说明", "confidence": 0.8}),
    content({"snippet": "原文", "reason": " ", "confidence": 0.8}),
    content(issue("0.8")), content(issue(True)), content(issue(-0.1)),
    content(issue(1.1)), content(issue(float("nan"))), content(issue(float("inf"))),
])
def test_invalid_output_is_retried_once_then_fails(endpoint, bad):
    requests = endpoint(bad)
    data, err, _ = llm.chat_json(DB(), "CONTENT_CHECK", {"text": "虚构样例"})
    assert data is None and err
    assert len(requests) == 2
    assert "虚构样例" not in err and "external-response-secret" not in err


@pytest.mark.parametrize("bad_envelope", [
    [], {}, {"choices": []}, {"choices": [None]},
    {"choices": [{"message": {}}]}, {"choices": [{"message": {"content": 123}}]},
])
def test_invalid_provider_envelope_is_not_a_success(endpoint, bad_envelope):
    requests = endpoint(bad_envelope)
    data, err, _ = llm.chat_json(DB(), "CONTENT_CHECK", {})
    assert data is None and err == "大模型响应结构无效"
    assert len(requests) == 2


@pytest.mark.parametrize("initial", ["not JSON", "{}", content(issue("0.8"))])
def test_valid_retry_recovers_even_with_one_network_attempt(endpoint, initial):
    requests = endpoint(initial, content(issue()), max_attempts=1)
    data, err, _ = llm.chat_json(DB(), "CONTENT_CHECK", {})
    assert err is None and data["issues"][0]["confidence"] == 0.8
    assert len(requests) == 2


def test_valid_empty_and_fenced_output(endpoint):
    requests = endpoint('```json\n{"issues": []}\n```')
    assert llm.chat_json(DB(), "CONTENT_CHECK", {})[:2] == ({"issues": []}, None)
    assert len(requests) == 1


def test_valid_json_object_is_not_extracted_from_a_wrong_root(endpoint):
    requests = endpoint('[{"issues": []}]')
    data, err, _ = llm.chat_json(DB(), "CONTENT_CHECK", {})
    assert data is None and err and len(requests) == 2


def test_nonstandard_json_constant_is_not_ignored_in_extra_fields(endpoint):
    endpoint('{"issues": [], "extra": NaN}')
    data, err, _ = llm.chat_json(DB(), "CONTENT_CHECK", {})
    assert data is None and err


@pytest.mark.parametrize("failure,error", [
    (httpx.ReadTimeout("sensitive-timeout-detail"), "大模型请求超时"),
    (httpx.ConnectError("sensitive-network-detail"), "大模型连接失败"),
    (503, "大模型接口 HTTP 503"),
])
def test_network_retry_budget_and_safe_errors(endpoint, failure, error):
    requests = endpoint(failure)
    assert llm.chat_json(DB(), "CONTENT_CHECK", {})[:2] == (None, error)
    assert len(requests) == 3


def test_http_401_is_not_retried_and_does_not_expose_response_body(endpoint):
    requests = endpoint(401)
    assert llm.chat_json(DB(), "CONTENT_CHECK", {})[:2] == (None, "大模型接口 HTTP 401")
    assert len(requests) == 1


def test_5xx_can_recover_within_network_budget(endpoint):
    requests = endpoint(503, content())
    assert llm.chat_json(DB(), "CONTENT_CHECK", {})[:2] == ({"issues": []}, None)
    assert len(requests) == 2


def run_review(db, texts, enabled=True):
    materials = [NS(id=i, type_id=1, status="ACTIVE") for i in range(1, len(texts) + 1)]
    versions = {m.id: NS(id=m.id * 10) for m in materials}
    parses = {m.id * 10: NS(full_text=t, corrected_text=None) for m, t in zip(materials, texts)}
    archive = NS(real_name="虚构学生", student_no="T2026001")
    return run_content(db, NS(archive=archive), materials, versions, parses,
                       {1: NS(code="THOUGHT_REPORT")}, enabled)


def semantic_rule(code="R-C02", **changes):
    data = dict(code=code, name="语义检查", basis="示例", message_template="请核对",
                engine="LLM", applies_to=[], severity="WARN", needs_human_judgement=True)
    data.update(changes)
    return NS(**data)


def rule_db(*semantic_rules):
    local_rule = semantic_rule("R-C01", engine="RULE")
    term = NS(term_type="VARIANT", wrong_variants=["错别字"], standard_text="标准写法")
    return DB({CheckRule: [*semantic_rules, local_rule], PoliticalTerm: [term]})


def test_mixed_rule_executes_rule_and_semantics(endpoint):
    requests = endpoint(content(issue(rule_code='R-C01')))
    mixed=semantic_rule('R-C01',engine='RULE_LLM',params={})
    db=rule_db(mixed)
    drafts,results=run_review(db,['错别字'])
    assert len(requests)==1
    assert {'AI_RULE','AI_LLM'} <= {d.source for d in drafts}
    assert any(r.get('engine')=='LLM' and r['result']=='FAIL' for r in results)


@pytest.mark.parametrize('code', ['CLASSIFY','EXTRACT','SUGGEST'])
def test_enrichment_tasks_reject_empty_objects(endpoint,code):
    endpoint('{}')
    value,error,_=llm.chat_json(DB(),code,{})
    assert value is None and error


@pytest.mark.parametrize("confidence,expected", [(0, 0), (0.1, 0), (0.499, 0), (0.5, 1), (1, 1)])
def test_confidence_threshold_preserves_zero_and_accepts_boundary(endpoint, confidence, expected):
    endpoint(content(issue(confidence)))
    drafts, results = run_review(rule_db(semantic_rule()), ["普通正文"])
    assert len(drafts) == expected
    if drafts:
        assert drafts[0].confidence == confidence
        assert drafts[0].source == "AI_LLM" and drafts[0].needs_human_judgement
    assert results[0]["result"] == ("FAIL" if expected else "PASS")


def test_low_confidence_items_do_not_use_the_ten_issue_limit(endpoint):
    endpoint(content(*([issue(0)] * 10), *([issue(0.8)] * 12)))
    drafts, _ = run_review(rule_db(semantic_rule()), ["普通正文"])
    assert len(drafts) == 10 and all(d.confidence == 0.8 for d in drafts)


def test_partial_semantic_success_is_discarded_on_later_failure(endpoint):
    requests = endpoint(content(issue()), 503)
    drafts, results = run_review(rule_db(semantic_rule(), semantic_rule("R-C07")), ["错别字一", "错别字二"])
    assert len(requests) == 4  # First success, then initial call plus two network retries.
    assert len(drafts) == 2 and all(d.source == "AI_RULE" for d in drafts)
    assert all(r["result"] == "SKIPPED" and r.get("error") for r in results[:2])
    assert results[-1]["result"] == "FAIL"


def test_invalid_output_falls_back_without_hiding_local_findings(endpoint):
    requests = endpoint(content(issue("0.8")))
    drafts, results = run_review(rule_db(semantic_rule()), ["错别字"])
    assert len(requests) == 2
    assert len(drafts) == 1 and drafts[0].source == "AI_RULE"
    assert results[0]["result"] == "SKIPPED" and results[0]["error"]


def test_unexpected_model_exception_does_not_expose_details_or_stop_rules(endpoint):
    endpoint(RuntimeError("secret-provider-detail"))
    drafts, results = run_review(rule_db(semantic_rule()), ["错别字"])
    assert len(drafts) == 1 and drafts[0].source == "AI_RULE"
    assert results[0]["error"] == "大模型调用异常"
    assert "secret-provider-detail" not in str(results)


def test_wrong_rule_code_is_not_misattributed(endpoint):
    endpoint(content(issue(rule_code="R-C99")))
    drafts, results = run_review(rule_db(semantic_rule()), ["普通正文"])
    assert not drafts and "规则编号不匹配" in results[0]["error"]


@pytest.mark.parametrize("texts,rule", [
    ([""], semantic_rule()), (["正文"], semantic_rule(applies_to=["OTHER_TYPE"])),
])
def test_missing_text_or_inapplicable_rule_does_not_claim_pass(endpoint, texts, rule):
    requests = endpoint(content())
    drafts, results = run_review(rule_db(rule), texts)
    assert not requests and not drafts
    assert results[0]["result"] == "SKIPPED" and not results[0].get("error")


def test_model_disabled_never_calls_endpoint(endpoint):
    requests = endpoint(content())
    drafts, results = run_review(rule_db(semantic_rule()), ["错别字"], enabled=False)
    assert not requests and drafts[0].source == "AI_RULE"
    assert results[0]["result"] == "SKIPPED"
