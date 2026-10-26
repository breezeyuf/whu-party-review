"""Bound OCR failure behavior and preserve whole-document LLM failure semantics."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ai import llm, ocr, ocr_review
from errors import AppError
from tests.test_llm_credentials import endpoint


def test_disabled_ocr_never_waits_for_another_job(monkeypatch):
    lock = Mock()
    monkeypatch.setattr(ocr, '_RUN_LOCK', lock)
    token = ocr.settings.set({'engine':'none'})
    try:
        text, blocks, engine, warning = ocr.ocr_pixmap(None)
    finally:
        ocr.settings.reset(token)
    assert not text and not blocks and engine is None and '未启用' in warning
    lock.acquire.assert_not_called()


def test_child_error_details_never_enter_persistable_diagnostics(monkeypatch):
    private = 'private student text in C:/private-model/secret'
    monkeypatch.setattr(ocr, 'available_engines', lambda:['rapidocr'])
    pool = Mock()
    pool.submit.return_value.result.return_value = ([], private)
    monkeypatch.setattr(ocr, '_pool', lambda:pool)
    token = ocr.settings.set({'engine':'rapidocr'})
    try:
        result = ocr.ocr_pixmap(SimpleNamespace(samples=b'',width=1,height=1,n=3))
    finally:
        ocr.settings.reset(token)
    assert result[:3] == ('',[],None)
    assert result[3] and private not in result[3] and 'private' not in result[3]


def test_ocr_timeout_resets_worker_and_next_request_can_succeed(monkeypatch):
    monkeypatch.setattr(ocr, 'available_engines', lambda:['rapidocr'])
    pool = Mock()
    pool.submit.return_value.result.side_effect = [TimeoutError(), ([('恢复成功',[0,0,1,1],0.9)],None)]
    monkeypatch.setattr(ocr, '_pool', lambda:pool)
    reset = Mock()
    monkeypatch.setattr(ocr, '_reset_pool', reset)
    token = ocr.settings.set({'engine':'rapidocr','timeout_s':1})
    try:
        pix = SimpleNamespace(samples=b'',width=1,height=1,n=3)
        assert '超时' in ocr.ocr_pixmap(pix)[3]
        assert ocr.ocr_pixmap(pix)[0] == '恢复成功'
    finally:
        ocr.settings.reset(token)
    reset.assert_called_once()


@pytest.mark.parametrize('url', ['https://[bad', 'https://vision.invalid:bad/v1',
                                'https://vision.invalid:99999/v1', 'https://vision.invalid /v1'])
def test_malformed_visual_url_is_a_validation_error(url):
    with pytest.raises(AppError):
        ocr_review.validate_config({'base_url':url})


def test_long_document_later_failure_discards_partial_findings(monkeypatch):
    monkeypatch.setattr(llm, 'llm_config', lambda db:{})
    calls = []
    def invoke(db,code,variables,*args,**kwargs):
        calls.append(variables['text'])
        return ({'issues':[{'reason':'partial finding'}]},None,2) if len(calls)==1 else (None,'later failure',3)
    monkeypatch.setattr(llm, '_chat_json', invoke)
    result,error,elapsed = llm.chat_json(None,'CONTENT_CHECK',{'text':'长'*12000})
    assert result is None and error == 'later failure' and elapsed == 5
    assert len(calls) == 2 and llm._ACTIVE_CALLS == 0


def test_explicit_zero_model_temperature_is_preserved(endpoint):
    db,config,_,requests = endpoint
    config['temperature'] = 0
    result,error,_ = llm.chat_json(db,'CONTENT_CHECK',{'text':'测试'})
    assert result == {'issues':[]} and error is None
    assert json.loads(requests[0].content)['temperature'] == 0
