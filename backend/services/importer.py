from __future__ import annotations

import re
from collections import defaultdict, deque
from pathlib import Path
from types import SimpleNamespace

from openpyxl import Workbook
from sqlalchemy.orm import Session

from errors import AppError, unprocessable
from models import Archive, BatchUploadItem, Job, Material, MaterialType, MaterialVersion, Submission
from security import sha256_bytes
from services import storage as store
from services.audit import log as audit_log
from services.materials import create_material_with_file
from services.scope import scoped_archives
from utils import now

# 允许上传 ZIP 的角色：旧任务没有记录上传人身份时，只从这些角色里取默认身份
IMPORT_ROLES = ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN")

DUPLICATE_NOTE = "相同文件已在该提交包中，未重复入库"


def users_template() -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "用户"
    ws.append(["username", "real_name", "gender", "org_code", "role", "phone", "email"])
    ws.append(["demo_user", "示例", "女", "DEMO_B1", "STUDENT", "", ""])
    ws2 = wb.create_sheet("学生档案")
    cols = ["student_no", "real_name", "gender", "ethnicity", "birth_date", "native_place",
            "major", "class_name", "branch_code", "batch_name"]
    cols += [f"T{str(i).zfill(2)}" for i in range(1, 22)]
    ws2.append(cols)
    return wb


def import_users_xlsx(db: Session, actor, data: bytes, dry_run: bool = True, batch_id=None) -> dict:
    from services.user_import import import_users
    return import_users(db, actor, data, dry_run=dry_run, batch_id=batch_id)


def _actor_identity(db: Session, job: Job):
    """识别时使用的数据范围身份：上传当刻的激活角色与组织。

    旧任务缺少 actor_role/actor_org_id 时，只从创建人可上传 ZIP 的角色里按既有优先级取
    默认身份，避免兼任 SYS_ADMIN 的账号被当成全校范围；没有这类角色则不自动匹配。
    """
    params = job.params or {}
    role = params.get("actor_role")
    if role:
        return SimpleNamespace(id=job.created_by, role=role, org_id=params.get("actor_org_id"))
    from deps import _pick_role

    candidates = [r for r in (job.creator.roles if job.creator else []) if r.role in IMPORT_ROLES]
    if not candidates:
        return SimpleNamespace(id=job.created_by, role=None, org_id=None)
    picked, picked_org = _pick_role(candidates, None)
    return SimpleNamespace(id=job.created_by, role=picked, org_id=picked_org)


def process_batch_upload(db: Session, job: Job) -> None:
    params = job.params or {}
    dest = f"tmp/batch_{job.id}"
    items = store.extract_zip_safe(params.get("zip_path"), dest)
    types = db.query(MaterialType).filter(MaterialType.is_active.is_(True)).all()
    identity = _actor_identity(db, job)
    existing: dict[str, deque] = defaultdict(deque)
    for row in (
        db.query(BatchUploadItem).filter(BatchUploadItem.job_id == job.id).order_by(BatchUploadItem.id).all()
    ):
        existing[row.entry_path].append(row)
    try:
        # 整次识别用保存点隔离：中途失败不留下半成品条目
        with db.begin_nested():
            result = _recognize(db, job, items, types, identity, existing)
    except Exception:
        for it in items:
            store.remove(it["temp_path"])
        raise
    job.result = result
    job.total = result["total"]
    job.done_count = result["total"]
    db.flush()


def _recognize(db: Session, job: Job, items: list, types: list, identity, existing: dict) -> dict:
    type_map = {t.id: t for t in types}
    matched = unmatched = 0
    rows = []
    for it in items:
        name = Path(it["entry_path"]).name
        student_no = _parse_student_no(it["entry_path"])
        type_hint = _parse_type_hint(name, types)
        arch = None
        if student_no:
            # 只匹配上传人数据范围内的档案：范围外的学号一律按未识别处理，不返回姓名
            arch = (
                scoped_archives(db.query(Archive), identity, db)
                .filter(Archive.student_no == student_no)
                .first()
            )
        status = "MATCHED" if arch else "UNMATCHED"
        mt_id = next((t.id for t in types if t.code == type_hint), None)
        row = existing[it["entry_path"]].popleft() if existing.get(it["entry_path"]) else None
        if row is not None and row.status in ("IMPORTED", "SKIPPED"):
            # 已导入/已跳过的条目保持不变，新解出的重复文件删掉
            store.remove(it["temp_path"])
            rows.append(row)
            if row.matched_archive_id:
                matched += 1
            else:
                unmatched += 1
            continue
        if row is None:
            row = BatchUploadItem(job_id=job.id, entry_path=it["entry_path"], created_at=now())
            db.add(row)
            row.temp_path = it["temp_path"]
            row.file_size = it["file_size"]
        else:
            # 复用已有条目：原暂存文件还在时保留原文件，否则改用新文件
            if row.temp_path and store.exists(row.temp_path):
                store.remove(it["temp_path"])
            else:
                row.temp_path = it["temp_path"]
                row.file_size = it["file_size"]
        row.parsed_student_no = student_no
        row.parsed_type_hint = type_hint
        row.material_type_id = mt_id
        row.matched_archive_id = arch.id if arch else None
        row.match_method = "DIRECTORY" if "/" in it["entry_path"].replace("\\", "/") else "FILENAME"
        row.status = status
        row.error = None
        row.updated_at = now()
        if arch:
            matched += 1
        else:
            unmatched += 1
        rows.append(row)
    db.flush()
    return {
        "total": len(rows), "matched": matched, "unmatched": unmatched,
        "imported": 0, "skipped": 0, "failed": 0,
        "items": [_item_dict(r, type_map) for r in rows],
    }


def parse_assign_body(body) -> tuple[int | None, list[dict], list[int]]:
    """校验确认请求的结构，返回 (请求级阶段, 条目分配, 跳过条目)。不合法抛 422。"""
    if not isinstance(body, dict):
        raise unprocessable("确认请求格式无效", [{"loc": ["body"], "msg": "请求体须为对象"}])
    errors: list[dict] = []
    stage_code = _positive_stage(body.get("stage_code"))
    if body.get("stage_code") is not None and stage_code is None:
        errors.append({"loc": ["body", "stage_code"], "msg": "导入阶段须为 1–5 的整数"})

    assignments: list[dict] = []
    raw_assignments = body.get("assignments", [])
    if not isinstance(raw_assignments, list):
        errors.append({"loc": ["body", "assignments"], "msg": "assignments 须为列表"})
    else:
        for index, entry in enumerate(raw_assignments):
            if not isinstance(entry, dict):
                errors.append({"loc": ["body", "assignments", index], "msg": "分配项须为对象"})
                continue
            item_id = _positive_int(entry.get("item_id"))
            archive_id = _positive_int(entry.get("archive_id"))
            if item_id is None:
                errors.append({"loc": ["body", "assignments", index, "item_id"], "msg": "item_id 须为正整数"})
            if archive_id is None:
                errors.append({"loc": ["body", "assignments", index, "archive_id"], "msg": "archive_id 须为正整数"})
            material_type_id = entry.get("material_type_id")
            if material_type_id is not None:
                material_type_id = _positive_int(material_type_id)
                if material_type_id is None:
                    errors.append({"loc": ["body", "assignments", index, "material_type_id"], "msg": "material_type_id 须为正整数或 null"})
            item_stage = entry.get("stage_code")
            if item_stage is not None:
                item_stage = _positive_stage(item_stage)
                if item_stage is None:
                    errors.append({"loc": ["body", "assignments", index, "stage_code"], "msg": "条目阶段须为 1–5 的整数或 null"})
            if item_id is None or archive_id is None:
                continue
            assignments.append({
                "item_id": item_id, "archive_id": archive_id,
                "material_type_id": material_type_id, "stage_code": item_stage,
            })

    skip_ids: list[int] = []
    raw_skips = body.get("skip_item_ids", [])
    if not isinstance(raw_skips, list):
        errors.append({"loc": ["body", "skip_item_ids"], "msg": "skip_item_ids 须为列表"})
    else:
        for index, value in enumerate(raw_skips):
            sid = _positive_int(value)
            if sid is None:
                errors.append({"loc": ["body", "skip_item_ids", index], "msg": "跳过条目须为正整数"})
            else:
                skip_ids.append(sid)
    if errors:
        raise unprocessable("确认请求格式无效", errors)
    return stage_code, assignments, skip_ids


def _positive_int(value) -> int | None:
    # 整数字段不接受布尔值和字符串
    if type(value) is int and value > 0:
        return value
    return None


def _positive_stage(value) -> int | None:
    if type(value) is int and 1 <= value <= 5:
        return value
    return None


def resolve_stage(item_stage, request_stage, job_stage, archive) -> int:
    """导入阶段优先级：条目级 > 请求级 > 任务参数 > 档案当前阶段。"""
    for value in (item_stage, request_stage, job_stage):
        if value:
            return int(value)
    return int(archive.current_stage)


class _ItemFailure(Exception):
    """单条导入的业务失败：只影响本条，不影响其他条目和 HTTP 状态。"""


def assign_batch_items(db, job: Job, actor, stage_code, assignments: list, skip_ids: list) -> dict:
    type_map = {t.id: t for t in db.query(MaterialType).all()}
    job_stage = (job.params or {}).get("stage_code")
    skip = set(skip_ids or [])
    imported = already_imported = skipped = failed = 0
    out: list[dict] = []
    handled: set[int] = set()

    for entry in assignments or []:
        item_id = entry["item_id"]
        if item_id in handled:
            # 同一 item_id 只处理首次出现的一条
            continue
        handled.add(item_id)
        item = (
            db.query(BatchUploadItem)
            .filter(BatchUploadItem.id == item_id, BatchUploadItem.job_id == job.id)
            .first()
        )
        if item is None:
            failed += 1
            out.append(_missing_item(item_id, "条目不属于该任务"))
            continue
        if item.id in skip:
            # 同时列入跳过的条目按跳过处理；已导入的保持 IMPORTED
            if item.status == "IMPORTED":
                already_imported += 1
                out.append(_item_dict(item, type_map, _material_stages(db, [item]), already_imported=True))
            else:
                item.status = "SKIPPED"
                item.error = None
                item.updated_at = now()
                skipped += 1
                out.append(_item_dict(item, type_map, _material_stages(db, [item]), already_imported=False))
            continue
        if item.status == "IMPORTED":
            # 幂等：重复确认不新建材料，返回原 material_id
            already_imported += 1
            out.append(_item_dict(item, type_map, _material_stages(db, [item]), already_imported=True))
            continue

        stored_rel = None
        material = None
        duplicate = None
        error = None
        try:
            with db.begin_nested():
                arch = (
                    scoped_archives(db.query(Archive), actor, db)
                    .filter(Archive.id == entry["archive_id"])
                    .first()
                )
                if arch is None:
                    raise _ItemFailure("档案不存在或无权限")
                stage = resolve_stage(entry.get("stage_code"), stage_code, job_stage, arch)
                if stage > arch.current_stage:
                    raise _ItemFailure("导入阶段不能超过档案当前阶段")
                sub = (
                    db.query(Submission)
                    .filter(Submission.archive_id == arch.id, Submission.stage_code == stage)
                    .first()
                )
                if sub is None:
                    raise _ItemFailure("该阶段提交包不存在")
                sub = (
                    db.query(Submission)
                    .filter(Submission.id == sub.id)
                    .with_for_update()
                    .populate_existing()
                    .one()
                )
                if sub.status not in ("DRAFT", "RETURNED"):
                    raise _ItemFailure("提交包审核中或已备案，不可导入")
                if not store.exists(item.temp_path):
                    raise _ItemFailure("暂存文件已清理，请重新上传 ZIP")
                data = store.read_bytes(item.temp_path)
                sha = sha256_bytes(data)
                mt_id = entry.get("material_type_id") or item.material_type_id
                duplicate = _duplicate_material(db, sub, sha)
                if duplicate is None:
                    material, ver, _job = create_material_with_file(
                        db, arch, sub, actor, Path(item.entry_path).name, data,
                        material_type_id=mt_id,
                        title=Path(item.entry_path).stem, stage_code=stage,
                    )
                    stored_rel = ver.stored_path
                    audit_log(db, actor, "BATCH_IMPORT", "material", material.id, {
                        "job_id": job.id, "item_id": item.id, "entry_path": item.entry_path,
                        "archive_id": arch.id, "submission_id": sub.id, "stage_code": stage,
                    })
                target_id = material.id if material is not None else duplicate.id
                # 条目回写实际使用的材料类型：确认响应和刷新后的 job.result 都靠它显示
                item.material_type_id = mt_id or (duplicate.type_id if duplicate is not None else material.type_id)
                item.status = "IMPORTED"
                item.material_id = target_id
                item.matched_archive_id = arch.id
                item.error = None
                item.updated_at = now()
                db.flush()
        except _ItemFailure as exc:
            error = str(exc)
        except AppError as exc:
            error = exc.biz_message
        except Exception as exc:  # 保存点已回滚，这里只记录原因
            error = str(exc)[:200]
        if error is not None:
            if stored_rel:
                # 材料行已随保存点回滚，文件不该留下
                store.remove(stored_rel)
            item.status = "FAILED"
            item.error = error[:200]
            item.updated_at = now()
            failed += 1
            out.append(_item_dict(item, type_map, already_imported=False))
            continue
        if material is None:
            already_imported += 1
            out.append(_item_dict(item, type_map, _material_stages(db, [item]),
                                  already_imported=True, note=DUPLICATE_NOTE))
        else:
            imported += 1
            out.append(_item_dict(item, type_map, _material_stages(db, [item]), already_imported=False))

    for sid in skip_ids or []:
        if sid in handled:
            continue
        handled.add(sid)
        item = db.query(BatchUploadItem).filter(BatchUploadItem.id == sid, BatchUploadItem.job_id == job.id).first()
        if item is None:
            # 其他任务的条目：不修改，只报失败
            failed += 1
            out.append(_missing_item(sid, "条目不属于该任务"))
            continue
        if item.status == "IMPORTED":
            already_imported += 1
            out.append(_item_dict(item, type_map, _material_stages(db, [item]), already_imported=True))
            continue
        item.status = "SKIPPED"
        item.error = None
        item.updated_at = now()
        skipped += 1
        out.append(_item_dict(item, type_map, _material_stages(db, [item]), already_imported=False))

    db.flush()
    return {
        "imported": imported, "already_imported": already_imported,
        "skipped": skipped, "failed": failed, "items": out,
    }


def _duplicate_material(db: Session, sub: Submission, sha: str):
    """提交包内当前版本内容相同的 ACTIVE 材料（重复上传同一文件时不重复入库）。"""
    return (
        db.query(Material)
        .join(MaterialVersion, MaterialVersion.id == Material.current_version_id)
        .filter(
            Material.submission_id == sub.id,
            Material.status == "ACTIVE",
            MaterialVersion.sha256 == sha,
        )
        .first()
    )


def rebuild_job_result(db: Session, job: Job, notes: dict | None = None) -> dict:
    """按数据库中的真实条目状态重建 job.result，确认后刷新页面看到的就是实际结果。

    `note` 不入库（本轮不改表结构）：沿用上一次 result 里已写的说明，再合并本次确认产生的
    说明，刷新后“相同文件已在该提交包中”之类的提示不会丢。
    """
    rows = (
        db.query(BatchUploadItem).filter(BatchUploadItem.job_id == job.id).order_by(BatchUploadItem.id).all()
    )
    type_map = {t.id: t for t in db.query(MaterialType).all()}
    material_stages = _material_stages(db, rows)
    base = job.result if isinstance(job.result, dict) else {}
    kept_notes = {
        row.get("item_id"): row.get("note")
        for row in (base.get("items") or [])
        if isinstance(row, dict) and row.get("note")
    }
    if notes:
        kept_notes.update(notes)
    return {
        "total": base.get("total", len(rows)),
        "matched": base.get("matched", sum(1 for r in rows if r.matched_archive_id)),
        "unmatched": base.get("unmatched", sum(1 for r in rows if not r.matched_archive_id)),
        "imported": sum(1 for r in rows if r.status == "IMPORTED"),
        "skipped": sum(1 for r in rows if r.status == "SKIPPED"),
        "failed": sum(1 for r in rows if r.status == "FAILED"),
        "items": [_item_dict(r, type_map, material_stages, note=kept_notes.get(r.id)) for r in rows],
    }


def _material_stages(db: Session, rows: list) -> dict[int, int]:
    ids = [r.material_id for r in rows if r.material_id]
    if not ids:
        return {}
    return {mid: stage for mid, stage in db.query(Material.id, Material.stage_code).filter(Material.id.in_(ids))}


def _missing_item(item_id, reason: str) -> dict:
    return {
        "item_id": item_id, "entry_path": None, "parsed_student_no": None, "matched_archive": None,
        "material_type": None, "status": "FAILED", "error": reason,
        "material_id": None, "stage_code": None, "note": None, "already_imported": False,
    }


def _parse_student_no(path: str) -> str | None:
    p = path.replace("\\", "/")
    m = re.search(r"(D\d{7}|\d{10,12}|[A-Z]\d{6,10})", p)
    return m.group(1) if m else None


def _parse_type_hint(name: str, types) -> str | None:
    for t in types:
        for kw in t.title_keywords or []:
            if kw and kw in name:
                return t.code
        if t.name and t.name in name:
            return t.code
    return None


def _item_dict(row: BatchUploadItem, type_map: dict, material_stages: dict | None = None,
               already_imported: bool | None = None, note: str | None = None) -> dict:
    mt = type_map.get(row.material_type_id)
    arch = row.matched_archive
    data = {
        "item_id": row.id, "entry_path": row.entry_path, "parsed_student_no": row.parsed_student_no,
        "matched_archive": {"id": arch.id, "real_name": arch.real_name} if arch else None,
        "material_type": mt.code if mt else row.parsed_type_hint,
        "status": row.status, "error": row.error,
        "material_id": row.material_id,
        "stage_code": (material_stages or {}).get(row.material_id),
        "note": note,
    }
    if already_imported is not None:
        # 确认响应里每条都带这个字段；识别结果与 job.result 不带（与设计示例一致）
        data["already_imported"] = already_imported
    return data
