"""Successful inference with no text is reviewable evidence, not an engine error."""
from copy import deepcopy
from datetime import date
from unittest.mock import Mock

import pytest

from ai import ocr, pipeline
from ai.ocr_status import pending_pages, review_warning
from models import AuditLog, Issue, ParseResult, TimeNodeExtraction
from services.workflow import report_is_stale
from tests.test_review_regressions import case, test_engine, as_client, material, parsed_material
from tests.test_rapidocr_review_fixes import make_scan, parse_scan
from utils import now


def empty_page(number=1):
    return {'page_no': number, 'source': 'scan', 'text': '', 'blocks': [], 'ocr_status': 'NEEDS_REVIEW',
            'quality': {'blur_score': 0, 'is_blurry': True}}


@pytest.mark.parametrize('ext', ['pdf', 'png'])
@pytest.mark.parametrize('lines', [[], [(' \n\t', [0, 0, 10, 10], .9)]])
def test_empty_native_result_is_done_and_has_review_evidence(monkeypatch, tmp_path, ext, lines):
    pool = Mock()
    pool.submit.return_value.result.return_value = (lines, None)
    monkeypatch.setattr(ocr, '_pool', lambda: pool)
    monkeypatch.setattr(ocr, 'available_engines', lambda: ['rapidocr'])
    result = parse_scan(monkeypatch, tmp_path, make_scan(tmp_path, ext))
    assert result['ocr_failed'] is False
    assert result['full_text'] == '' and result['ocr_engine'] == 'rapidocr'
    assert result['pages'][0]['ocr_status'] == 'NEEDS_REVIEW'
    assert result['warnings'][0]['code'] == 'OCR-REVIEW'
    assert '空白页' in result['warnings'][0]['message']


def _empty_result():
    return {'parser': 'NONE', 'ocr_engine': 'rapidocr', 'full_text': '', 'pages': [empty_page()],
            'warnings': [review_warning(1)], 'page_count': 1, 'ocr_failed': False}


def test_first_empty_parse_is_editable_done(case, monkeypatch):
    c = case
    m, v = material(c)
    monkeypatch.setattr(pipeline, 'parse_version_file', lambda *args: _empty_result())
    parsed = pipeline.parse_version(c.db, v.id, use_llm=False)
    assert v.parse_status == 'DONE' and v.parse_error is None
    assert parsed.full_text == '' and pending_pages(parsed)


def test_empty_retry_preserves_text_classification_and_all_nodes(case, monkeypatch):
    c = case
    m, v = parsed_material(c)
    parsed = c.db.query(ParseResult).filter_by(version_id=v.id).one()
    parsed.corrected_text = '人工确认正文'
    parsed.corrected_fields = {'name': '人工姓名'}
    parsed.extracted_fields = {'name': '旧识别姓名'}
    parsed.visual_marks = {'anchors': [{'slot': '签名'}]}
    m.type_source, m.type_status, m.type_confidence = 'MANUAL', 'CONFIRMED', 1
    rows = [c.add(TimeNodeExtraction, archive_id=c.arch.id, material_id=m.id,
                  material_version_id=v.id, node_code=code, value_date=date(2026, 1, 1),
                  method=method, is_current=True, created_at=now())
            for code, method in [('T02', 'MANUAL'), ('T06', 'RULE')]]
    monkeypatch.setattr(pipeline, 'parse_version_file', lambda *args: _empty_result())
    pipeline.parse_version(c.db, v.id, use_llm=False)
    c.db.refresh(parsed)
    assert v.parse_status == 'DONE' and v.page_count == 2
    assert parsed.full_text == '原始文本' and parsed.corrected_text == '人工确认正文'
    assert parsed.corrected_fields == {'name': '人工姓名'} and parsed.extracted_fields == {'name': '旧识别姓名'}
    assert parsed.visual_marks['anchors'] and m.type_status == 'CONFIRMED'
    assert all(row.is_current for row in rows)
    assert parsed.pages[0]['ocr_status'] == 'NEEDS_REVIEW'
    assert parsed.warnings[-1]['retained_previous'] is True
    assert '本次重新解析' in parsed.warnings[-1]['message']


def _review_case(c, *, legacy=False, mixed=False):
    m, v = parsed_material(c)
    parsed = c.db.query(ParseResult).filter_by(version_id=v.id).one()
    parsed.full_text = '已识别正文' if mixed else ''
    parsed.pages = [empty_page()]
    if mixed:
        parsed.pages += [{'page_no': 2, 'source': 'text', 'text': '已识别正文'}]
    if legacy:
        parsed.pages[0].pop('ocr_status')
    parsed.warnings = [review_warning(1)]
    v.page_count = len(parsed.pages)
    c.db.flush()
    return m, v, parsed


def _disable_business_rules(c, *, f07=False):
    snapshot = deepcopy(c.rv.snapshot)
    for group in ('checklist_items', 'time_rules', 'check_rules'):
        for row in snapshot[group]:
            row['is_active'] = f07 and group == 'check_rules' and row['code'] == 'R-F07'
            if row.get('code') == 'R-F07':
                row['severity'], row['applies_to'] = 'BLOCK', []
    c.rv.snapshot = snapshot
    c.db.flush()


@pytest.mark.parametrize('legacy', [False, True])
@pytest.mark.parametrize('f07', [False, True])
def test_ocr_warning_prevents_pass_without_automatic_return_and_resolves_on_confirm(case, as_client, legacy, f07):
    c = case
    m, v, parsed = _review_case(c, legacy=legacy)
    _disable_business_rules(c, f07=f07)
    report = pipeline.run_check(c.db, c.sub.id, use_llm=False)
    assert report.status == 'DONE' and report.recommendation == 'NEEDS_REVIEW'
    issue = c.db.query(Issue).filter_by(report_id=report.id, rule_code='OCR-REVIEW').one()
    assert issue.severity == 'WARN' and issue.needs_human_judgement and issue.location['page_no'] == 1
    assert not report_is_stale(c.db, c.sub, report)
    response = as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'ocr_reviewed_pages': [1]})
    assert response.status_code == 200, response.text
    assert report_is_stale(c.db, c.sub, report)
    assert not pending_pages(parsed) and not parsed.warnings
    assert parsed.pages[0]['ocr_status'] == 'MANUALLY_REVIEWED'
    audit = c.db.query(AuditLog).filter_by(action='PARSE_CORRECT', object_id=str(m.id)).one()
    assert audit.detail['ocr_reviewed_pages'] == [1]
    fresh = pipeline.run_check(c.db, c.sub.id, trigger_type='RECHECK', use_llm=False)
    assert not c.db.query(Issue).filter_by(report_id=fresh.id, rule_code='OCR-REVIEW').all()
    assert issue.resolution == 'RESOLVED'


@pytest.mark.parametrize('value', [None, '1', [True], [1.0], ['1'], [0], [9], [1, 1], [2]])
def test_review_confirmation_rejects_invalid_or_nonpending_page(case, as_client, value):
    c = case
    m, v, parsed = _review_case(c, mixed=True)
    before = deepcopy(parsed.pages)
    response = as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'corrected_text': '不应写入', 'ocr_reviewed_pages': value})
    assert response.status_code == 422, response.text
    assert parsed.pages == before and parsed.corrected_text is None


def test_single_page_transcription_clears_review_but_reset_restores_it(case, as_client):
    c = case
    m, v, parsed = _review_case(c)
    client = as_client(c.reviewer)
    for text, pending in [(' \t\n', True), ('对照原图校正的正文', False), (None, True)]:
        response = client.put(f'/api/materials/{m.id}/parsed', json={'version_id': v.id, 'corrected_text': text})
        assert response.status_code == 200, response.text
        assert bool(pending_pages(parsed)) is pending
        assert bool(parsed.warnings) is pending


def test_resaving_mixed_document_does_not_waive_its_empty_page(case, as_client):
    c = case
    m, v, parsed = _review_case(c, mixed=True)
    response = as_client(c.reviewer).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'corrected_text': parsed.full_text})
    assert response.status_code == 200, response.text
    assert pending_pages(parsed)


def test_student_cannot_confirm_ocr_review(case, as_client):
    c = case
    m, v, parsed = _review_case(c)
    response = as_client(c.student).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'ocr_reviewed_pages': [1]})
    assert response.status_code == 403
    assert pending_pages(parsed)


def test_trial_retains_ocr_warning_when_image_quality_rule_is_disabled(case):
    from services.rule_trial import trial_rules
    c = case
    _review_case(c)
    _disable_business_rules(c, f07=True)
    trial = trial_rules(c.db, {'submission_ids': [c.sub.id],
        'overrides': {'check_rules': [{'code': 'R-F07', 'is_active': False}]}}, c.org)['results'][0]
    assert trial['added'] == trial['removed'] == []
    assert trial['current']['summary']['by_severity']['WARN'] >= 1
    assert trial['trial']['summary']['by_severity']['WARN'] >= 1
