"""G3：同一任务的两个确认请求并发时只建一份材料。

这里需要两个会话同时看到**已提交**的数据，所以不用 case 夹具（它把测试包在事务里），
而是在独立 schema 中提交造数，两个线程各自开一个会话按接口同样的顺序加锁后确认。
"""
from __future__ import annotations

import threading

import pytest
from sqlalchemy.orm import Session

from models import Job, Material
from services.importer import assign_batch_items, rebuild_job_result
from services.scope import scoped_jobs
from services import storage as store
from tests.pg_fixtures import (
    add_job,
    add_upload_item,
    build_case,
    make_schema_engine,
    pdf_bytes,
)


@pytest.fixture(scope="module")
def committed_schema():
    schema = make_schema_engine("zipconc")
    try:
        yield schema
    finally:
        schema.drop()


@pytest.fixture
def committed_case(committed_schema, tmp_path, monkeypatch):
    from config import ensure_storage

    monkeypatch.setattr(store, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr("config.STORAGE_DIR", tmp_path)
    ensure_storage()
    db = Session(bind=committed_schema.engine, expire_on_commit=False)
    ctx = build_case(db)
    db.commit()
    try:
        yield ctx
    finally:
        db.close()


def test_two_concurrent_confirms_create_one_material(committed_case, committed_schema):
    case = committed_case
    setup = Session(bind=committed_schema.engine, expire_on_commit=False)
    try:
        temp_path = store.save_tmp(pdf_bytes("concurrent"), "申请书.pdf")
        job = add_job(
            setup, created_by=case.reviewer.id, params={"stage_code": None},
            target_type="batch", target_id=case.batches[0].id,
        )
        item = add_upload_item(
            setup, job, entry_path="2026001001_申请书.pdf", temp_path=temp_path,
            archive_id=case.arch_a.id, status="MATCHED",
        )
        job_id, item_id, archive_id = job.id, item.id, case.arch_a.id
        setup.commit()
    finally:
        setup.close()

    barrier = threading.Barrier(2)
    results: list = []
    errors: list = []

    def confirm():
        db = Session(bind=committed_schema.engine, expire_on_commit=False)
        try:
            barrier.wait(timeout=10)
            locked = (
                scoped_jobs(db, case.reviewer)
                .filter(Job.id == job_id, Job.job_type == "BATCH_UPLOAD")
                .with_for_update()
                .populate_existing()
                .first()
            )
            result = assign_batch_items(
                db, locked, case.reviewer, None,
                [{"item_id": item_id, "archive_id": archive_id,
                  "material_type_id": None, "stage_code": None}],
                [],
            )
            locked.result = rebuild_job_result(db, locked)
            db.commit()
            results.append(result)
        except Exception as exc:  # pragma: no cover - 失败时由下面的断言暴露
            db.rollback()
            errors.append(exc)
        finally:
            db.close()

    threads = [threading.Thread(target=confirm, name=f"confirm-{i}") for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not errors, errors
    assert len(results) == 2
    assert sum(row["imported"] for row in results) == 1
    assert sum(row["already_imported"] for row in results) == 1
    imported = [entry for result in results for entry in result["items"] if entry["status"] == "IMPORTED"]
    assert len({entry["material_id"] for entry in imported}) == 1

    check = Session(bind=committed_schema.engine)
    try:
        assert check.query(Material).filter(Material.submission_id == case.sub_draft.id).count() == 1
    finally:
        check.close()
