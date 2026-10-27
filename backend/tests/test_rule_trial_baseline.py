"""A preview compares two fresh evaluations, never an old saved report."""
from datetime import date

from models import AiReport, ArchiveTimeNode, AuditLog, CheckRule, Issue, RuleVersion, TimeRule
from seed_rules import snapshot_rules
from services.rule_trial import trial_rules
from tests.test_review_regressions import case, test_engine, parsed_material
from utils import now


def setup_time_rule(c):
    parsed_material(c)
    for code, value in [('T01', date(2026, 1, 2)), ('T02', date(2026, 1, 1))]:
        c.add(ArchiveTimeNode, archive_id=c.arch.id, node_code=code, value_date=value, updated_at=now())
    c.add(TimeRule, code='R-TRIAL', name='试运行先后顺序', rule_type='ORDER', severity='BLOCK', applies_stages=[1],
          message_template='核对先后顺序',
          params={'checks': [{'op': 'before', 'a': 'T01', 'b': 'T02'}]},
          is_active=True, sort_order=999, created_at=now(), updated_at=now())
    snapshot_rules(c.db, 'time-rules', 'CREATE', 'preview test', None, c.org.id)
    c.db.flush()


def counts(c):
    return tuple(c.db.query(model).count() for model in (Issue, AiReport, RuleVersion, AuditLog))


def test_unchanged_rules_match_without_report_and_do_not_write(case):
    c = case
    setup_time_rule(c)
    c.sub.latest_report_id = None
    c.db.flush()
    before = counts(c)
    result = trial_rules(c.db, {'submission_ids': [c.sub.id]}, c.org)['results'][0]
    assert result['added'] == result['removed'] == []
    assert result['current'] == result['trial']
    assert result['current']['summary']['by_category']['TIME'] >= 1
    assert counts(c) == before
    assert not c.db.new and not c.db.dirty and not c.db.deleted


def test_override_compares_published_rules_not_stale_report(case):
    c = case
    setup_time_rule(c)
    c.add(Issue, submission_id=c.sub.id, report_id=c.report.id, category='TIME', severity='WARN',
          title='旧报告问题', description='旧材料结论', rule_code='OLD', source='AI_RULE',
          fingerprint='old-report-only', created_at=now(), updated_at=now())
    before = counts(c)
    result = trial_rules(c.db, {'submission_ids': [c.sub.id], 'overrides': {
        'time_rules': [{'code': 'R-TRIAL', 'is_active': False}]}}, c.org)['results'][0]
    assert not result['added']
    assert [i['rule_code'] for i in result['removed_items']] == ['R-TRIAL']
    assert 'old-report-only' not in result['current']['issue_keys']
    assert result['current']['summary']['total'] == result['trial']['summary']['total'] + 1
    assert counts(c) == before
    assert c.db.query(TimeRule).filter_by(code='R-TRIAL').one().is_active


def test_severity_override_is_visible_in_both_summaries(case):
    c = case
    setup_time_rule(c)
    result = trial_rules(c.db, {'submission_ids': [c.sub.id], 'overrides': {
        'time_rules': [{'code': 'R-TRIAL', 'severity': 'WARN'}]}}, c.org)['results'][0]
    assert result['added'] == result['removed'] == []
    current, trial = (result[key]['summary']['by_severity'] for key in ('current', 'trial'))
    assert current['BLOCK'] == trial.get('BLOCK', 0) + 1
    assert trial['WARN'] == current.get('WARN', 0) + 1


def test_similarity_uses_one_candidate_snapshot_for_both_runs(case, monkeypatch):
    from ai import similarity
    c = case
    parsed_material(c)
    rule = c.db.query(CheckRule).filter_by(code='R-C10').one()
    rule.is_active = True
    rule.applies_to = []
    rule.params = {'threshold': 0.8}
    snapshot_rules(c.db, 'check-rules', 'UPDATE', 'similarity preview test', rule.id, c.org.id)
    calls = []

    def candidates(*args):
        calls.append(True)
        return iter([(999, 1999, '原始文本' if len(calls) == 1 else '已经变化的其他文本')])

    monkeypatch.setattr(similarity, 'batch_candidates', candidates)
    result = trial_rules(c.db, {'submission_ids': [c.sub.id]}, c.org)['results'][0]
    assert len(calls) == 1
    assert result['added'] == result['removed'] == []
    assert result['current'] == result['trial']
