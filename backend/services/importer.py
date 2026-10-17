from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook, load_workbook
from sqlalchemy.orm import Session

from errors import unprocessable
from models import Archive, BatchUploadItem, Job, MaterialType, Org, User, UserRole
from security import hash_password, mask_phone, encrypt_field, random_password
from services.materials import create_material_with_file
from services.scope import scoped_archives
from services.users import PRIVILEGED, can_manage_user
from services import storage as store
from services.timeline import merge_archive_nodes
from utils import as_date, now
from models import TimeNodeExtraction

VALID_ROLES = {"STUDENT", "BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN", "SYS_ADMIN"}


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
    wb = load_workbook(BytesIO(data), data_only=True)
    errors = []
    created_users = created_archives = imported_nodes = 0
    total = 0
    valid = 0
    passwords = []
    if "用户" in wb.sheetnames:
        ws = wb["用户"]
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        total += len(rows)
        for i, row in enumerate(rows, start=2):
            if not any(row):
                continue
            username, real_name, gender, org_code, role, phone, email = (list(row) + [None] * 7)[:7]
            if not username or not real_name:
                errors.append({"sheet": "用户", "row": i, "column": "username", "message": "必填"})
                continue
            org = db.query(Org).filter(Org.code == str(org_code)).first() if org_code else None
            if not org:
                errors.append({"sheet": "用户", "row": i, "column": "org_code", "message": "组织不存在"})
                continue
            if not can_manage_user(actor, org):
                errors.append({"sheet": "用户", "row": i, "column": "org_code", "message": "无权在该组织下创建用户"})
                continue
            role_name = str(role or "STUDENT").strip() or "STUDENT"
            if role_name not in VALID_ROLES:
                errors.append({"sheet": "用户", "row": i, "column": "role", "message": f"未知角色 {role_name}"})
                continue
            if role_name in PRIVILEGED and actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
                errors.append({"sheet": "用户", "row": i, "column": "role", "message": "不能授予组织部/系统管理员角色"})
                continue
            valid += 1
            if dry_run:
                continue
            if db.query(User).filter(User.username == str(username)).first():
                continue
            pwd = random_password()
            u = User(
                username=str(username), password_hash=hash_password(pwd), real_name=str(real_name),
                gender=gender, org_id=org.id, email=str(email) if email else None,
                phone_enc=encrypt_field(str(phone) if phone else None), phone_masked=mask_phone(str(phone) if phone else None),
                must_change_password=True, created_at=now(), updated_at=now(),
            )
            db.add(u)
            db.flush()
            db.add(UserRole(user_id=u.id, role=role_name, org_id=org.id, created_at=now()))
            created_users += 1
            passwords.append((username, pwd))
    if "学生档案" in wb.sheetnames:
        ws = wb["学生档案"]
        headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue
            rec = dict(zip(headers, row))
            total += 1
            if not rec.get("student_no") or not rec.get("real_name"):
                errors.append({"sheet": "学生档案", "row": i, "column": "student_no", "message": "必填"})
                continue
            valid += 1
            if dry_run:
                continue
            branch = db.query(Org).filter(Org.code == str(rec.get("branch_code"))).first()
            if not branch:
                errors.append({"sheet": "学生档案", "row": i, "column": "branch_code", "message": "支部不存在"})
                continue
            if not can_manage_user(actor, branch):
                errors.append({"sheet": "学生档案", "row": i, "column": "branch_code", "message": "无权在该支部下建档案"})
                continue
            user = db.query(User).filter(User.username == str(rec["student_no"])).first()
            if not user:
                pwd = random_password()
                user = User(
                    username=str(rec["student_no"]), password_hash=hash_password(pwd),
                    real_name=str(rec["real_name"]), gender=rec.get("gender"), org_id=branch.id,
                    must_change_password=True, created_at=now(), updated_at=now(),
                )
                db.add(user)
                db.flush()
                db.add(UserRole(user_id=user.id, role="STUDENT", org_id=branch.id, created_at=now()))
                passwords.append((user.username, pwd))
                created_users += 1
            if db.query(Archive).filter(Archive.student_no == str(rec["student_no"])).first():
                continue
            college = db.query(Org).filter(Org.id == branch.parent_id).first()
            arch = Archive(
                student_user_id=user.id, student_no=str(rec["student_no"]), real_name=str(rec["real_name"]),
                gender=rec.get("gender"), ethnicity=rec.get("ethnicity"), birth_date=as_date(rec.get("birth_date")),
                native_place=rec.get("native_place"), major=rec.get("major"), class_name=rec.get("class_name"),
                college_id=college.id if college else branch.id, branch_id=branch.id, batch_id=batch_id,
                current_stage=1, status="ACTIVE", anon_code=f"A{rec['student_no']}", data_source="IMPORT",
                created_by=actor.id, created_at=now(), updated_at=now(),
            )
            db.add(arch)
            db.flush()
            created_archives += 1
            from models import Submission
            db.add(Submission(
                archive_id=arch.id, stage_code=1, batch_id=batch_id, college_id=arch.college_id,
                branch_id=arch.branch_id, status="DRAFT", round_no=1, ai_status="NONE",
                created_at=now(), updated_at=now(),
            ))
            for k, v in rec.items():
                if k and str(k).startswith("T") and v:
                    d = as_date(v)
                    if d:
                        db.add(TimeNodeExtraction(
                            archive_id=arch.id, node_code=str(k), value_date=d, method="IMPORT",
                            is_current=True, created_at=now(),
                        ))
                        imported_nodes += 1
            merge_archive_nodes(db, arch.id)
    if errors and not dry_run:
        db.rollback()
        raise unprocessable("导入存在错误", errors)
    result = {
        "total": total, "valid": valid, "created_users": created_users,
        "created_archives": created_archives, "imported_nodes": imported_nodes,
        "errors": errors,
    }
    if passwords and not dry_run:
        result["initial_passwords"] = [{"username": a, "password": b} for a, b in passwords]
    return result


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
