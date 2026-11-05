from datetime import date
from types import SimpleNamespace
import pytest

from ai.extract import extract_nodes
from ai.date_evidence import evidence_state


def ranges(text, *, code='T10', pages=None, mapped=True):
    definition = SimpleNamespace(code=code, value_kind='DATE_RANGE', has_hours=code == 'T10',
        extract_keywords=['培训', '学时', '结业'] if code == 'T10' else ['公示'])
    mapping = {'field:培训起': code, 'field:学时': code} if mapped else {}
    return [row for row in extract_nodes(text, pages or [], SimpleNamespace(date_node_map=mapping), [definition])
            if row['node_code'] == code]


def test_training_range_excludes_birth_and_certificate_dates():
    text = '出生日期：2000年1月1日\n培训时间：2026年9月15日至2026年9月18日，共24学时\n落款：2026年9月20日'
    rows = ranges(text)
    assert len(rows) == 1
    assert (rows[0]['value_date'], rows[0]['value_end_date']) == (date(2026, 9, 15), date(2026, 9, 18))
    assert rows[0]['hours'] == 24
    assert '2026年9月15日' in rows[0]['raw_text'] and '2026年9月18日' in rows[0]['raw_text']
    assert not rows[0]['invalid_reason']


def test_reversed_range_remains_reversed_and_invalid():
    row = ranges('培训时间：2026年9月18日至2026年9月15日')[0]
    assert (row['value_date'], row['value_end_date']) == (date(2026, 9, 18), date(2026, 9, 15))
    assert '早于' in row['invalid_reason']


def test_unconnected_dates_are_not_fabricated_into_a_range():
    rows = ranges('培训报名日期：2026年9月1日\n结业证发证日期：2026年9月20日')
    assert rows and all(row['value_end_date'] is None for row in rows)
    assert all(not evidence_state(row)[0] for row in rows)


def test_multiple_training_periods_require_review_instead_of_combining():
    rows = ranges('第一期培训：2026年9月1日至2026年9月3日\n第二期培训：2026年9月20日至2026年9月22日')
    assert {(row['value_date'], row['value_end_date']) for row in rows} == {
        (date(2026, 9, 1), date(2026, 9, 3)), (date(2026, 9, 20), date(2026, 9, 22))}
    assert all(not evidence_state(row)[0] for row in rows)


def test_publicity_uses_its_own_range_and_not_training_dates():
    rows = ranges('培训时间：2026年8月1日至2026年8月3日\n公示时间：2026年9月15日至2026年9月22日', code='T11')
    assert len(rows) == 1
    assert (rows[0]['value_date'], rows[0]['value_end_date']) == (date(2026, 9, 15), date(2026, 9, 22))


@pytest.mark.parametrize('text', [
    '培训时间：2026年9月15日至18日',
    '培训时间：2026年9月15日至9月18日',
    '培训时间：２０２６年９月１５日至２０２６年９月１８日',
    '培训时间：2026-09-15 — 2026-09-18',
    '培训时间：2026/09/15～2026/09/18',
    '培训时间：二〇二六年九月十五日至二〇二六年九月十八日',
    '培训开始日期：2026年9月15日\n结束日期：2026年9月18日',
    '培训时间\n2026年9月15日至2026年9月18日',
])
def test_explicit_range_formats(text):
    row = ranges(text)[0]
    assert (row['value_date'], row['value_end_date']) == (date(2026, 9, 15), date(2026, 9, 18))
    assert not row['invalid_reason']


def test_abbreviated_cross_year_is_not_silently_assigned_a_year():
    row = ranges('培训时间：2026年12月30日至1月3日')[0]
    assert not evidence_state(row)[0]
    assert '跨年' in row['invalid_reason']


def test_invalid_endpoint_is_retained_for_correction():
    row = ranges('培训时间：2026年2月25日至2026年2月30日')[0]
    assert row['value_end_date'] is None
    assert row['invalid_reason']
    assert '2026年2月30日' in row['raw_text']


def test_unrelated_material_does_not_gain_a_training_range():
    assert ranges('出生日期：2000年1月1日\n入学时间：2019年9月1日至2023年6月30日', mapped=False) == []


def test_repeated_identical_period_is_one_record():
    row = '培训时间：2026年9月15日至2026年9月18日'
    assert len(ranges(row + '\n' + row)) == 1


def test_certificate_validity_is_not_automatically_training_period():
    rows = ranges('有效期：2026年1月1日至2027年1月1日')
    assert all(not evidence_state(row)[0] for row in rows)


def test_low_confidence_ocr_end_is_not_hidden_by_confident_start():
    text = '培训时间：2026年9月15日至2026年9月18日'
    pages = [{'page_no': 1, 'source': 'ocr', 'text': text, 'blocks': [
        {'text': '培训时间：2026年9月15日', 'bbox': [0,0,100,20], 'conf': .95},
        {'text': '至2026年9月18日', 'bbox': [0,30,100,50], 'conf': .2}]}]
    row = ranges(text, pages=pages)[0]
    assert row['confidence'] == .2 and not evidence_state(row, pages)[0]


def test_end_region_pending_visual_review_is_checked_on_another_page():
    text = '培训时间：2026年9月15日\n至2026年9月18日'
    pages = [
        {'page_no': 1, 'source': 'ocr', 'text': text.splitlines()[0],
         'blocks': [{'text': text.splitlines()[0], 'bbox': [0,0,100,20], 'conf': .95}]},
        {'page_no': 2, 'source': 'ocr', 'text': text.splitlines()[1],
         'blocks': [{'text': text.splitlines()[1], 'bbox': [0,100,100,120], 'conf': .95}],
         'vision_reviews': [{'status': 'pending', 'bbox': [0,100,100,120]}]},
    ]
    row = ranges(text, pages=pages)[0]
    assert not evidence_state(row, pages)[0]
    assert '视觉复核' in row['invalid_reason']


def test_model_single_date_cannot_complete_a_range(monkeypatch):
    from ai import enrichment
    monkeypatch.setattr(enrichment, 'chat_json', lambda *args, **kwargs: ({'dates': [
        {'node_code': 'T10', 'date': '2026-09-15', 'raw_text': '2026年9月15日', 'confidence': .95}]}, None, None))
    nodes = [SimpleNamespace(code='T10', name='培训起止', value_kind='DATE_RANGE')]
    rows, error = enrichment.extract_fallback(None, '培训2026年9月15日', [], [], nodes)
    assert not error and rows[0]['value_date'] == date(2026, 9, 15)
    assert not evidence_state(rows[0])[0]
