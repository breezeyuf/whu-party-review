"""模型请求边界的脱敏回归；使用虚构身份和 HTTP 替身，不连接数据库或真实模型。"""
import json
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from ai import llm
from ai.checks.content import run_content


ARCHIVE = SimpleNamespace(real_name="测试同学甲", student_no="TEST20260001")
PHONE = "13800001234"
ID_CARD = "11010120000101001X"
TEXT = (
    f"姓名：{ARCHIVE.real_name}，学号：{ARCHIVE.student_no}；"
    f"手机号：{PHONE}，身份证号：{ID_CARD}。思想汇报包含学习与实践。"
)


@pytest.fixture
def model_endpoint(monkeypatch):
    requests = []
    settings = {"base_url": "https://model.example.invalid/v1", "model": "test-model"}
    template = SimpleNamespace(system_prompt="核查材料并输出 JSON。", user_prompt="{rules}\n{text}")
    db = Mock()
    db.query.return_value.filter.return_value.first.side_effect = lambda: template
    monkeypatch.setattr(llm, "llm_config", lambda _: settings)
    monkeypatch.setattr(llm, "llm_api_key", lambda _: "test-api-key")
    client_class = httpx.Client

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"issues": []}'}}]})

    monkeypatch.setattr(
        llm.httpx, "Client",
        lambda **kwargs: client_class(transport=httpx.MockTransport(respond), **kwargs),
    )

    def configure(*, use_template=True, extra_settings=None):
        nonlocal template
        if not use_template:
            template = None
        settings.update(extra_settings or {})
        return db, template, requests

    return configure


def payload_text(request):
    payload = json.loads(request.content)
    return "\n".join(message["content"] for message in payload["messages"])


@pytest.mark.parametrize("use_template", [True, False])
def test_outgoing_material_is_redacted_without_changing_original(model_endpoint, use_template):
    db, _, requests = model_endpoint(use_template=use_template)
    variables = {"rules": "检查内容要素", "text": TEXT}
    original = deepcopy(variables)

    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", variables, archive=ARCHIVE)

    assert error is None and result == {"issues": []}
    assert variables == original
    assert len(requests) == 1
    sent = payload_text(requests[0])
    for secret in (ARCHIVE.real_name, ARCHIVE.student_no, PHONE, ID_CARD):
        assert secret not in sent
    for placeholder in ("[姓名]", "[学号]", "[手机号]", "[身份证号]"):
        assert placeholder in sent
    assert "思想汇报包含学习与实践" in sent
    assert requests[0].headers["Authorization"] == "Bearer test-api-key"


def test_no_archive_still_redacts_phone_and_id_card(model_endpoint):
    db, _, requests = model_endpoint()
    _, error, _ = llm.chat_json(db, "CONTENT_CHECK", {"text": TEXT})

    assert error is None
    sent = payload_text(requests[0])
    assert PHONE not in sent and ID_CARD not in sent
    assert "[手机号]" in sent and "[身份证号]" in sent


def test_final_system_and_user_templates_are_redacted(model_endpoint):
    db, template, requests = model_endpoint()
    template.system_prompt = f"为{ARCHIVE.real_name}审核，联系人 {PHONE}。"
    template.user_prompt = f"学号 {ARCHIVE.student_no}，身份证 {ID_CARD}。\n{{text}}"

    llm.chat_json(db, "CONTENT_CHECK", {"text": "普通正文"}, archive=ARCHIVE)

    sent = payload_text(requests[0])
    for secret in (ARCHIVE.real_name, ARCHIVE.student_no, PHONE, ID_CARD):
        assert secret not in sent
    assert "普通正文" in sent


def test_nested_fallback_variables_are_copied_and_redacted(model_endpoint):
    db, _, requests = model_endpoint(use_template=False)
    variables = {"items": [{"text": TEXT}], "count": 1, "enabled": True}
    original = deepcopy(variables)

    llm.chat_json(db, "CONTENT_CHECK", variables, archive=ARCHIVE)

    sent = payload_text(requests[0])
    assert PHONE not in sent and ARCHIVE.real_name not in sent
    assert '"count": 1' in sent and '"enabled": true' in sent
    assert variables == original


@pytest.mark.parametrize("use_template", [True, False])
def test_redaction_precedes_text_limit(model_endpoint, use_template):
    db, _, requests = model_endpoint(use_template=use_template)
    text = "正文" * 2999 + PHONE + "尾部" * 100

    llm.chat_json(db, "CONTENT_CHECK", {"text": text}, archive=ARCHIVE)

    sent = payload_text(requests[0])
    assert "138" not in sent
    assert "尾部" not in sent


def test_explicit_disable_preserves_existing_configuration(model_endpoint):
    db, _, requests = model_endpoint(extra_settings={"desensitize": False})

    llm.chat_json(db, "CONTENT_CHECK", {"text": TEXT}, archive=ARCHIVE)

    sent = payload_text(requests[0])
    assert ARCHIVE.real_name in sent and PHONE in sent


def test_content_pipeline_supplies_current_archive_to_request_boundary(model_endpoint):
    _, _, requests = model_endpoint()
    rule = SimpleNamespace(
        code="R-C02", name="内容核查", basis="测试依据", message_template="检查内容", engine="LLM",
        applies_to=[], severity="WARN",
    )
    db = Mock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [rule]
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
        system_prompt="核查材料", user_prompt="{text}",
    )
    material = SimpleNamespace(id=1, type_id=1, status="ACTIVE")
    version = SimpleNamespace(id=11)
    parsed = SimpleNamespace(corrected_text=None, full_text=TEXT)

    drafts, results = run_content(
        db, SimpleNamespace(archive=ARCHIVE), [material], {1: version}, {11: parsed}, {}, True,
    )

    assert drafts == [] and results[0]["result"] == "PASS"
    assert len(requests) == 1
    sent = payload_text(requests[0])
    assert ARCHIVE.real_name not in sent and ARCHIVE.student_no not in sent


def test_unconfigured_model_sends_nothing(model_endpoint):
    db, _, requests = model_endpoint(extra_settings={"base_url": ""})

    result, error, _ = llm.chat_json(db, "CONTENT_CHECK", {"text": TEXT}, archive=ARCHIVE)

    assert result is None and error == "未配置大模型"
    assert requests == []
