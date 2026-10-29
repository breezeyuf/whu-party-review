from datetime import timedelta
from io import BytesIO
from pathlib import Path

import pytest

from models import Notice, Job, UserRole, ExportFile
from services.rules import export_kind, validate_record
from services.completion_batch import run_notice_batch
from tests.test_review_regressions import case, test_engine, as_client, pair, parsed_material
from utils import now


def test_seeded_time_rules_round_trip(case, as_client):
    buffer = BytesIO()
    export_kind(case.db, 'time-rules').save(buffer)
    client = as_client(case.org)
    for dry in ('true', 'false'):
        response = client.post('/api/rules/time-rules/import', files={'file': ('rules.xlsx', buffer.getvalue())}, data={'mode': 'upsert', 'dry_run': dry})
        assert response.status_code == 200, response.text
        assert response.json()['data']['errors'] == []
        assert response.json()['data']['updated'] == 23


@pytest.mark.parametrize('stages', [[True], [0], [6], ['1'], [1.5]])
def test_invalid_stage_arrays_rejected(stages):
    assert validate_record('time-rules', {'applies_stages': stages})


def test_unassign_batch_synchronizes_active_package(case, as_client):
    pair(case)
    m, _ = parsed_material(case)
    response = as_client(case.org).put(f'/api/archives/{case.arch.id}', json={'batch_id': None})
    assert response.status_code == 200
    case.db.refresh(case.sub)
    assert case.sub.batch_id is None
    client = as_client(case.cross)
    assert client.get(f'/api/submissions/{case.sub.id}').status_code == 404
    assert client.get(f'/api/materials/{m.id}/parsed').status_code == 404


def test_legacy_anonymous_data_migration_is_repeatable(case):
    c = case
    c.arch.anon_code = 'A' + c.arch.student_no
    note = c.add(Notice, notice_type='RECTIFICATION', archive_id=c.arch.id, submission_id=c.sub.id,
        student_user_id=c.student.id, title='保持正文', content={'student': {'student_no': c.arch.student_no, 'anon_code': c.arch.anon_code}, 'note': '保持正文'},
        status='SENT', created_by=c.reviewer.id, created_at=now(), updated_at=now())
    export = c.add(ExportFile, export_type='DESENSITIZED_DATA', file_name='old.xlsx', stored_path='exports/old.xlsx',
        created_by=c.org.id, created_at=now(), expires_at=now() + timedelta(days=7))
    c.db.flush()
    sql = (Path(__file__).parents[1] / 'migrations/sql/0005_anonymous_identifiers.sql').read_text(encoding='utf-8')
    c.db.connection().exec_driver_sql(sql)
    c.db.refresh(c.arch); c.db.refresh(note); c.db.refresh(export)
    anonymous = c.arch.anon_code
    assert c.arch.student_no not in anonymous
    assert note.content['student']['anon_code'] == anonymous
    assert note.content['note'] == '保持正文'
    assert export.expires_at <= now()
    c.db.connection().exec_driver_sql(sql)
    c.db.refresh(c.arch)
    assert c.arch.anon_code == anonymous


def test_background_completion_creates_notices_and_progress(case, as_client):
    c = case
    response = as_client(c.reviewer).post('/api/submissions/completion-notices', json={'submission_ids': [c.sub.id, c.sub.id], 'send': False, 'background': True})
    assert response.status_code == 200, response.text
    job = c.db.get(Job, response.json()['data']['job_id'])
    assert job.total == 1
    result = run_notice_batch(c.db, job)
    assert len(result['created']) == 1
    notice = c.db.get(Notice, result['created'][0]['notice_id'])
    assert notice.status == 'DRAFT'
    assert job.done_count == job.total == 1


def test_queued_notice_rechecks_revoked_role(case, as_client):
    response = as_client(case.reviewer).post('/api/submissions/completion-notices', json={'submission_ids': [case.sub.id], 'background': True})
    job = case.db.get(Job, response.json()['data']['job_id'])
    case.db.query(UserRole).filter_by(user_id=case.reviewer.id).delete()
    from errors import AppError
    with pytest.raises(AppError):
        run_notice_batch(case.db, job)
    assert case.db.query(Notice).count() == 0


def test_batch_failure_does_not_leave_partial_notices(case, as_client, monkeypatch):
    from services import completion_batch
    response = as_client(case.reviewer).post('/api/submissions/completion-notices', json={'submission_ids': [case.sub.id], 'background': True})
    job = case.db.get(Job, response.json()['data']['job_id'])
    original = completion_batch.create_completion_notice
    def fail(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError('interrupted')
    monkeypatch.setattr(completion_batch, 'create_completion_notice', fail)
    with pytest.raises(RuntimeError):
        run_notice_batch(case.db, job)
    assert case.db.query(Notice).count() == 0
