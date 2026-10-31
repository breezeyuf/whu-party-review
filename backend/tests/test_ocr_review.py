import base64
from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import Mock

import fitz
import httpx
import pytest

from ai import ocr_review as review
from errors import AppError


@pytest.fixture
def config():
    return {**review.DEFAULTS, 'enabled': True, 'allow_image_upload': True,
            'base_url': 'https://vision.example.invalid/v1', 'model': 'vision-test',
            'api_key_enc': 'encrypted', 'api_key_base_url': 'https://vision.example.invalid/v1'}


@pytest.fixture
def transport(monkeypatch):
    requests = []
    reply = {'content': {'text': '申请日期2026年10月24日', 'confidence': 0.95, 'uncertain': False}, 'status': 200}
    client = httpx.Client
    def respond(req):
        requests.append(req)
        if reply.get('timeout'):
            raise httpx.ReadTimeout('private response', request=req)
        return httpx.Response(reply['status'], json={'choices': [{'message': {'content': json.dumps(reply['content'])}}]})
    monkeypatch.setattr(httpx, 'Client', lambda **kw: client(transport=httpx.MockTransport(respond), **{k:v for k,v in kw.items() if k != "transport"}))
    monkeypatch.setattr(review, 'decrypt_field', lambda value: 'synthetic-secret')
    return requests, reply


@pytest.fixture
def document(tmp_path, monkeypatch):
    with fitz.open() as doc:
        p = doc.new_page(width=595, height=842)
        p.insert_text((60, 100), '虚构学生 2026', fontname='china-s', fontsize=20)
        doc.save(tmp_path / 'preview.pdf')
    monkeypatch.setattr(review, 'STORAGE_DIR', tmp_path)
    return {'preview_pdf_path': 'preview.pdf', 'full_text': '申请日期2026年10月2日', 'warnings': [],
            'pages': [{'page_no': 1, 'source': 'ocr', 'text': '申请日期2026年10月2日',
                       'blocks': [{'text': '申请日期2026年10月2日', 'conf': 0.5, 'bbox': [50, 70, 330, 110]}]}]}


def test_image_and_ocr_sent_together_without_changing_evidence(monkeypatch, config, transport, document):
    requests, _ = transport
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    original = deepcopy(document)
    review.review_result(None, document)
    assert document['full_text'] == original['full_text']
    page = document['pages'][0]
    assert page['blocks'] == original['pages'][0]['blocks'] and page['text'] == original['pages'][0]['text']
    item = page['vision_reviews'][0]
    assert item['status'] == 'pending' and item['candidate_text'] == '申请日期2026年10月24日'
    assert item['original_text'] == original['full_text'] and item['block_index'] == 0
    assert document['warnings']
    req = requests[0]
    payload = json.loads(req.content)
    assert req.headers['Authorization'] == 'Bearer synthetic-secret'
    assert str(req.url) == config['base_url'] + '/chat/completions'
    content = payload['messages'][1]['content']
    assert original['full_text'] in content[0]['text']
    png = base64.b64decode(content[1]['image_url']['url'].split(',')[1])
    assert png.startswith(b'\x89PNG')
    pix = fitz.Pixmap(png)
    assert pix.width < 1000 and pix.height < 200  # actual crop, not whole-page disclosure
    assert 'synthetic-secret' not in json.dumps(document)


@pytest.mark.parametrize('field', ['enabled', 'allow_image_upload'])
def test_disabled_or_unapproved_never_sends(monkeypatch, config, transport, document, field):
    config[field] = False
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    assert not transport[0]


def test_high_confidence_skips_and_all_pages_option_overrides(monkeypatch, config, transport, document):
    document['pages'][0]['blocks'][0]['conf'] = 0.99
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    assert not transport[0]
    config['review_all'] = True
    review.review_result(None, document)
    assert len(transport[0]) == 1
    assert document['pages'][0]['vision_reviews'][0]['block_index'] is None


def test_empty_local_ocr_can_get_full_page_suggestion(monkeypatch, config, transport, document):
    document['full_text'] = ''
    document['pages'][0].update(text='', blocks=[], source='scan')
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    assert len(transport[0]) == 1 and document['full_text'] == ''
    assert document['pages'][0]['vision_reviews'][0]['status'] == 'pending'


def test_text_layer_is_not_uploaded(monkeypatch, config, transport, document):
    document['pages'][0]['source'] = 'text'
    config['review_all'] = True
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    assert not transport[0]


def test_region_budget(monkeypatch, config, transport, document):
    config['max_regions'] = 1
    document['pages'][0]['blocks'] *= 3
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    assert len(transport[0]) == 1
    assert any('上限' in w for w in document['warnings'])


@pytest.mark.parametrize('failure', ['timeout', 'http', 'schema'])
def test_failure_preserves_ocr_and_stops_further_calls(monkeypatch, config, transport, document, failure):
    requests, reply = transport
    if failure == 'timeout': reply['timeout'] = True
    if failure == 'http': reply['status'] = 500
    if failure == 'schema': reply['content'] = {'text': {'invalid': 'nested text'}}
    document['pages'][0]['blocks'] *= 3
    original = document['full_text']
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    assert document['full_text'] == original and len(requests) == 1
    assert document['pages'][0]['vision_reviews'][0]['status'] == 'failed'
    assert document['warnings'] and 'private response' not in str(document)


def test_credential_binding_blocks_changed_endpoint(config, transport):
    config['base_url'] = 'https://other.example.invalid/v1'
    answer, error = review.review_image(config, b'png', 'test')
    assert answer is None and error and not transport[0]


@pytest.mark.parametrize('patch', [
    {'timeout_s': 0}, {'timeout_s': 121}, {'max_regions': 1.5}, {'max_regions': True},
    {'confidence_threshold': float('nan')}, {'confidence_threshold': 1.1},
    {'enabled': 'true'}, {'base_url': 'file:///tmp'}, {'base_url': 'https://user:pass@host/v1'},
    {'api_key_enc': 'injected'}, {'unknown': 1},
])
def test_invalid_config_rejected(patch):
    with pytest.raises(AppError): review.validate_config(patch)


def test_settings_encrypt_hide_and_bind_independent_key(monkeypatch, config):
    from services import settings
    row = SimpleNamespace(value=deepcopy(config))
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = row
    monkeypatch.setattr(settings, 'get_setting', lambda db, key, default: row.value if key == 'ocr_vision' else {})
    monkeypatch.setattr(settings, 'available_engines', lambda: [])
    monkeypatch.setattr(settings, 'encrypt_field', lambda s: 'encrypted:' + s)
    actor = SimpleNamespace(role='SYS_ADMIN', id=1)
    with pytest.raises(AppError):
        settings.update_settings(db, actor, {'ocr_vision': {'base_url': 'https://changed.invalid/v1'}})
    assert row.value == config
    result = settings.update_settings(db, actor, {'ocr_vision': {'base_url': 'https://changed.invalid/v1', 'api_key': 'new-secret'}})
    assert row.value['api_key_enc'] == 'encrypted:new-secret'
    assert row.value['api_key_base_url'] == 'https://changed.invalid/v1'
    assert result['ocr_vision']['api_key_set'] is True
    assert 'api_key_enc' not in result['ocr_vision'] and 'api_key_base_url' not in result['ocr_vision']
    assert 'new-secret' not in str(result)
    settings.update_settings(db, actor, {'ocr_vision': {'api_key': ''}})
    assert row.value['api_key_enc'] == ''


def test_org_admin_cannot_configure_vision():
    from services.settings import update_settings
    with pytest.raises(AppError) as e:
        update_settings(Mock(), SimpleNamespace(role='ORG_ADMIN'), {'ocr_vision': {'enabled': True}})
    assert e.value.status_code == 403


def test_connection_uses_synthetic_image_even_when_disabled(monkeypatch, config, transport):
    config.update(enabled=False, allow_image_upload=False)
    transport[1]['content']['text'] = '虚构学生 2026'
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    result = review.test_connection(None)
    assert result['ok'] and len(transport[0]) == 1


def test_no_text_model_settings_are_read(monkeypatch, config, transport, document):
    read = Mock(return_value=config)
    monkeypatch.setattr(review, 'get_setting', read)
    review.review_result(None, document)
    read.assert_called_once_with(None, 'ocr_vision', {})


@pytest.fixture(autouse=True)
def synthetic_private_dns(monkeypatch):
    from services import model_network
    monkeypatch.setattr(model_network, "_resolve", lambda *args: ["10.2.3.4"])


def test_text_only_provider_response_is_uncertain_and_preserves_evidence(monkeypatch, config, transport, document):
    requests, reply = transport
    reply['content'] = {'text': 'synthetic transcription'}
    original = deepcopy(document)
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    review.review_result(None, document)
    item = document['pages'][0]['vision_reviews'][0]
    assert len(requests) == 1
    assert item['status'] == 'pending'
    assert item['candidate_text'] == 'synthetic transcription'
    assert item['confidence'] == 0 and item['uncertain'] is True
    assert document['full_text'] == original['full_text']
    assert document['pages'][0]['text'] == original['pages'][0]['text']


def test_text_only_connection_is_not_rejected_for_missing_confidence(monkeypatch, config, transport):
    transport[1]['content'] = {'text': '虚构学生 2026'}
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    assert review.test_connection(None)['ok'] is True


def test_wrong_synthetic_transcription_does_not_pass_connection(monkeypatch, config, transport):
    transport[1]['content'] = {'text': 'unrelated response'}
    monkeypatch.setattr(review, 'get_setting', lambda *args: config)
    assert review.test_connection(None)['ok'] is False


def test_truncated_provider_output_never_becomes_a_suggestion(monkeypatch, config):
    monkeypatch.setattr(review, 'decrypt_field', lambda _: 'synthetic-key')
    response = Mock()
    response.json.return_value = {'choices': [{'finish_reason': 'length', 'message': {'content': '{"text":"partial"}'}}]}
    monkeypatch.setattr(review, '_post_chat', lambda *args: (response, None))
    answer, error = review.review_image(config, b'png', 'synthetic original')
    assert answer is None and '长度上限' in error
