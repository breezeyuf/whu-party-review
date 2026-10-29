from datetime import date, timedelta
from types import SimpleNamespace

from ai.extract import extract_nodes
from ai.date_evidence import POLICY_VERSION
import pytest

from models import ParseResult, TimeNodeExtraction, ArchiveTimeNode, AuditLog
from services.timeline import merge_archive_nodes, node_map_for_archive
from tests.test_review_regressions import case, test_engine, parsed_material, as_client
from utils import now


def scan(confidence=.2):
    return [{'page_no': 1, 'source': 'ocr', 'text': '申请日期 2026年9月15日',
             'blocks': [{'text': '申请日期 2026年9月15日', 'bbox': [10, 20, 200, 40], 'conf': confidence}]}]


def test_ocr_date_keeps_recognition_confidence_instead_of_syntax_confidence():
    rows = extract_nodes(scan()[0]['text'], scan(), SimpleNamespace(date_node_map={'signature_date': 'T02'}), [])
    assert rows[0]['value_date'] == date(2026, 9, 15)
    assert rows[0]['confidence'] == .2


def test_low_confidence_date_is_candidate_but_not_rule_input(case):
    m, v = parsed_material(case)
    row = case.add(TimeNodeExtraction, archive_id=case.arch.id, material_id=m.id,
        material_version_id=v.id, node_code='T02', value_date=date(2026, 9, 15),
        confidence=.2, method='RULE', is_current=True, created_at=now())
    merge_archive_nodes(case.db, case.arch.id)
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert row.value_date == date(2026, 9, 15)
    assert nodes['T02']['date'] is None


def pending_source(c, *, confidence=.2, method='RULE', code='T02'):
    m, v = parsed_material(c)
    parsed = c.db.query(ParseResult).filter_by(version_id=v.id).one()
    parsed.pages = scan(confidence)
    row = c.add(TimeNodeExtraction, archive_id=c.arch.id, material_id=m.id, material_version_id=v.id,
        node_code=code, value_date=date(2026, 9, 15), raw_text='2026年9月15日', page_no=1,
        bbox=[10,20,200,40], confidence=confidence, method=method, is_current=True, created_at=now())
    merge_archive_nodes(c.db, c.arch.id)
    return m, v, row


def test_review_warning_runs_even_with_no_enabled_time_rules(case):
    from ai.checks.timeline import run_timeline
    from ai.report import summarize, recommend
    pending_source(case)
    nodes = node_map_for_archive(case.db, case.arch.id)
    snapshot, drafts, results = run_timeline(case.db, case.sub, nodes,
        rule_set=SimpleNamespace(rows=lambda _: []))
    assert snapshot['date_evidence_policy'] == POLICY_VERSION
    assert len(drafts) == 1 and drafts[0].rule_code == 'DATE-REVIEW'
    assert drafts[0].severity == 'WARN' and drafts[0].needs_human_judgement
    assert recommend(summarize(drafts, 1, results), drafts) == 'NEEDS_REVIEW'


def test_unconfirmed_required_date_is_not_described_as_missing(case):
    from ai.checks.timeline import run_timeline
    pending_source(case)
    rule = SimpleNamespace(code='TEST-REQUIRED', name='必填日期', applies_stages=[], severity='BLOCK', basis='',
        message_template='', params={'checks': [{'op': 'required', 'nodes_by_stage': {'1': ['T02']}}]})
    _, drafts, results = run_timeline(case.db, case.sub, node_map_for_archive(case.db, case.arch.id),
        rule_set=SimpleNamespace(rows=lambda _: [rule]))
    assert all(d.rule_code != 'TEST-REQUIRED' for d in drafts)
    assert next(r for r in results if r['rule_code'] == 'TEST-REQUIRED')['result'] == 'SKIPPED'


def test_manual_confirmation_without_changing_date_preserves_evidence(case, as_client):
    m, v, row = pending_source(case)
    client = as_client(case.reviewer)
    before = client.get(f'/api/materials/{m.id}/parsed').json()['data']['extractions'][0]
    assert before['usable'] is False and before['confidence'] == .2
    response = client.put(f'/api/materials/{m.id}/parsed', json={'version_id': v.id,
        'reason': '已逐字对照原图确认', 'extractions': [{'extraction_id': row.id, 'date': '2026-09-15'}]})
    assert response.status_code == 200, response.text
    after = client.get(f'/api/materials/{m.id}/parsed').json()['data']['extractions'][0]
    assert after['usable'] is True and after['method'] == 'MANUAL'
    assert after['date'] == before['date'] and after['raw_text'] == before['raw_text']
    assert node_map_for_archive(case.db, case.arch.id)['T02']['date'] == '2026-09-15'
    audit = case.db.query(AuditLog).filter(AuditLog.action == 'PARSE_CORRECT').order_by(AuditLog.id.desc()).first()
    assert audit.detail['extractions'][0]['before']['method'] == 'RULE'


def test_legacy_report_using_uncertain_date_must_be_rechecked(case):
    from services.workflow import report_is_stale
    m, v, _ = pending_source(case)
    case.report.material_versions = [{'material_id': m.id, 'version_id': v.id}]
    case.report.finished_at = now() + timedelta(seconds=1)
    case.report.timeline_snapshot = {}
    case.db.flush()
    assert report_is_stale(case.db, case.sub, case.report)
    case.report.timeline_snapshot = {'date_evidence_policy': POLICY_VERSION}
    assert not report_is_stale(case.db, case.sub, case.report)


def test_filed_stage_approval_keeps_locked_historical_date(case):
    _, _, row = pending_source(case)
    node = case.db.query(ArchiveTimeNode).filter_by(archive_id=case.arch.id, node_code='T02').one()
    node.locked, node.value_date = True, row.value_date
    case.sub.status = 'FILED'
    case.db.flush()
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T02']['date'] == '2026-09-15'
    assert nodes['T02']['sources'][0]['usable'] is True


@pytest.mark.parametrize('confidence', [.1, .69])
def test_low_confidence_model_date_also_waits_for_confirmation(case, confidence):
    m, v = parsed_material(case)
    case.add(TimeNodeExtraction, archive_id=case.arch.id, material_id=m.id, material_version_id=v.id,
        node_code='T02', value_date=date(2026, 9, 15), confidence=confidence,
        method='LLM', is_current=True, created_at=now())
    merge_archive_nodes(case.db, case.arch.id)
    assert node_map_for_archive(case.db, case.arch.id)['T02']['date'] is None


def test_confident_native_text_and_manual_date_remain_usable(case):
    for code, method in [('T02', 'RULE'), ('T03', 'MANUAL')]:
        m, v = parsed_material(case)
        case.add(TimeNodeExtraction, archive_id=case.arch.id, material_id=m.id, material_version_id=v.id,
            node_code=code, value_date=date(2026, 9, 15), confidence=.9 if method == 'RULE' else 1,
            method=method, is_current=True, created_at=now())
    merge_archive_nodes(case.db, case.arch.id)
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T02']['date'] == nodes['T03']['date'] == '2026-09-15'


def test_pending_vision_review_blocks_only_its_date_region():
    pages = scan(.95)
    pages[0]['vision_reviews'] = [{'status': 'pending', 'bbox': [10,20,200,40]}]
    rows = extract_nodes(pages[0]['text'], pages, SimpleNamespace(date_node_map={'signature_date': 'T02'}), [])
    assert '视觉复核' in rows[0]['invalid_reason']


def test_range_uses_confidence_of_both_endpoints():
    from ai.date_evidence import bound_extractions
    pages = [{'page_no': 1, 'source': 'ocr', 'blocks': [
        {'text': '开始2026年9月15日', 'bbox': [0,0,100,20], 'conf': .2},
        {'text': '结束2026年9月18日', 'bbox': [0,30,100,50], 'conf': .95}]}]
    row = {'node_code': 'T10', 'value_date': date(2026,9,15), 'value_end_date': date(2026,9,18),
           'raw_text': '2026年9月18日', 'page_no': 1, 'bbox': [0,30,100,50], 'confidence': .9, 'method': 'RULE'}
    bound_extractions([row], pages)
    assert row['confidence'] == .2 and '待人工确认日期' in row['invalid_reason']


def test_partial_pending_sequence_is_not_counted_as_a_complete_sequence(case):
    from ai.checks.timeline import run_timeline
    node_map = {'T03': {'date': '2026-01-01'}, 'T06': {'date': '2026-03-01', 'seq': ['2026-03-01'],
        'pending_sources': True}}
    rule = SimpleNamespace(code='TEST-SEQUENCE', name='思想汇报周期', applies_stages=[], severity='BLOCK', basis='',
        message_template='', params={'checks': [{'op': 'seq_period_count', 'seq': 'T06[*]', 'from': 'T03',
                                               'to': '$today', 'period_months': 3}]})
    _, _, results = run_timeline(case.db, case.sub, node_map, rule_set=SimpleNamespace(rows=lambda _: [rule]))
    assert results[0]['result'] == 'SKIPPED' and '待人工确认' in results[0]['reason']


def test_rule_trial_cannot_disable_date_review_and_does_not_write_issues(case, as_client):
    from models import TimeRule, Issue
    pending_source(case)
    before = case.db.query(Issue).count()
    overrides = [{'code': rule.code, 'is_active': False} for rule in case.db.query(TimeRule).all()]
    response = as_client(case.org).post('/api/rules/dry-run', json={
        'submission_ids': [case.sub.id], 'overrides': {'time_rules': overrides}})
    assert response.status_code == 200, response.text
    trial = response.json()['data']['results'][0]['trial']
    assert trial['summary']['by_category']['TIME'] == 1
    assert case.db.query(Issue).count() == before


def test_retry_preserves_manual_date_confirmation(case, as_client, monkeypatch):
    from ai import pipeline
    m, v, row = pending_source(case)
    response = as_client(case.reviewer).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'reason': '对照原图确认',
        'extractions': [{'extraction_id': row.id, 'date': '2026-09-15'}]})
    assert response.status_code == 200
    result = {'parser': 'OCR', 'ocr_engine': 'rapidocr', 'full_text': scan()[0]['text'],
              'pages': scan(), 'page_count': 1, 'warnings': []}
    monkeypatch.setattr(pipeline, 'parse_version_file', lambda *args: result)
    pipeline.parse_version(case.db, v.id, use_llm=False)
    assert row.is_current and row.method == 'MANUAL' and row.confidence == 1
    assert node_map_for_archive(case.db, case.arch.id)['T02']['date'] == '2026-09-15'


def test_legacy_syntactic_confidence_does_not_override_low_confidence_ocr(case):
    m, v = parsed_material(case)
    parsed = case.db.query(ParseResult).filter_by(version_id=v.id).one()
    parsed.pages = scan()
    case.add(TimeNodeExtraction, archive_id=case.arch.id, material_id=m.id,
        material_version_id=v.id, node_code='T02', value_date=date(2026, 9, 15), raw_text='2026年9月15日',
        page_no=1, bbox=[10,20,200,40], confidence=.9, method='RULE', is_current=True, created_at=now())
    merge_archive_nodes(case.db, case.arch.id)
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T02']['date'] is None


def legacy_training_range(c):
    m, v = parsed_material(c)
    parsed = c.db.query(ParseResult).filter_by(version_id=v.id).one()
    text = '出生日期2000年1月1日\n培训时间2026年9月15日至2026年9月18日\n落款2026年9月20日'
    parsed.pages = [{'page_no': 1, 'source': 'text', 'text': text, 'blocks': [{'text': text}]}]
    row = c.add(TimeNodeExtraction, archive_id=c.arch.id, material_id=m.id, material_version_id=v.id,
        node_code='T10', value_date=date(2000, 1, 1), value_end_date=date(2026, 9, 20), hours=24,
        raw_text='2026年9月20日', page_no=1, confidence=.9, method='RULE', is_current=True, created_at=now())
    merge_archive_nodes(c.db, c.arch.id)
    return m, v, row


def test_legacy_document_wide_range_is_excluded_and_previous_report_is_stale(case):
    from services.workflow import report_is_stale
    m, v, row = legacy_training_range(case)
    assert row.value_date == date(2000, 1, 1)  # Keep original evidence.
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T10']['date'] is None and nodes['T10']['hours'] is None
    assert nodes['T10']['sources'][0]['usable'] is False
    case.report.material_versions = [{'material_id': m.id, 'version_id': v.id}]
    case.report.finished_at = now() + timedelta(seconds=1)
    case.report.timeline_snapshot = {'date_evidence_policy': 1}
    case.db.flush()
    assert report_is_stale(case.db, case.sub, case.report)


def test_correcting_legacy_training_period_restores_only_confirmed_range(case, as_client):
    m, v, row = legacy_training_range(case)
    response = as_client(case.reviewer).put(f'/api/materials/{m.id}/parsed', json={
        'version_id': v.id, 'reason': '原图明确记载培训起止，出生和落款不属于培训期间',
        'extractions': [{'extraction_id': row.id, 'date': '2026-09-15', 'end_date': '2026-09-18', 'hours': 24}]})
    assert response.status_code == 200, response.text
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T10']['date'] == '2026-09-15' and nodes['T10']['end_date'] == '2026-09-18'
    assert nodes['T10']['hours'] == 24
    assert row.raw_text == '2026年9月20日' and row.method == 'MANUAL'


def test_filed_legacy_range_remains_historical_evidence(case):
    _, _, row = legacy_training_range(case)
    node = case.db.query(ArchiveTimeNode).filter_by(archive_id=case.arch.id, node_code='T10').one()
    node.locked, node.value_date, node.value_end_date = True, row.value_date, row.value_end_date
    case.sub.status = 'FILED'
    case.db.flush()
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T10']['date'] == '2000-01-01' and nodes['T10']['sources'][0]['usable'] is True
