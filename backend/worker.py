from __future__ import annotations

import threading
import time
from datetime import timedelta

from sqlalchemy import text

from config import WORKER_ENABLED
from database import SessionLocal
from models import Job, Material, Submission
from utils import get_setting, now
from diagnostics import event, log_exception

# 站内消息里的任务类型 / 状态用中文，避免界面出现英文枚举
_JOB_TYPE_NAME = {
    "PARSE": "材料解析",
    "AI_CHECK": "AI 校验",
    "BATCH_AI_CHECK": "批量 AI 校验",
    "BATCH_UPLOAD": "批量上传",
    "EXPORT": "数据导出",
}
_JOB_STATUS_NAME = {
    "QUEUED": "排队中",
    "RUNNING": "运行中",
    "SUCCEEDED": "已完成",
    "PARTIAL": "部分失败",
    "FAILED": "失败",
}


_stop = threading.Event()
_threads: list[threading.Thread] = []
_last_scan = 0.0


def start_workers() -> None:
    _stop.clear()
    if not WORKER_ENABLED:
        event("worker.disabled")
        return
    db = SessionLocal()
    try:
        cfg = get_setting(db, "worker", {"concurrency": 2, "heartbeat_timeout_s": 300})
        n = int(cfg.get("concurrency") or 2)
        timeout = int(cfg.get("heartbeat_timeout_s") or 300)
        db.query(Job).filter(Job.status == "RUNNING").filter(
            (Job.heartbeat_at.is_(None)) | (Job.heartbeat_at < now() - timedelta(seconds=timeout))
        ).update({"status": "QUEUED"}, synchronize_session=False)
        db.commit()
    except Exception as e:
        log_exception("worker.recovery_failed", e)
        db.rollback()
    finally:
        db.close()
    for i in range(max(1, n)):
        t = threading.Thread(target=_loop, name=f"worker-{i}", daemon=True)
        t.start()
        _threads.append(t)
    event("worker.started", threads=len(_threads))


def stop_workers() -> None:
    _stop.set()
    from ai.ocr import shutdown as ocr_shutdown
    ocr_shutdown()


def _loop() -> None:
    global _last_scan
    while not _stop.is_set():
        did = False
        db = SessionLocal()
        try:
            job = _claim(db)
            if job:
                did = True
                _run(db, job)
            if time.time() - _last_scan > 600:
                _scan(db)
                _last_scan = time.time()
            db.commit()
        except Exception as e:
            db.rollback()
            log_exception("worker.loop_failed", e)
        finally:
            db.close()
        if not did:
            with SessionLocal() as settings_db:
                delay = get_setting(settings_db, 'worker', {}).get('poll_interval_s', 1)
            _stop.wait(max(0.1, float(delay)))


def _claim(db) -> Job | None:
    row = db.execute(
        text("SELECT id FROM jobs WHERE status='QUEUED' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1")
    ).first()
    if not row:
        return None
    job = db.query(Job).filter(Job.id == row[0]).first()
    if not job:
        return None
    job.status = "RUNNING"
    job.started_at = now()
    job.heartbeat_at = now()
    job.attempts = (job.attempts or 0) + 1
    db.flush()
    # 先提交领取结果：任务随后失败/回滚时 attempts 不会丢失，避免无限重试
    db.commit()
    return job


def _heartbeat(db, job: Job) -> None:
    job.heartbeat_at = now()
    db.flush()


def _fail(db, job: Job, err: str) -> None:
    if not db.is_active:
        db.rollback()
    try:
        _apply_fail(db, job, err)
    except Exception as exc:
        log_exception("worker.failure_record_failed", exc, job_id=job.id)
        # 会话可能处于 aborted 状态（如 run_check 内部 flush 失败），回滚后重新加载任务再写
        db.rollback()
        fresh = db.query(Job).filter(Job.id == job.id).first()
        if fresh:
            try:
                _apply_fail(db, fresh, err)
            except Exception as exc:
                log_exception("worker.failure_retry_record_failed", exc, job_id=job.id)
                db.rollback()


def _apply_fail(db, job: Job, err: str) -> None:
    job.error = err[:800]
    if job.attempts < (job.max_attempts or 3):
        job.status = "QUEUED"
        job.stage_text = "等待重试"
    else:
        job.status = "FAILED"
        job.finished_at = now()
        _notify_done(db, job)
    db.flush()


def _ok(db, job: Job, result=None, status="SUCCEEDED") -> None:
    job.status = status
    job.progress = 100
    job.result = result
    job.error = None
    job.finished_at = now()
    db.flush()
    _notify_done(db, job)


def _notify_done(db, job: Job) -> None:
    if not job.created_by:
        return
    try:
        from services.messages import send_message
        send_message(db, job.created_by, "JOB_DONE",
                     f"任务 {_JOB_TYPE_NAME.get(job.job_type, job.job_type)} #{job.id} {_JOB_STATUS_NAME.get(job.status, job.status)}",
                     job.error or "", "job", job.id)
    except Exception as exc:
        log_exception("worker.notification_failed", exc, job_id=job.id)


def _run(db, job: Job) -> None:
    job.stage_text = "执行中"
    _heartbeat(db, job)
    # Release the job row before starting an independent heartbeat transaction.
    db.commit()
    pulse_stop = threading.Event()
    pulse = threading.Thread(target=_pulse, args=(job.id, pulse_stop), daemon=True)
    pulse.start()
    try:
        if job.job_type == "PARSE":
            from ai.pipeline import parse_version
            vid = (job.params or {}).get("version_id") or job.target_id
            parse_version(db, int(vid))
            _ok(db, job, {"version_id": vid})
        elif job.job_type == "AI_CHECK":
            from ai.pipeline import run_check
            sid = (job.params or {}).get("submission_id") or job.target_id
            trig = (job.params or {}).get("trigger_type") or "REVIEW"
            use_llm = (job.params or {}).get("use_llm", True)
            sub = db.query(Submission).filter(Submission.id == sid).first()
            if sub:
                sub.ai_status = "RUNNING"
            report = run_check(db, int(sid), trig, job.created_by, job.id, use_llm=use_llm)
            _ok(db, job, {"report_id": report.id, "report_no": report.report_no})
            if job.parent_id:
                _bump_parent(db, job.parent_id, True)
        elif job.job_type == "BATCH_AI_CHECK":
            kids = db.query(Job).filter(Job.parent_id == job.id).all()
            if not kids:
                ids = (job.params or {}).get("submission_ids") or []
                if not ids:
                    _ok(db, job, {"total": 0, "failed": 0})
                    return
                for sid in ids:
                    child = Job(
                        job_type="AI_CHECK", status="QUEUED", parent_id=job.id,
                        target_type="submission", target_id=sid,
                        params={"submission_id": sid, "trigger_type": "BATCH", "use_llm": True},
                        created_by=job.created_by, created_at=now(),
                    )
                    db.add(child)
                    sub = db.query(Submission).filter(Submission.id == sid).first()
                    if sub:
                        sub.ai_status = "QUEUED"
                db.flush()
                job.stage_text = "已拆分子任务"
                job.status = "RUNNING"
                return
            done = sum(1 for k in kids if k.status in ("SUCCEEDED", "FAILED", "PARTIAL"))
            failed = sum(1 for k in kids if k.status == "FAILED")
            job.done_count = done
            job.failed_count = failed
            job.progress = int(100 * done / max(1, len(kids)))
            if done >= len(kids):
                st = "SUCCEEDED" if failed == 0 else ("FAILED" if failed == len(kids) else "PARTIAL")
                _ok(db, job, {"total": len(kids), "failed": failed}, st)
            else:
                job.heartbeat_at = now()
                job.status = "RUNNING"
        elif job.job_type == "BATCH_UPLOAD":
            from services.importer import process_batch_upload
            process_batch_upload(db, job)
            _ok(db, job, job.result)
        elif job.job_type == "EXPORT":
            from services.exporter import run_export_job
            run_export_job(db, job)
            _ok(db, job, job.result)
        elif job.job_type == "NOTICE_BATCH":
            _ok(db, job, {"ok": True})
        else:
            _fail(db, job, f"未知任务类型 {job.job_type}")
    except Exception as e:
        log_exception("worker.job_failed", e, job_id=job.id, job_type=job.job_type)
        _fail(db, job, "任务执行失败，请联系管理员并提供任务编号")
        if job.job_type == "AI_CHECK" and job.parent_id:
            _bump_parent(db, job.parent_id, False)
    finally:
        pulse_stop.set()
        pulse.join(timeout=2)


def _pulse(job_id, stopped, interval=5):
    while not stopped.wait(interval):
        try:
            with SessionLocal() as heartbeat_db:
                # Avoid blocking shutdown when the worker has already locked its final result.
                heartbeat_db.execute(text("SET LOCAL lock_timeout = '500ms'"))
                heartbeat_db.query(Job).filter(Job.id == job_id, Job.status == 'RUNNING').update(
                    {'heartbeat_at': now()}, synchronize_session=False)
                heartbeat_db.commit()
        except Exception:
            continue


def _bump_parent(db, parent_id: int, ok: bool) -> None:
    # FOR NO KEY UPDATE serialises sibling workers without conflicting with the FK KEY SHARE lock
    # each child's own update holds on this row (plain FOR UPDATE deadlocks between siblings).
    p = db.query(Job).filter(Job.id == parent_id).with_for_update(key_share=True).populate_existing().first()
    if not p:
        return
    kids = [s for (s,) in db.query(Job.status).filter(Job.parent_id == parent_id).all()]
    done = sum(1 for s in kids if s in ("SUCCEEDED", "FAILED", "PARTIAL", "CANCELLED"))
    failed = sum(1 for s in kids if s == "FAILED")
    p.done_count = done
    p.failed_count = failed
    p.progress = int(100 * done / max(1, len(kids) or p.total or 1))
    p.heartbeat_at = now()
    if kids and done >= len(kids):
        st = "SUCCEEDED" if failed == 0 else ("FAILED" if failed == len(kids) else "PARTIAL")
        p.status = st
        p.progress = 100
        p.result = {"total": len(kids), "failed": failed}
        p.finished_at = now()
        _notify_done(db, p)


def _scan(db) -> None:
    from models import ImportPasswordFile
    from models import Message, ExportFile
    from datetime import datetime, timezone
    db.query(ImportPasswordFile).filter(ImportPasswordFile.expires_at <= now()).delete(synchronize_session=False)
    from services.deadlines import scan_deadlines
    from services.storage import abs_path
    scan_deadlines(db)
    for exported in db.query(ExportFile).filter(ExportFile.expires_at < now()).all():
        try:
            path = abs_path(exported.stored_path)
            path.unlink(missing_ok=True)
        except (OSError, ValueError):
            continue
        db.delete(exported)
    db.execute(text("DELETE FROM revoked_tokens WHERE expires_at < now()"))
