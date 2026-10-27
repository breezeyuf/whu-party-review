"""Persist review evidence and exercise the existing manual correction API."""
from copy import deepcopy

from ai import pipeline
from models import ParseResult
from tests.test_review_regressions import case, test_engine, material, as_client


def test_pipeline_persists_review_without_promoting_model_text(case, as_client, monkeypatch):
    from ai import ocr_review
    c = case
    m, v = material(c)
    result = {'parser': 'OCR', 'ocr_engine': 'rapidocr', 'full_text': '本地原文', 'char_count': 4,
              'pages': [{'page_no': 1, 'text': '本地原文', 'source': 'ocr', 'blocks': []}],
              'warnings': [], 'page_count': 1}
    monkeypatch.setattr(pipeline, 'parse_version_file', lambda *a: deepcopy(result))
    def review(db, parsed):
        parsed['pages'][0]['vision_reviews'] = [{'status': 'pending', 'original_text': '本地原文',
            'candidate_text': '模型修正文', 'model': 'synthetic-vision', 'block_index': None,
            'bbox': [0, 0, 100, 100], 'confidence': 0.9, 'uncertain': False}]
    monkeypatch.setattr(ocr_review, 'review_result', review)
    parsed = pipeline.parse_version(c.db, v.id)
    c.db.expire(parsed)
    assert parsed.full_text == '本地原文' and parsed.corrected_text is None
    response = as_client(c.reviewer).get(f'/api/materials/{m.id}/parsed').json()['data']
    assert response['pages'][0]['vision_reviews'][0]['candidate_text'] == '模型修正文'
    saved = as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'corrected_text': '人工核对后的文字', 'corrected_fields': {}, 'recheck': False,
    })
    assert saved.status_code == 200, saved.text
    c.db.expire_all()
    persisted = c.db.query(ParseResult).filter(ParseResult.version_id == v.id).one()
    assert persisted.corrected_text == '人工核对后的文字'
    assert persisted.full_text == '本地原文'
    assert persisted.pages[0]['vision_reviews'][0]['candidate_text'] == '模型修正文'


def test_rule_only_parse_does_not_send_images(case, monkeypatch):
    from ai import ocr_review
    c = case
    _, v = material(c)
    monkeypatch.setattr(pipeline, 'parse_version_file', lambda *a: {'parser': 'NONE', 'full_text': '', 'pages': []})
    def unexpected(*args):
        raise AssertionError('rule-only parsing must not invoke visual review')
    monkeypatch.setattr(ocr_review, 'review_result', unexpected)
    pipeline.parse_version(c.db, v.id, use_llm=False)
