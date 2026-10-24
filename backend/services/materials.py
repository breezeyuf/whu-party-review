from __future__ import annotations

import difflib
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi.responses import Response
from sqlalchemy.orm import Session

from errors import conflict, too_large, unprocessable, unsupported
from models import (
    Job,
    Material,
    MaterialType,
    MaterialVersion,
    ParseResult,
    Submission,
    TimeNodeExtraction,
)
from security import detect_ext, sha256_bytes
from services import storage as store
from utils import get_setting, now


def _validate_upload(db, filename: str, data: bytes) -> tuple[str, str]:
    cfg = get_setting(db, "upload", {})
    max_mb = int(cfg.get("max_file_mb") or 20)
    if len(data) > max_mb * 1024 * 1024:
        raise too_large(f"文件超过 {max_mb} MB")
    ext, mime = detect_ext(filename, data[:16])
    allowed = cfg.get("allowed_ext", ["pdf", "jpg", "jpeg", "png", "docx"])
    allowed = {str(value).lower().lstrip(".") for value in (allowed or [])}
    if not ext or ext not in allowed:
        raise unsupported("文件格式不符合当前上传设置，或文件内容与扩展名不符")
    if ext == "docx":
        try:
            with zipfile.ZipFile(BytesIO(data)) as document:
                for name in ("[Content_Types].xml", "word/document.xml"):
                    entry = document.getinfo(name)
                    if entry.is_dir() or not entry.file_size:
                        raise ValueError("DOCX 内容为空")
        except (zipfile.BadZipFile, KeyError, ValueError):
            raise unsupported("文件不是有效的 DOCX 文档包") from None
    return ext, mime


def enqueue_job(db: Session, job_type: str, created_by: int, target_type=None, target_id=None, params=None, total=1, parent_id=None) -> Job:
    job = Job(
        job_type=job_type, status="QUEUED", parent_id=parent_id, target_type=target_type, target_id=target_id,
        params=params or {}, total=total, created_by=created_by, created_at=now(),
    )
    db.add(job)
    db.flush()
    return job


def create_material_with_file(
    db: Session, archive, submission: Submission, actor, filename: str, data: bytes,
    material_type_id: Optional[int] = None, title: Optional[str] = None, stage_code: Optional[int] = None,
    change_note: Optional[str] = None, issue_ids: Optional[list[int]] = None,
) -> tuple[Material, MaterialVersion, Job]:
    submission = db.query(Submission).filter(Submission.id == submission.id).with_for_update().populate_existing().one()
    if submission.status not in ("DRAFT", "RETURNED"):
        raise conflict("提交包审核中，不可上传材料")
    ext, mime = _validate_upload(db, filename, data)
    rel, sha, size = store.save_bytes(data, archive.id, ext)
    try:
        stage = stage_code or submission.stage_code
        mt = db.query(MaterialType).filter(MaterialType.id == material_type_id).first() if material_type_id else None
        material = Material(
            archive_id=archive.id, submission_id=submission.id, stage_code=stage,
            title=title or Path(filename).stem,
            declared_type_id=mt.id if mt else None,
            type_id=mt.id if mt else None,
            type_source="DECLARED" if mt else None,
            type_confidence=1.0 if mt else None,
            type_status="AUTO" if mt else "PENDING",
            version_count=1, status="ACTIVE", uploaded_by=actor.id,
            created_at=now(), updated_at=now(),
        )
        db.add(material)
        db.flush()
        ver = MaterialVersion(
            material_id=material.id, version_no=1, original_filename=filename, stored_path=rel,
            file_ext=ext, mime_type=mime, file_size=size, sha256=sha, change_note=change_note,
            parse_status="PENDING", uploaded_by=actor.id, uploaded_at=now(),
        )
        db.add(ver)
        db.flush()
        material.current_version_id = ver.id
        job = enqueue_job(db, "PARSE", actor.id, "material_version", ver.id, {"version_id": ver.id})
        db.flush()
    except Exception:
        # 文件已落盘但数据库写入失败：删掉刚写出的文件再抛出，避免留下孤儿文件
        store.remove(rel)
        raise
    return material, ver, job


def add_version(db, material: Material, actor, filename: str, data: bytes, change_note=None, issue_ids=None):
    sub = db.query(Submission).filter(Submission.id == material.submission_id).with_for_update().populate_existing().first()
    if not sub or sub.status not in ("DRAFT", "RETURNED"):
        raise conflict("提交包审核中，不可更新材料")
    # 行锁串行化同一材料的并发版本创建，避免 version_no 冲突
    locked = db.query(Material).filter(Material.id == material.id).with_for_update().populate_existing().first()
    if locked is not None:
        material = locked
    # 整改问题须属于当前材料或提交包（与问题回复接口同一口径），先校验再落盘
    target_issues = []
    if issue_ids:
        from models import Issue
        ids = issue_ids if isinstance(issue_ids, list) else [int(x) for x in str(issue_ids).split(",") if str(x).strip().isdigit()]
        for iid in ids:
            iss = db.query(Issue).filter(
                Issue.id == iid, Issue.submission_id == material.submission_id,
                Issue.is_active.is_(True),
                (Issue.material_id.is_(None)) | (Issue.material_id == material.id),
            ).first()
            if not iss:
                raise unprocessable("整改问题不属于当前材料或提交包")
            target_issues.append(iss)
    ext, mime = _validate_upload(db, filename, data)
    rel, sha, size = store.save_bytes(data, material.archive_id, ext)
    no = material.version_count + 1
    db.query(TimeNodeExtraction).filter(
        TimeNodeExtraction.material_id == material.id, TimeNodeExtraction.is_current.is_(True)
    ).update({"is_current": False})
    ver = MaterialVersion(
        material_id=material.id, version_no=no, original_filename=filename, stored_path=rel,
        file_ext=ext, mime_type=mime, file_size=size, sha256=sha, change_note=change_note,
        parse_status="PENDING", uploaded_by=actor.id, uploaded_at=now(),
    )
    db.add(ver)
    db.flush()
    material.current_version_id = ver.id
    material.version_count = no
    material.updated_at = now()
    responded = []
    for iss in target_issues:
        iss.response_type = "MODIFIED"
        iss.response_version_id = ver.id
        iss.responded_at = now()
        responded.append(iss.id)
    job = enqueue_job(db, "PARSE", actor.id, "material_version", ver.id, {"version_id": ver.id})
    return ver, job, responded


def file_response(ver: MaterialVersion, disposition: str = "inline") -> Response:
    data = store.read_bytes(ver.stored_path)
    fname = quote(ver.original_filename)
    dispo = "attachment" if disposition == "attachment" else "inline"
    return Response(
        content=data,
        media_type=ver.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f"{dispo}; filename*=UTF-8''{fname}"},
    )


def text_diff(from_text: str, to_text: str) -> dict:
    a = [p for p in re.split(r"\n+", from_text or "") if p is not None]
    b = [p for p in re.split(r"\n+", to_text or "") if p is not None]
    sm = difflib.SequenceMatcher(a=a, b=b)
    hunks = []
    stats = {"added": 0, "removed": 0, "changed": 0}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        op = {"replace": "replace", "delete": "delete", "insert": "insert", "equal": "equal"}[tag]
        if tag == "insert":
            stats["added"] += j2 - j1
        elif tag == "delete":
            stats["removed"] += i2 - i1
        elif tag == "replace":
            stats["changed"] += max(i2 - i1, j2 - j1)
        hunks.append({"op": op, "from_text": "\n".join(a[i1:i2]), "to_text": "\n".join(b[j1:j2]), "from_page": None, "to_page": None})
    return {"stats": stats, "hunks": hunks}
