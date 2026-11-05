from datetime import date, timedelta
from types import SimpleNamespace as N

import pytest

from ai.date_evidence import states_for
from models import MaterialType, TimeNodeDef, TimeNodeExtraction, ArchiveTimeNode, Job
from services.timeline import merge_archive_nodes, node_map_for_archive
from tests.test_review_regressions import case, test_engine, parsed_material, as_client
from utils import now


def talk_source(c, method='RULE', material_code='PARTY_TALK_RECORD'):
    m, v = parsed_material(c)
    m.type_id = c.db.query(MaterialType).filter_by(code=material_code).one().id
    m.type_status = 'CONFIRMED'
    row = c.add(TimeNodeExtraction, archive_id=c.arch.id, material_id=m.id, material_version_id=v.id,
        node_code='T03', value_date=date(2026, 9, 15), confidence=.95, method=method,
        raw_text='2026年9月15日', is_current=True, created_at=now())
    merge_archive_nodes(c.db, c.arch.id)
    return m, v, row


@pytest.mark.parametrize('method', ['RULE', 'LLM'])
def test_old_wrong_source_is_removed_from_effective_timeline_and_report(case, method):
    from services.workflow import report_is_stale
    m, v, row = talk_source(case, method)
    assert node_map_for_archive(case.db, case.arch.id)['T03']['date'] == '2026-09-15'
    m.type_id = case.db.query(MaterialType).filter_by(code='COMMITTEE_TALK_RECORD').one().id
    case.db.flush()
    # Even before a reparse or merge, stale stored aggregates cannot be reused.
    nodes = node_map_for_archive(case.db, case.arch.id)
    assert nodes['T03']['date'] is None and not nodes['T03']['sources'][0]['usable']
    assert row.value_date == date(2026, 9, 15)
    case.report.material_versions = [{'material_id': m.id, 'version_id': v.id}]
    case.report.finished_at = now() + timedelta(seconds=1)
    case.report.timeline_snapshot = {'date_evidence_policy': 2}
    case.db.flush()
    assert report_is_stale(case.db, case.sub, case.report)
    merge_archive_nodes(case.db, case.arch.id)
    stored = case.db.query(ArchiveTimeNode).filter_by(archive_id=case.arch.id, node_code='T03').one()
    assert stored.value_date is None


def test_source_mismatch_does_not_erase_manual_or_filed_locked_dates(case):
    m, v, row = talk_source(case, material_code='COMMITTEE_TALK_RECORD')
    row.method = 'MANUAL'
    merge_archive_nodes(case.db, case.arch.id)
    assert node_map_for_archive(case.db, case.arch.id)['T03']['date'] == '2026-09-15'
    row.method = 'RULE'
    stored = case.db.query(ArchiveTimeNode).filter_by(archive_id=case.arch.id, node_code='T03').one()
    stored.locked = True
    case.sub.status = 'FILED'
    case.db.flush()
    mapped = node_map_for_archive(case.db, case.arch.id)['T03']
    assert mapped['date'] == '2026-09-15' and mapped['sources'][0]['usable']


def test_source_check_uses_pinned_types_and_definitions_without_live_rule_query(case):
    _, _, row = talk_source(case)

    class PinnedSession:
        def query(self, entity):
            assert entity is not TimeNodeDef and entity is not MaterialType
            return case.db.query(entity)

    defs = [N(code='T03', source_material_codes=('PINNED',))]
    type_id = case.db.query(MaterialType).filter_by(code='PARTY_TALK_RECORD').one().id
    db = PinnedSession()
    assert states_for(db, [row], node_defs=defs, material_types={type_id: N(code='PINNED', date_node_map={})})[row.id][0]
    assert not states_for(db, [row], node_defs=defs, material_types={})[row.id][0]
    assert not states_for(db, [row], node_defs=defs, material_types={type_id: N(code='OTHER', date_node_map={})})[row.id][0]


def test_reclassification_queues_parse_and_refreshes_nodes_preserving_manual(case, as_client, monkeypatch):
    from ai import pipeline
    m, v, row = talk_source(case)
    manual = case.add(TimeNodeExtraction, archive_id=case.arch.id, material_id=m.id, material_version_id=v.id,
        node_code='T01', value_date=date(2003, 5, 12), confidence=1, method='MANUAL',
        is_current=True, created_at=now())
    new_type = case.db.query(MaterialType).filter_by(code='COMMITTEE_TALK_RECORD').one()
    client = as_client(case.reviewer)
    response = client.put(f'/api/materials/{m.id}/type', json={'material_type_id': new_type.id})
    assert response.status_code == 200, response.text
    data = response.json()['data']
    assert data['parse_job_id'] and data['current_version']['parse_status'] == 'PENDING'
    assert node_map_for_archive(case.db, case.arch.id)['T03']['date'] is None
    again = client.put(f'/api/materials/{m.id}/type', json={'material_type_id': new_type.id})
    assert again.status_code == 200
    assert case.db.query(Job).filter_by(job_type='PARSE', target_id=v.id).count() == 1
    monkeypatch.setattr(pipeline, 'parse_version_file', lambda *a: {
        'parser': 'PDF_TEXT', 'full_text': '谈话日期：2026年9月15日', 'pages': [], 'page_count': 1})
    pipeline.parse_version(case.db, v.id, use_llm=False)
    mapped = node_map_for_archive(case.db, case.arch.id)
    assert mapped['T15']['date'] == '2026-09-15' and mapped['T03']['date'] is None
    assert manual.is_current and manual.method == 'MANUAL' and mapped['T01']['date'] == '2003-05-12'


def test_reclassification_reuses_queued_parse(case, as_client):
    from services.materials import enqueue_job
    m, v, _ = talk_source(case)
    job = enqueue_job(case.db, 'PARSE', case.reviewer.id, 'material_version', v.id, {'version_id': v.id})
    v.parse_status = 'PENDING'
    new_type = case.db.query(MaterialType).filter_by(code='COMMITTEE_TALK_RECORD').one()
    response = as_client(case.reviewer).put(f'/api/materials/{m.id}/type', json={'material_type_id': new_type.id})
    assert response.status_code == 200 and response.json()['data']['parse_job_id'] == job.id
    assert case.db.query(Job).filter_by(job_type='PARSE', target_id=v.id).count() == 1
