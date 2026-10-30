from datetime import date
from types import SimpleNamespace as N

import pytest

from ai.extract import extract_nodes


def node(code, sources, keywords, kind='DATE'):
    return N(code=code, name=code, value_kind=kind, source_material_codes=sources,
             extract_keywords=keywords, has_hours=False)


def material(code, mapping=None):
    return N(code=code, date_node_map=mapping or {})


def test_early_talk_cannot_create_later_committee_talk_date():
    defs = [node('T03', ['PARTY_TALK_RECORD'], ['谈话']), node('T15', ['COMMITTEE_TALK_RECORD'], ['谈话'])]
    rows = extract_nodes('谈话日期：2026年9月15日', [], material('PARTY_TALK_RECORD', {'signature_date': 'T03'}), defs)
    assert {row['node_code'] for row in rows} == {'T03'}


def test_candidate_publicity_cannot_create_regularization_publicity():
    defs = [node('T11', ['CANDIDATE_PUBLICITY'], ['公示'], 'DATE_RANGE'),
            node('T19', ['REGULARIZATION_PUBLICITY'], ['公示'], 'DATE_RANGE')]
    rows = extract_nodes('公示时间：2026年9月15日至2026年9月22日', [], material('CANDIDATE_PUBLICITY', {'field:公示起': 'T11'}), defs)
    assert {row['node_code'] for row in rows} == {'T11'}


def test_training_document_does_not_supply_birth_node_from_nearby_dates():
    defs = [node('T01', ['AUTOBIOGRAPHY'], ['出生日期']), node('T10', ['TRAINING_CERT'], ['培训'], 'DATE_RANGE')]
    rows = extract_nodes('出生日期2000年1月1日\n培训2026年9月15日至2026年9月18日', [], material('TRAINING_CERT'), defs)
    assert {row['node_code'] for row in rows} == {'T10'}


@pytest.mark.parametrize('raw', ['2003年5月12日', '二〇〇三年五月十二日', '２００３年５月１２日'])
def test_mapped_birth_date_keeps_original_ocr_evidence(raw):
    text = '出生日期：' + raw
    pages = [{'page_no': 1, 'source': 'ocr', 'text': text,
              'blocks': [{'text': text, 'bbox': [10,20,200,40], 'conf': .93}]}]
    rows = extract_nodes(text, pages, material('AUTOBIOGRAPHY', {'field:出生日期': 'T01'}),
                         [node('T01', ['AUTOBIOGRAPHY'], ['出生日期'])])
    assert rows[0]['value_date'] == date(2003, 5, 12)
    assert rows[0]['raw_text'] == raw and rows[0]['bbox'] == [10,20,200,40]
    assert not rows[0]['invalid_reason'] and rows[0]['confidence'] >= .7


def test_specific_material_mapping_overrides_general_source_list():
    from types import MappingProxyType
    mt = material('CUSTOM', MappingProxyType({'signature_date': 'T03'}))
    rows = extract_nodes('谈话日期：2026年9月15日', [], mt,
                         [node('T03', ('PARTY_TALK_RECORD',), ['谈话'])])
    assert len(rows) == 1 and not rows[0]['invalid_reason']


def test_keyword_date_keeps_fullwidth_ocr_evidence():
    text = '谈话日期：２０２６年９月１５日'
    pages = [{'page_no': 1, 'source': 'ocr', 'text': text,
              'blocks': [{'text': text, 'bbox': [10, 20, 200, 40], 'conf': .93}]}]
    rows = extract_nodes(text, pages, material('PARTY_TALK_RECORD'),
                         [node('T03', ['PARTY_TALK_RECORD'], ['谈话'])])
    assert rows[0]['value_date'] == date(2026, 9, 15)
    assert rows[0]['raw_text'] == '２０２６年９月１５日' and rows[0]['bbox'] == [10, 20, 200, 40]
    assert not rows[0]['invalid_reason']


def test_unrestricted_custom_nodes_still_extract():
    rows = extract_nodes('谈话日期：2026年9月15日', [], material('CUSTOM'),
                         [node('T90', [], ['谈话'])])
    assert len(rows) == 1 and not rows[0]['invalid_reason']


def test_unknown_material_keeps_candidate_for_manual_review():
    rows = extract_nodes('谈话日期：2026年9月15日', [], None,
                         [node('T03', ['PARTY_TALK_RECORD'], ['谈话'])])
    assert rows[0]['value_date'] == date(2026, 9, 15)
    assert '材料类型未明确' in rows[0]['invalid_reason']


def test_model_receives_only_eligible_nodes_and_cannot_supply_wrong_source(monkeypatch):
    from ai import enrichment
    seen = {}

    def answer(db, purpose, params, **kwargs):
        seen.update(params)
        return {'dates': [dict(node_code=code, date='2026-09-15', raw_text='2026年9月15日', confidence=.95)
                          for code in ['T03', 'T15']]}, None, None

    monkeypatch.setattr(enrichment, 'chat_json', answer)
    defs = [node('T03', ['PARTY_TALK_RECORD'], []), node('T15', ['COMMITTEE_TALK_RECORD'], [])]
    rows, error = enrichment.extract_fallback(None, '2026年9月15日', [], [], defs,
                                              material_type=material('PARTY_TALK_RECORD'))
    assert not error and 'T03' in seen['nodes'] and 'T15' not in seen['nodes']
    assert [row['node_code'] for row in rows] == ['T03']


def test_model_unknown_source_is_pending_and_manual_values_are_preserved(monkeypatch):
    from ai import enrichment
    monkeypatch.setattr(enrichment, 'chat_json', lambda *a, **kw: ({'dates': [
        dict(node_code='T03', date='2026-09-15', raw_text='2026年9月15日', confidence=.95)]}, None, None))
    rows, _ = enrichment.extract_fallback(None, '2026年9月15日', [], [],
                                          [node('T03', ['PARTY_TALK_RECORD'], [])])
    assert '材料类型未明确' in rows[0]['invalid_reason']
    from ai.node_sources import bound_sources
    manual = dict(rows[0], method='MANUAL', invalid_reason=None)
    assert bound_sources([manual], [node('T03', ['PARTY_TALK_RECORD'], [])], None)[0] == manual
