from __future__ import annotations

import re
from pathlib import Path

from openpyxl import Workbook
from sqlalchemy.orm import Session

from models import Archive, BatchUploadItem, Job, MaterialType
from services.materials import create_material_with_file
from services.scope import scoped_archives
from services import storage as store
from utils import now


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


def process_batch_upload(db: Session, job: Job) -> None:
    params = job.params or {}
    zip_rel = params.get("zip_path")
    dest = f"tmp/batch_{job.id}"
    items = store.extract_zip_safe(zip_rel, dest)
    types = db.query(MaterialType).filter(MaterialType.is_active.is_(True)).all()
    result_items = []
    matched = unmatched = imported = 0
    for it in items:
        name = Path(it["entry_path"]).name
        student_no = _parse_student_no(it["entry_path"])
        type_hint = _parse_type_hint(name, types)
        arch = db.query(Archive).filter(Archive.student_no == student_no).first() if student_no else None
        status = "MATCHED" if arch else "UNMATCHED"
        row = BatchUploadItem(
            job_id=job.id, entry_path=it["entry_path"], temp_path=it["temp_path"],
            file_size=it["file_size"], parsed_student_no=student_no, parsed_type_hint=type_hint,
            matched_archive_id=arch.id if arch else None,
            match_method="DIRECTORY" if "/" in it["entry_path"].replace("\\", "/") else "FILENAME",
            material_type_id=next((t.id for t in types if t.code == type_hint), None),
            status=status, created_at=now(), updated_at=now(),
        )
        db.add(row)
        db.flush()
        if arch:
            matched += 1
        else:
            unmatched += 1
        result_items.append(_item_dict(row, arch, types))
    job.result = {"total": len(items), "matched": matched, "unmatched": unmatched, "imported": imported, "items": result_items}
    job.total = len(items)
    job.done_count = len(items)
    db.flush()


def assign_batch_items(db, job: Job, actor, assignments: list, skip_ids: list) -> dict:
    types = {t.id: t for t in db.query(MaterialType).all()}
    skip = set(skip_ids or [])
    imported = skipped = failed = 0
    out = []
    class Dummy:
        pass
    for a in assignments or []:
        item_id = a.get("item_id")
        item = db.query(BatchUploadItem).filter(BatchUploadItem.id == item_id, BatchUploadItem.job_id == job.id).first() if item_id else None
        if not item:
            failed += 1
            continue
        if item.id in skip:
            item.status = "SKIPPED"
            skipped += 1
            continue
        arch_id = a.get("archive_id")
        arch = scoped_archives(db.query(Archive), actor, db).filter(Archive.id == arch_id).first() if arch_id else None
        if not arch:
            item.status = "FAILED"
            item.error = "档案不存在或无权限"
            failed += 1
            out.append(_item_dict(item, None, list(types.values())))
            continue
        from models import Submission
        sub = db.query(Submission).filter(Submission.archive_id == arch.id, Submission.stage_code == arch.current_stage).first()
        if not sub:
            item.status = "FAILED"
            item.error = "无提交包"
            failed += 1
            out.append(_item_dict(item, arch, list(types.values())))
            continue
        data = store.read_bytes(item.temp_path)
        mt_id = a.get("material_type_id") or item.material_type_id
        try:
            # 单条导入用保存点隔离：失败只回滚该条，不污染整个会话
            with db.begin_nested():
                mat, ver, _ = create_material_with_file(
                    db, arch, sub, actor, Path(item.entry_path).name, data, material_type_id=mt_id, title=Path(item.entry_path).stem,
                )
            item.status = "IMPORTED"
            item.material_id = mat.id
            item.matched_archive_id = arch.id
            imported += 1
        except Exception as e:
            item.status = "FAILED"
            item.error = str(e)[:200]
            failed += 1
        out.append(_item_dict(item, arch, list(types.values())))
    for sid in skip:
        item = db.query(BatchUploadItem).filter(BatchUploadItem.id == sid).first()
        if item:
            item.status = "SKIPPED"
            skipped += 1
    db.flush()
    return {"imported": imported, "skipped": skipped, "failed": failed, "items": out}


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


def _item_dict(row: BatchUploadItem, arch, types) -> dict:
    mt = next((t for t in types if t.id == row.material_type_id), None) if not isinstance(types, dict) else types.get(row.material_type_id)
    if isinstance(types, dict):
        mt = types.get(row.material_type_id)
    return {
        "item_id": row.id, "entry_path": row.entry_path, "parsed_student_no": row.parsed_student_no,
        "matched_archive": {"id": arch.id, "real_name": arch.real_name} if arch else None,
        "material_type": mt.code if mt else row.parsed_type_hint, "status": row.status, "error": row.error,
    }
