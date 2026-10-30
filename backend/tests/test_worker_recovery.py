"""Crash recovery and attempt fencing against a disposable PostgreSQL schema."""
from datetime import timedelta
import threading
import time
from types import SimpleNamespace

import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from models import Job
from tests.pg_fixtures import make_schema_engine
from utils import now
import worker


@pytest.fixture(scope="module")
def recovery_schema():
    schema = make_schema_engine("worker_recovery")
    try:
        yield schema
    finally:
        schema.drop()


@pytest.fixture
def sessions(recovery_schema, monkeypatch):
    factory = sessionmaker(bind=recovery_schema.engine, expire_on_commit=False, autoflush=False)
    monkeypatch.setattr(worker, "SessionLocal", factory)
    yield factory
    with factory() as db:
        db.query(Job).delete(synchronize_session=False)
        db.commit()


def add_job(sessions, **values):
    values = {"job_type": "NOTICE_BATCH", "status": "QUEUED", "created_at": now(), **values}
    with sessions() as db:
        job = Job(**values)
        db.add(job)
        db.commit()
        return job.id


def recover(sessions, timeout=300):
    with sessions() as db:
        count = worker._recover(db, timeout)
        db.commit()
        return count


def test_periodic_recovery_handles_orphan_not_yet_stale_at_restart(sessions, monkeypatch):
    current = now()
    from ai import pipeline
    monkeypatch.setattr(pipeline, "parse_version", lambda *_args: None)
    jid = add_job(sessions, job_type="PARSE", target_id=1, status="RUNNING", attempts=1, started_at=current, heartbeat_at=current)
    monkeypatch.setattr(worker, "now", lambda: current)
    monkeypatch.setattr(worker, "get_setting", lambda *_args: {"heartbeat_timeout_s": 300})
    observed = []

    class TwoScans:
        def is_set(self):
            return len(observed) == 2

        def wait(self, delay):
            nonlocal current
            assert 0 < delay <= 30
            with sessions() as db:
                observed.append(db.get(Job, jid).status)
            current += timedelta(seconds=301)

    monkeypatch.setattr(worker, "_stop", TwoScans())
    # NOTICE_BATCH 现在会真正生成批量通知并核验发起人，这里只验证恢复与领取代次，
    # 否则缺少发起人权限会让任务回到 QUEUED，掩盖本用例要检查的状态迁移。
    from services import completion_batch
    monkeypatch.setattr(completion_batch, "run_notice_batch", lambda _db, _job: {"ok": True})
    worker._recovery_loop()
    assert observed == ["RUNNING", "QUEUED"]
    with sessions() as db:
        job = worker._claim(db)
        assert job.id == jid and job.attempts == 2
        worker._run_claimed(db, job)
        db.commit()
    with sessions() as db:
        assert db.get(Job, jid).status == "SUCCEEDED"


def test_active_handler_survives_missed_heartbeat_and_allows_pulse(sessions, monkeypatch):
    from ai import pipeline

    jid = add_job(sessions, job_type="PARSE", target_id=1)
    entered, release = threading.Event(), threading.Event()
    errors, attempts = [], []

    def slow_parse(db, _version_id):
        entered.set()
        assert release.wait(8)

    monkeypatch.setattr(pipeline, "parse_version", slow_parse)
    real_pulse = worker._pulse
    monkeypatch.setattr(worker, "_pulse", lambda _id, stopped, **_kw: stopped.wait(8))

    def execute():
        try:
            with sessions() as db:
                job = worker._claim(db)
                attempts.append(job._worker_attempt)
                job.heartbeat_at = now() - timedelta(minutes=10)
                db.commit()
                worker._run_claimed(db, job)
                db.commit()
        except BaseException as exc:
            errors.append(exc)

    running = threading.Thread(target=execute)
    running.start()
    try:
        assert entered.wait(5)
        assert recover(sessions) == 0
        with sessions() as db:
            assert worker._claim(db) is None
            assert db.get(Job, jid).attempts == 1
        stopped = threading.Event()
        pulse = threading.Thread(target=real_pulse, args=(jid, stopped, 0.01), kwargs={"attempt": attempts[0]})
        pulse.start()
        try:
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                with sessions() as db:
                    if db.get(Job, jid).heartbeat_at > now() - timedelta(seconds=5):
                        break
                time.sleep(0.01)
            else:
                pytest.fail("Heartbeat was blocked by the active handler")
        finally:
            stopped.set()
            pulse.join(2)
    finally:
        release.set()
        running.join(5)
    assert not running.is_alive() and not errors
    with sessions() as db:
        assert db.get(Job, jid).status == "SUCCEEDED"


def test_claim_abandoned_before_execution_cannot_run_again(sessions, monkeypatch):
    add_job(sessions)
    with sessions() as old_db:
        old = worker._claim(old_db)
        old.heartbeat_at = now() - timedelta(minutes=10)
        old_db.commit()
        assert recover(sessions) == 1
        with sessions() as new_db:
            replacement = worker._claim(new_db)
            assert replacement.attempts == 2
        called = []
        monkeypatch.setattr(worker, "_run", lambda *_args: called.append(True))
        worker._run_claimed(old_db, old)
        assert not called


@pytest.mark.parametrize("late_result", ["success", "failure"])
def test_old_attempt_cannot_write_after_rollback_and_manual_retry(sessions, monkeypatch, late_result):
    from ai import pipeline

    jid = add_job(sessions, job_type="PARSE", target_id=1)
    tokens = []

    def superseded_parse(db, _version_id):
        db.rollback()
        with sessions() as other:
            old = other.get(Job, jid)
            old.status = "QUEUED"
            old.attempts = 0
            other.commit()
            new = worker._claim(other)
            tokens.append(new._worker_attempt)
            worker._ok(other, new, {"owner": "replacement"})
            other.commit()
        db.add(Job(job_type="NOTICE_BATCH", status="QUEUED", created_at=now()))
        if late_result == "failure":
            raise RuntimeError("old attempt returned an error")

    monkeypatch.setattr(pipeline, "parse_version", superseded_parse)
    with sessions() as db:
        old = worker._claim(db)
        old_token = old._worker_attempt
        worker._run_claimed(db, old)
        db.commit()
    assert old_token[1] == tokens[0][1] == 1
    assert old_token[2] != tokens[0][2]
    with sessions() as db:
        job = db.get(Job, jid)
        assert job.status == "SUCCEEDED" and job.result == {"owner": "replacement"}
        assert job.error is None and db.query(Job).count() == 1


def test_old_pulse_does_not_extend_replacement_lease(sessions):
    jid = add_job(sessions)
    with sessions() as db:
        old = worker._claim(db)
        token = old._worker_attempt
        old.status = "QUEUED"
        db.commit()
        newer = worker._claim(db)
        baseline = newer.heartbeat_at
    stopped = threading.Event()
    pulse = threading.Thread(target=worker._pulse, args=(jid, stopped, 0.01), kwargs={"attempt": token})
    pulse.start()
    pulse.join(3)
    stopped.set()
    assert not pulse.is_alive()
    with sessions() as db:
        assert db.get(Job, jid).heartbeat_at == baseline


def test_exhausted_orphan_fails_and_finishes_batch_once(sessions, monkeypatch):
    stale = now() - timedelta(minutes=10)
    parent = add_job(sessions, job_type="BATCH_AI_CHECK", status="RUNNING", attempts=3, heartbeat_at=stale)
    child = add_job(sessions, job_type="AI_CHECK", parent_id=parent, status="RUNNING", attempts=3, heartbeat_at=stale)
    add_job(sessions, job_type="AI_CHECK", parent_id=parent, status="SUCCEEDED")
    notified = []
    monkeypatch.setattr(worker, "_notify_done", lambda _db, job: notified.append((job.id, job.status)))
    assert recover(sessions) == 2
    assert recover(sessions) == 0
    with sessions() as db:
        assert db.get(Job, child).status == "FAILED"
        assert db.get(Job, child).attempts == 3
        p = db.get(Job, parent)
        assert (p.status, p.done_count, p.failed_count, p.progress) == ("PARTIAL", 2, 1, 100)
        assert p.result == {"total": 2, "failed": 1}
    assert notified == [(child, "FAILED"), (parent, "PARTIAL")]


def test_waiting_parent_does_not_retry_or_split_again(sessions):
    parent = add_job(sessions, job_type="BATCH_AI_CHECK", params={"submission_ids": [11, 12]})
    with sessions() as db:
        job = worker._claim(db)
        worker._run_claimed(db, job)
        db.commit()
    for _ in range(4):
        with sessions() as db:
            p = db.get(Job, parent)
            p.heartbeat_at = now() - timedelta(minutes=10)
            db.commit()
        assert recover(sessions) == 1
        with sessions() as db:
            p = db.get(Job, parent)
            assert p.status == "RUNNING" and p.attempts == 1
            assert p.stage_text == "等待子任务完成"
            assert db.query(Job).filter(Job.parent_id == parent).count() == 2


def test_recovery_workers_skip_rows_already_owned_by_another_recovery(sessions):
    stale = now() - timedelta(minutes=10)
    first = add_job(sessions, status="RUNNING", attempts=1, heartbeat_at=stale)
    second = add_job(sessions, status="RUNNING", attempts=3, heartbeat_at=stale)
    with sessions() as holding:
        holding.query(Job).filter(Job.id == first).with_for_update().one()
        assert recover(sessions) == 1
        with sessions() as db:
            assert db.get(Job, first).status == "RUNNING"
            assert db.get(Job, second).status == "FAILED"
        holding.rollback()
    assert recover(sessions) == 1


@pytest.mark.parametrize("operation", ["commit", "savepoint", "flush_error"])
def test_handler_transaction_boundaries_keep_recovery_safe(sessions, monkeypatch, operation):
    from ai import pipeline

    jid = add_job(sessions, job_type="PARSE", target_id=1)

    def parse(db, _version_id):
        if operation == "commit":
            db.commit()
            pytest.fail("A handler must not release its execution lock")
        elif operation == "savepoint":
            with db.begin_nested():
                db.execute(text("SELECT 1"))
        else:
            db.add(Job(job_type="INVALID", status="QUEUED", created_at=now()))
            db.flush()

    monkeypatch.setattr(pipeline, "parse_version", parse)
    with sessions() as db:
        job = worker._claim(db)
        worker._run_claimed(db, job)
        db.commit()
    with sessions() as db:
        job = db.get(Job, jid)
        assert job.status == ("SUCCEEDED" if operation == "savepoint" else "QUEUED")
        assert job.attempts == 1
        assert db.query(Job).count() == 1


def test_lost_database_connection_is_recovered_and_late_result_is_discarded(sessions, monkeypatch):
    from ai import pipeline

    jid = add_job(sessions, job_type="PARSE", target_id=1)
    entered, release = threading.Event(), threading.Event()
    backend_pids, errors = [], []

    def parse(db, _version_id):
        if backend_pids:
            return
        backend_pids.append(db.execute(text("SELECT pg_backend_pid()")).scalar_one())
        entered.set()
        assert release.wait(8)
        db.add(Job(job_type="NOTICE_BATCH", status="QUEUED", created_at=now()))

    monkeypatch.setattr(pipeline, "parse_version", parse)
    monkeypatch.setattr(worker, "_pulse", lambda _id, stopped, **_kw: stopped.wait(8))

    def old_worker():
        try:
            with sessions() as db:
                job = worker._claim(db)
                job.heartbeat_at = now() - timedelta(minutes=10)
                db.commit()
                worker._run_claimed(db, job)
                db.commit()
        except BaseException as exc:
            errors.append(exc)

    running = threading.Thread(target=old_worker)
    running.start()
    try:
        assert entered.wait(5)
        with sessions() as db:
            # Terminate only the backend identified by this isolated test worker.
            assert db.execute(text("SELECT pg_terminate_backend(:pid)"), {"pid": backend_pids[0]}).scalar_one()
            db.commit()
        assert recover(sessions) == 1
        with sessions() as db:
            replacement = worker._claim(db)
            assert replacement.attempts == 2
            worker._run_claimed(db, replacement)
            db.commit()
    finally:
        release.set()
        running.join(5)
    assert not running.is_alive() and not errors
    with sessions() as db:
        job = db.get(Job, jid)
        assert job.status == "SUCCEEDED" and job.attempts == 2
        assert db.query(Job).count() == 1


def test_parallel_children_finish_parent_without_deadlock_or_duplicate_notice(sessions, monkeypatch):
    from ai import pipeline

    parent = add_job(sessions, job_type="BATCH_AI_CHECK", status="RUNNING", attempts=1, heartbeat_at=now())
    for sid in (101, 102):
        add_job(sessions, job_type="AI_CHECK", parent_id=parent, target_id=sid)
    together = threading.Barrier(2)
    errors, notices = [], []

    def check(_db, sid, *_args, **_kwargs):
        together.wait(timeout=5)
        return SimpleNamespace(id=sid, report_no=1)

    monkeypatch.setattr(pipeline, "run_check", check)
    monkeypatch.setattr(worker, "_notify_done", lambda _db, job: notices.append((job.id, job.status)))

    def execute():
        try:
            with sessions() as db:
                job = worker._claim(db)
                worker._run_claimed(db, job)
                db.commit()
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=execute) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(8)
    assert all(not thread.is_alive() for thread in threads) and not errors
    with sessions() as db:
        job = db.get(Job, parent)
        assert (job.status, job.done_count, job.failed_count) == ("SUCCEEDED", 2, 0)
    assert notices.count((parent, "SUCCEEDED")) == 1
