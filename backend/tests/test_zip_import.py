"""G3：ZIP 上传、识别与确认入库。

覆盖幂等、内容查重、跳过语义、导入阶段优先级、单条失败隔离、任务可见性与状态校验、
job.result 回写、识别范围与识别重试。
"""
from __future__ import annotations

from models import AuditLog, BatchUploadItem, Job, Material
from services.importer import process_batch_upload
from tests.pg_fixtures import (  # noqa: F401  夹具由 import 引入
    add_archive,
    add_job,
    add_material,
    add_submission,
    add_upload_item,
    as_client,
    case,
    pdf_bytes,
    pg_schema,
    storage_tmp,
    zip_bytes,
)


def upload(case, client, entries, *, stage_code=None, batch_id=None):
    data = {k: v for k, v in {"stage_code": stage_code, "batch_id": batch_id}.items() if v is not None}
    return client.post(
        "/api/materials/batch-upload",
        files={"file": ("batch.zip", zip_bytes(entries), "application/zip")},
        data=data,
    )


def recognize(case, job, *, status="SUCCEEDED"):
    process_batch_upload(case.db, job)
    job.status = status
    case.db.flush()
    case.db.refresh(job)
    return job


def upload_and_recognize(case, client, entries, **form):
    response = upload(case, client, entries, **form)
    assert response.status_code == 200, response.text
    job = case.db.query(Job).filter(Job.id == response.json()["data"]["job_id"]).one()
    return recognize(case, job)


def assign(case, client, job, body):
    return client.put(f"/api/materials/batch-upload/{job.id}/assign", json=body)


def items_of(job):
    return {row["entry_path"]: row for row in (job.result or {}).get("items", [])}


def test_upload_rejects_bad_form_fields_before_saving(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    for form, message in (
        ({"stage_code": "abc"}, "阶段参数无效"),
        ({"stage_code": "6"}, "阶段参数无效"),
        ({"batch_id": "0"}, "批次参数无效"),
        ({"batch_id": "abc"}, "批次参数无效"),
    ):
        response = upload(case, client, {"2026001001_申请书.pdf": pdf_bytes("a")}, **form)
        assert response.status_code == 422, (form, response.text)
        assert response.json()["message"] == message
    assert list((storage_tmp / "tmp").iterdir()) == []
    assert case.db.query(Job).count() == 0


def test_upload_records_uploader_identity_and_stage(case, as_client, storage_tmp):
    response = upload(case, as_client(case.reviewer), {"2026001001_申请书.pdf": pdf_bytes("a")},
                      stage_code=2, batch_id=case.batches[0].id)
    assert response.status_code == 200, response.text
    job = case.db.query(Job).filter(Job.id == response.json()["data"]["job_id"]).one()
    assert job.job_type == "BATCH_UPLOAD"
    assert job.params["stage_code"] == 2
    assert job.params["batch_id"] == case.batches[0].id
    assert job.params["actor_role"] == "BRANCH_REVIEWER"
    assert job.params["actor_org_id"] == case.branches[0].id


def test_repeat_confirm_is_idempotent(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"2026001001_申请书.pdf": pdf_bytes("a")})
    item_id = job.result["items"][0]["item_id"]
    body = {"assignments": [{"item_id": item_id, "archive_id": case.arch_a.id}]}

    first = assign(case, client, job, body)
    assert first.status_code == 200, first.text
    data = first.json()["data"]
    assert (data["imported"], data["already_imported"], data["skipped"], data["failed"]) == (1, 0, 0, 0)
    material_id = data["items"][0]["material_id"]
    assert data["items"][0]["stage_code"] == 2
    assert data["items"][0]["status"] == "IMPORTED"
    assert case.db.query(Material).filter(Material.submission_id == case.sub_draft.id).count() == 1

    second = assign(case, client, job, body)
    again = second.json()["data"]
    assert (again["imported"], again["already_imported"]) == (0, 1)
    assert again["items"][0]["material_id"] == material_id
    assert case.db.query(Material).filter(Material.submission_id == case.sub_draft.id).count() == 1
    # 审计只写一条
    audit = case.db.query(AuditLog).filter(AuditLog.action == "BATCH_IMPORT").all()
    assert len(audit) == 1
    assert audit[0].detail["item_id"] == item_id
    assert audit[0].detail["archive_id"] == case.arch_a.id
    assert audit[0].detail["stage_code"] == 2
    assert audit[0].object_type == "material"


def test_same_content_is_not_stored_twice(case, as_client, storage_tmp):
    content = pdf_bytes("dup")
    existing, _ = add_material(case.db, case.sub_draft, content=content)
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"2026001001_申请书.pdf": content})
    item_id = job.result["items"][0]["item_id"]
    data = assign(case, client, job, {"assignments": [{"item_id": item_id, "archive_id": case.arch_a.id}]}).json()["data"]
    assert (data["imported"], data["already_imported"]) == (0, 1)
    row = data["items"][0]
    assert row["status"] == "IMPORTED"
    assert row["material_id"] == existing.id
    assert row["note"] == "相同文件已在该提交包中，未重复入库"
    assert case.db.query(Material).filter(Material.submission_id == case.sub_draft.id).count() == 1
    # 刷新任务详情后说明仍在
    detail = case.db.query(Job).filter(Job.id == job.id).one()
    assert detail.result["items"][0]["note"] == "相同文件已在该提交包中，未重复入库"
    assert detail.result["items"][0]["material_id"] == existing.id


def test_skip_only_touches_items_of_the_same_job(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"2026001001_申请书.pdf": pdf_bytes("a")})
    item_id = job.result["items"][0]["item_id"]
    other_job = add_job(case.db, created_by=case.reviewer.id)
    other_item = add_upload_item(case.db, other_job, entry_path="2026001999_申请书.pdf", status="MATCHED")

    data = assign(case, client, job, {"skip_item_ids": [item_id, other_item.id]}).json()["data"]
    assert data["skipped"] == 1
    assert data["failed"] == 1
    outside = next(row for row in data["items"] if row["item_id"] == other_item.id)
    assert outside["status"] == "FAILED" and outside["error"] == "条目不属于该任务"
    case.db.refresh(other_item)
    assert other_item.status == "MATCHED"
    assert case.db.query(BatchUploadItem).filter_by(id=item_id).one().status == "SKIPPED"


def test_imported_item_is_not_downgraded_by_skip(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"2026001001_申请书.pdf": pdf_bytes("a")})
    item_id = job.result["items"][0]["item_id"]
    assign(case, client, job, {"assignments": [{"item_id": item_id, "archive_id": case.arch_a.id}]})
    data = assign(case, client, job, {"skip_item_ids": [item_id]}).json()["data"]
    assert (data["skipped"], data["already_imported"]) == (0, 1)
    assert data["items"][0]["status"] == "IMPORTED"
    assert case.db.query(BatchUploadItem).filter_by(id=item_id).one().status == "IMPORTED"


def stage_archive(case, *, student_no="2026003001", current_stage=3, stages=(1, 2, 3), status="DRAFT"):
    arch = add_archive(case.db, case, student_no=student_no, branch=0, current_stage=current_stage)
    subs = {stage: add_submission(case.db, arch, stage, status) for stage in stages}
    return arch, subs


def test_stage_priority_item_over_request_over_job(case, as_client, storage_tmp):
    arch, subs = stage_archive(case)
    client = as_client(case.reviewer)
    job = upload_and_recognize(
        case, client,
        {"2026003001_a.pdf": pdf_bytes("a"), "2026003001_b.pdf": pdf_bytes("b")},
        stage_code=2,
    )
    rows = job.result["items"]
    data = assign(case, client, job, {
        "stage_code": 2,
        "assignments": [
            {"item_id": rows[0]["item_id"], "archive_id": arch.id, "stage_code": 3},
            {"item_id": rows[1]["item_id"], "archive_id": arch.id},
        ],
    }).json()["data"]
    by_id = {row["item_id"]: row for row in data["items"]}
    assert by_id[rows[0]["item_id"]]["stage_code"] == 3
    assert by_id[rows[1]["item_id"]]["stage_code"] == 2
    assert case.db.query(Material).filter_by(submission_id=subs[3].id).count() == 1
    assert case.db.query(Material).filter_by(submission_id=subs[2].id).count() == 1


def test_stage_falls_back_to_job_then_archive_current(case, as_client, storage_tmp):
    arch, subs = stage_archive(case, student_no="2026003002", stages=(1, 2, 3))
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"2026003002_a.pdf": pdf_bytes("a")}, stage_code=1)
    row = job.result["items"][0]
    data = assign(case, client, job, {"assignments": [{"item_id": row["item_id"], "archive_id": arch.id}]}).json()["data"]
    assert data["items"][0]["stage_code"] == 1

    arch2, _ = stage_archive(case, student_no="2026003003", stages=(1, 2, 3))
    job2 = upload_and_recognize(case, client, {"2026003003_a.pdf": pdf_bytes("b")})
    row2 = job2.result["items"][0]
    data2 = assign(case, client, job2, {"assignments": [{"item_id": row2["item_id"], "archive_id": arch2.id}]}).json()["data"]
    assert data2["items"][0]["stage_code"] == 3  # 档案当前阶段


def test_one_item_failure_does_not_block_others(case, as_client, storage_tmp):
    arch, subs = stage_archive(case, student_no="2026003011", current_stage=2, stages=(1, 2))
    no_sub, _ = stage_archive(case, student_no="2026003012", current_stage=3, stages=(1, 2))
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {
        "2026003011_a.pdf": pdf_bytes("a"),
        "2026003011_b.pdf": pdf_bytes("b"),
        "2026003012_c.pdf": pdf_bytes("c"),
        "2026001002_d.pdf": pdf_bytes("d"),
    })
    rows = {row["entry_path"]: row["item_id"] for row in job.result["items"]}
    data = assign(case, client, job, {
        "assignments": [
            {"item_id": rows["2026003011_a.pdf"], "archive_id": arch.id, "stage_code": 3},   # 超过当前阶段
            {"item_id": rows["2026003011_b.pdf"], "archive_id": arch.id, "stage_code": 1},   # 成功
            {"item_id": rows["2026003012_c.pdf"], "archive_id": no_sub.id, "stage_code": 3},  # 没有该阶段提交包
            {"item_id": rows["2026001002_d.pdf"], "archive_id": case.arch_b.id, "stage_code": 1},  # ORG_FILING
        ],
    }).json()["data"]
    by_id = {row["item_id"]: row for row in data["items"]}
    assert by_id[rows["2026003011_a.pdf"]]["error"] == "导入阶段不能超过档案当前阶段"
    assert by_id[rows["2026003011_a.pdf"]]["status"] == "FAILED"
    assert by_id[rows["2026003011_b.pdf"]]["status"] == "IMPORTED"
    assert by_id[rows["2026003012_c.pdf"]]["error"] == "该阶段提交包不存在"
    assert by_id[rows["2026001002_d.pdf"]]["error"] == "提交包审核中或已备案，不可导入"
    assert (data["imported"], data["failed"]) == (1, 3)
    assert case.db.query(Material).filter_by(submission_id=subs[1].id).count() == 1


def test_missing_temp_file_fails_only_that_item(case, as_client, storage_tmp):
    job = add_job(case.db, created_by=case.reviewer.id)
    item = add_upload_item(case.db, job, entry_path="2026001001_申请书.pdf", temp_path="tmp/gone.pdf",
                           archive_id=case.arch_a.id, status="MATCHED")
    data = assign(case, as_client(case.reviewer), job,
                  {"assignments": [{"item_id": item.id, "archive_id": case.arch_a.id}]}).json()["data"]
    assert data["failed"] == 1
    assert data["items"][0]["error"] == "暂存文件已清理，请重新上传 ZIP"


def test_job_lookup_hides_other_people_and_other_types(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    foreign = add_job(case.db, created_by=case.org_admin.id)
    other_type = add_job(case.db, job_type="EXPORT", created_by=case.reviewer.id)
    for job in (foreign, other_type):
        response = assign(case, client, job, {"assignments": []})
        assert response.status_code == 404, response.text
        assert response.json()["message"] == "任务不存在"


def test_confirm_requires_finished_recognition(case, as_client, storage_tmp):
    job = add_job(case.db, status="RUNNING", created_by=case.reviewer.id)
    response = assign(case, as_client(case.reviewer), job, {"assignments": []})
    assert response.status_code == 409
    assert response.json()["message"] == "文件归属识别尚未完成，请稍后再确认"


def test_assign_body_is_validated(case, as_client, storage_tmp):
    job = add_job(case.db, created_by=case.reviewer.id)
    client = as_client(case.reviewer)
    for body in (
        {"assignments": "bad"},
        {"assignments": [{"item_id": True, "archive_id": 1}]},
        {"assignments": [{"item_id": 1, "archive_id": 1, "material_type_id": "3"}]},
        {"assignments": [{"item_id": 1, "archive_id": 0}]},
        {"assignments": [{"item_id": 1, "archive_id": 1, "stage_code": 6}]},
        {"stage_code": 0},
        {"skip_item_ids": ["a"]},
        {"skip_item_ids": [False]},
    ):
        response = assign(case, client, job, body)
        assert response.status_code == 422, (body, response.text)
        assert response.json()["message"] == "确认请求格式无效"
        assert response.json()["data"]["errors"]


def test_job_result_is_rebuilt_from_the_database(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {
        "2026001001_申请书.pdf": pdf_bytes("a"),
        "2026001002_思想汇报.pdf": pdf_bytes("b"),
    })
    rows = job.result["items"]
    data = assign(case, client, job, {
        "assignments": [{"item_id": rows[0]["item_id"], "archive_id": case.arch_a.id}],
        "skip_item_ids": [rows[1]["item_id"]],
    }).json()["data"]
    assert (data["imported"], data["skipped"]) == (1, 1)

    detail = client.get(f"/api/jobs/{job.id}").json()["data"]
    result = detail["result"]
    assert result["imported"] == 1 and result["skipped"] == 1 and result["failed"] == 0
    assert result["total"] == 2
    statuses = {row["item_id"]: row["status"] for row in result["items"]}
    assert statuses[rows[0]["item_id"]] == "IMPORTED"
    assert statuses[rows[1]["item_id"]] == "SKIPPED"
    imported = next(row for row in result["items"] if row["item_id"] == rows[0]["item_id"])
    assert imported["material_id"] is not None and imported["stage_code"] == 2


def test_recognition_only_matches_uploader_scope(case, as_client, storage_tmp):
    client = as_client(case.reviewer)  # 支部 0 的审核员
    job = upload_and_recognize(case, client, {
        "2026001001_申请书.pdf": pdf_bytes("a"),
        "2026001003_申请书.pdf": pdf_bytes("b"),  # 支部 1 的档案，超出上传人范围
        "nobody.pdf": pdf_bytes("c"),
    })
    rows = items_of(job)
    inside = rows["2026001001_申请书.pdf"]
    assert inside["status"] == "MATCHED"
    assert inside["matched_archive"]["id"] == case.arch_a.id
    outside = rows["2026001003_申请书.pdf"]
    assert outside["status"] == "UNMATCHED"
    assert outside["matched_archive"] is None  # 不返回范围外学生的姓名
    assert rows["nobody.pdf"]["status"] == "UNMATCHED"


def test_recognition_retry_reuses_items(case, as_client, storage_tmp):
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"2026001001_申请书.pdf": pdf_bytes("a")})
    first = [row["item_id"] for row in job.result["items"]]
    process_batch_upload(case.db, job)
    case.db.flush()
    case.db.refresh(job)
    assert [row["item_id"] for row in job.result["items"]] == first
    assert case.db.query(BatchUploadItem).filter_by(job_id=job.id).count() == 1


def test_unmatched_item_can_still_be_assigned(case, as_client, storage_tmp):
    arch, _ = stage_archive(case, student_no="2026003021", current_stage=2, stages=(1, 2))
    client = as_client(case.reviewer)
    job = upload_and_recognize(case, client, {"nobody.pdf": pdf_bytes("z")})
    row = job.result["items"][0]
    assert row["status"] == "UNMATCHED"
    data = assign(case, client, job, {"assignments": [{"item_id": row["item_id"], "archive_id": arch.id}]}).json()["data"]
    assert data["imported"] == 1
    assert data["items"][0]["status"] == "IMPORTED"
    assert data["items"][0]["matched_archive"]["id"] == arch.id
