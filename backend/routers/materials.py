from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import conflict, forbidden, not_found, unprocessable
from models import (
    AiReport,
    Archive,
    BatchUploadItem,
    ChecklistItem,
    Issue,
    Job,
    Material,
    MaterialType,
    MaterialVersion,
    ParseResult,
    Submission,
    TimeNodeExtraction,
)
from schemas.common import ok
from services.audit import log
from services.importer import assign_batch_items
from services.materials import add_version, create_material_with_file, enqueue_job, file_response, text_diff
from services.scope import can_review, ensure_archive_access, ensure_submission_access, scoped_archives
from services.storage import save_tmp
from services.timeline import merge_archive_nodes
from ai.checks.completeness import expected_count, run_completeness
from ai.parser import render_page_png
from utils import get_setting, now
from config import STORAGE_DIR
from pathlib import Path

router = APIRouter(tags=["materials"])


def _editable_submission(db, actor, material, *, reviewer=False):
    sub = ensure_submission_access(db, actor, material.submission_id)
    sub = db.query(Submission).filter(Submission.id == sub.id).with_for_update().populate_existing().one()
    if material.status != "ACTIVE":
        raise conflict("已删除材料不可修改")
    if actor.role in ("STUDENT", "BRANCH_REVIEWER") and sub.status in ("DRAFT", "RETURNED"):
        return sub
    if reviewer and can_review(sub, actor, db):
        return sub
    raise forbidden("当前角色或状态不可修改材料")


def _ver_brief(db, v: MaterialVersion, is_current=False) -> dict:
    up = None
    if v.uploaded_by:
        from models import User
        u = db.query(User).filter(User.id == v.uploaded_by).first()
        up = u.real_name if u else None
    return {
        "id": v.id, "version_no": v.version_no, "original_filename": v.original_filename,
        "file_ext": v.file_ext, "file_size": v.file_size, "sha256": v.sha256, "page_count": v.page_count,
        "change_note": v.change_note, "parse_status": v.parse_status, "parse_error": v.parse_error,
        "is_frozen": v.is_frozen, "uploaded_by_name": up, "uploaded_at": v.uploaded_at.isoformat() if v.uploaded_at else None,
        "is_current": is_current,
    }


@router.post("/archives/{aid}/materials")
async def upload_material(
    aid: int, file: UploadFile = File(...), material_type_id: str | None = Form(None),
    stage_code: str | None = Form(None), title: str | None = Form(None),
    request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user),
):
    arch = ensure_archive_access(db, actor, aid, request)
    if actor.role not in ("STUDENT", "BRANCH_REVIEWER"):
        raise forbidden("仅学生本人或本支部可上传材料")
    sub = db.query(Submission).filter(Submission.archive_id == aid, Submission.stage_code == (int(stage_code) if stage_code else arch.current_stage)).first()
    if not sub:
        raise not_found("提交包不存在")
    if sub.status not in ("DRAFT", "RETURNED") and actor.role == "STUDENT":
        raise conflict("提交包审核中，不可上传")
    data = await file.read()
    mt = int(material_type_id) if material_type_id else None
    mat, ver, job = create_material_with_file(db, arch, sub, actor, file.filename or "file", data, mt, title, int(stage_code) if stage_code else None)
    log(db, actor, "UPLOAD", "material", mat.id, {"filename": file.filename})
    return ok({"material": _material_dict(db, mat), "version": _ver_brief(db, ver, True), "parse_job_id": job.id})


@router.get("/archives/{aid}/materials")
def list_materials(aid: int, stage_code: int | None = None, include_deleted: bool = False,
                   request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    arch = ensure_archive_access(db, actor, aid, request)
    sc = stage_code or arch.current_stage
    sub = db.query(Submission).filter(Submission.archive_id == aid, Submission.stage_code == sc).first()
    mats = db.query(Material).filter(Material.archive_id == aid, Material.stage_code == sc)
    if not include_deleted:
        mats = mats.filter(Material.status == "ACTIVE")
    mats = mats.all()
    from services.timeline import node_map_for_archive
    from ai.dsl import NodeVal
    from utils import as_date
    nm = node_map_for_archive(db, aid)
    nodes = {}
    for c, n in nm.items():
        nodes[c] = type("N", (), {"date": as_date(n.get("date")), "end": as_date(n.get("end")), "hours": n.get("hours"),
                                  "seq": n.get("seq") or [], "missing": not n.get("date")})()
    items = db.query(ChecklistItem).filter(ChecklistItem.stage_code == sc, ChecklistItem.is_active.is_(True)).order_by(ChecklistItem.sort_order).all()
    today = now().date()
    batch_end = arch.batch.end_date if arch.batch else None
    min_tail = int(get_setting(db, "calendar", {}).get("period_min_tail_days", 30))
    grouped = []
    used = set()
    for it in items:
        matched = [m for m in mats if m.type_id == it.material_type_id and m.status == "ACTIVE"]
        used.update(m.id for m in matched)
        expected = expected_count(it, nodes, batch_end, today, min_tail)
        grouped.append({
            "checklist_item_id": it.id,
            "material_type": {"id": it.material_type.id, "code": it.material_type.code, "name": it.material_type.name},
            "required": it.is_required, "expected_count": expected, "actual_count": len(matched),
            "missing_count": max(0, expected - len(matched)), "requirement_text": it.requirement_text,
            "materials": [_material_list_item(db, m) for m in matched],
        })
    unclassified = [_material_list_item(db, m) for m in mats if not m.type_id and m.status == "ACTIVE"]
    extra = [_material_list_item(db, m) for m in mats if m.id not in used and m.type_id and m.status == "ACTIVE"]
    return ok([{"stage_code": sc, "checklist": grouped, "unclassified": unclassified, "extra": extra}])


def _material_list_item(db, m: Material) -> dict:
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == m.current_version_id).first() if m.current_version_id else None
    open_n = db.query(Issue).filter(Issue.material_id == m.id, Issue.is_active.is_(True)).count()
    return {
        "id": m.id, "title": m.title, "type_status": m.type_status, "type_confidence": m.type_confidence,
        "current_version": {
            "id": ver.id, "version_no": ver.version_no, "parse_status": ver.parse_status,
            "page_count": ver.page_count, "uploaded_at": ver.uploaded_at.isoformat() if ver.uploaded_at else None,
        } if ver else None,
        "open_issue_count": open_n,
    }


def _material_dict(db, m: Material) -> dict:
    t = m.type
    dt = m.declared_type
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == m.current_version_id).first() if m.current_version_id else None
    sub = db.query(Submission).filter(Submission.id == m.submission_id).first()
    return {
        "id": m.id, "archive_id": m.archive_id, "submission_id": m.submission_id, "stage_code": m.stage_code,
        "title": m.title, "type": {"id": t.id, "code": t.code, "name": t.name} if t else None,
        "declared_type": {"id": dt.id, "code": dt.code, "name": dt.name} if dt else None,
        "type_source": m.type_source, "type_confidence": m.type_confidence, "type_status": m.type_status,
        "version_count": m.version_count,
        "current_version": _ver_brief(db, ver, True) if ver else None,
        "editable": bool(sub and sub.status in ("DRAFT", "RETURNED")),
    }


@router.get("/materials/{mid}")
def get_material(mid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    return ok(_material_dict(db, m))


@router.delete("/materials/{mid}")
def delete_material(mid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    sub = _editable_submission(db, actor, m)
    if sub.status not in ("DRAFT", "RETURNED"):
        raise conflict("审核中不可删除")
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == m.current_version_id).first() if m.current_version_id else None
    if ver and ver.is_frozen:
        raise conflict("材料已随提交包提交，不可删除")
    m.status = "DELETED"
    m.deleted_at = now()
    m.deleted_by = actor.id
    db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_id == mid).update({"is_current": False})
    db.flush()
    merge_archive_nodes(db, m.archive_id)
    log(db, actor, "MATERIAL_DELETE", "material", mid, {})
    return ok({})


@router.get("/materials/{mid}/file")
def get_file(mid: int, version_id: int | None = None, disposition: str = "inline",
             request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    vid = version_id or m.current_version_id
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == vid, MaterialVersion.material_id == mid).first()
    if not ver:
        raise not_found()
    return file_response(ver, disposition)


@router.get("/materials/{mid}/pages/{n}")
def get_page(mid: int, n: int, version_id: int | None = None, scale: float = 1.5,
             request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    vid = version_id or m.current_version_id
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == vid, MaterialVersion.material_id == mid).first()
    if not ver:
        raise not_found()
    pr = db.query(ParseResult).filter(ParseResult.version_id == vid).first()
    preview = (pr.preview_pdf_path if pr and pr.preview_pdf_path else ver.stored_path) if ver else None
    # 预览缓存可能被清理（storage/previews 属派生文件），缺失时回退到材料原文
    if preview and not (STORAGE_DIR / preview).is_file():
        preview = ver.stored_path
    if not preview:
        raise not_found()
    scale = min(3, max(0.5, scale))
    cache = STORAGE_DIR / "cache" / f"{vid}_{n}_{scale}.png"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.is_file():
        data = cache.read_bytes()
        # still need headers; re-open for dims
        png, count, w, h = render_page_png(preview, n, scale)
        return Response(content=data, media_type="image/png", headers={"X-Page-Count": str(count), "X-Page-Width": str(w), "X-Page-Height": str(h)})
    png, count, w, h = render_page_png(preview, n, scale)
    cache.write_bytes(png)
    return Response(content=png, media_type="image/png", headers={"X-Page-Count": str(count), "X-Page-Width": str(w), "X-Page-Height": str(h)})


@router.post("/materials/{mid}/versions")
async def post_version(mid: int, file: UploadFile = File(...), change_note: str | None = Form(None),
                       issue_ids: str | None = Form(None), request: Request = None,
                       db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    _editable_submission(db, actor, m)
    data = await file.read()
    ver, job, responded = add_version(db, m, actor, file.filename or "file", data, change_note, issue_ids)
    return ok({"version": _ver_brief(db, ver, True), "parse_job_id": job.id, "responded_issue_ids": responded})


@router.get("/materials/{mid}/versions")
def list_versions(mid: int, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    vers = db.query(MaterialVersion).filter(MaterialVersion.material_id == mid).order_by(MaterialVersion.version_no).all()
    out = []
    for v in vers:
        d = _ver_brief(db, v, v.id == m.current_version_id)
        d["report_ids"] = []
        out.append(d)
    return ok(out)


@router.get("/materials/{mid}/parsed")
def get_parsed(mid: int, version_id: int | None = None, request: Request = None,
               db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    vid = version_id or m.current_version_id
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == vid, MaterialVersion.material_id == mid).first() if vid else None
    if vid and not ver:
        raise not_found("材料版本不存在")
    pr = db.query(ParseResult).filter(ParseResult.version_id == vid).first() if vid else None
    exs = db.query(TimeNodeExtraction).filter(TimeNodeExtraction.material_version_id == vid, TimeNodeExtraction.is_current.is_(True)).all() if vid else []
    return ok({
        "material_id": mid, "version_id": vid, "version_no": ver.version_no if ver else None,
        "parser": pr.parser if pr else None, "ocr_engine": pr.ocr_engine if pr else None,
        "page_count": ver.page_count if ver else 0,
        "full_text": pr.full_text if pr else "", "corrected_text": pr.corrected_text if pr else None,
        "pages": pr.pages if pr else [], "visual_marks": pr.visual_marks if pr else {},
        "extracted_fields": pr.extracted_fields if pr else {}, "corrected_fields": pr.corrected_fields if pr else None,
        "extractions": [{
            "id": e.id, "node_code": e.node_code, "seq_index": e.seq_index,
            "date": e.value_date.isoformat() if e.value_date else None,
            "end_date": e.value_end_date.isoformat() if e.value_end_date else None,
            "hours": e.hours, "raw_text": e.raw_text, "page_no": e.page_no, "bbox": e.bbox,
            "method": e.method, "confidence": e.confidence, "invalid_reason": e.invalid_reason,
        } for e in exs],
        "warnings": pr.warnings if pr else [],
    })


@router.put("/materials/{mid}/parsed")
def put_parsed(mid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "CROSS_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    sub = _editable_submission(db, actor, m, reviewer=True)
    vid = body.get("version_id") or m.current_version_id
    if vid != m.current_version_id:
        raise conflict("历史材料版本只读")
    if body.get("extractions") and not (body.get("reason") or "").strip():
        raise unprocessable("时间节点校正须填写原因")
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == vid, MaterialVersion.material_id == mid).first() if vid else None
    if vid and not ver:
        raise not_found("材料版本不存在")
    pr = db.query(ParseResult).filter(ParseResult.version_id == vid).first()
    if not pr:
        raise not_found()
    if "corrected_text" in body:
        pr.corrected_text = body.get("corrected_text")
    if "corrected_fields" in body:
        pr.corrected_fields = body.get("corrected_fields")
    pr.corrected_by = actor.id
    pr.corrected_at = now()
    pr.updated_at = now()
    for ex in body.get("extractions") or []:
        if ex.get("delete") and ex.get("extraction_id"):
            row = db.query(TimeNodeExtraction).filter(
                TimeNodeExtraction.id == ex["extraction_id"], TimeNodeExtraction.material_version_id == vid
            ).first()
            if row:
                row.is_current = False
            continue
        from utils import as_date
        if ex.get("extraction_id"):
            row = db.query(TimeNodeExtraction).filter(
                TimeNodeExtraction.id == ex["extraction_id"], TimeNodeExtraction.material_version_id == vid
            ).first()
            if row:
                row.value_date = as_date(ex.get("date"))
                row.value_end_date = as_date(ex.get("end_date"))
                row.hours = ex.get("hours")
                row.method = "MANUAL"
        else:
            db.add(TimeNodeExtraction(
                archive_id=m.archive_id, node_code=ex["node_code"], material_id=m.id, material_version_id=vid,
                seq_index=ex.get("seq_index") or 0, value_date=as_date(ex.get("date")),
                value_end_date=as_date(ex.get("end_date")), hours=ex.get("hours"), method="MANUAL",
                is_current=True, created_at=now(),
            ))
    merge_archive_nodes(db, m.archive_id)
    log(db, actor, "PARSE_CORRECT", "material", mid, {"reason": body.get("reason"), "version_id": vid})
    job_id = None
    if body.get("recheck"):
        job = enqueue_job(db, "AI_CHECK", actor.id, "submission", m.submission_id,
                          {"submission_id": m.submission_id, "trigger_type": "REVIEW"})
        job_id = job.id
    data = {"ok": True}
    if job_id:
        data["job_id"] = job_id
    return ok(data)


@router.put("/materials/{mid}/type")
def set_type(mid: int, body: dict, request: Request, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    sub = _editable_submission(db, actor, m, reviewer=True)
    mt = db.query(MaterialType).filter(MaterialType.id == body.get("material_type_id")).first()
    if not mt:
        raise unprocessable("材料类型不存在")
    m.type_id = mt.id
    m.type_source = "MANUAL"
    m.type_status = "CONFIRMED"
    m.type_confidence = 1.0
    m.updated_at = now()
    log(db, actor, "MATERIAL_TYPE_CONFIRM", "material", mid, {"type_id": mt.id})
    return ok(_material_dict(db, m))


@router.get("/materials/{mid}/diff")
def diff(mid: int, from_version: int | None = None, to_version: int | None = None,
         request: Request = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    m = db.query(Material).filter(Material.id == mid).first()
    if not m:
        raise not_found()
    ensure_archive_access(db, actor, m.archive_id, request)
    vers = db.query(MaterialVersion).filter(MaterialVersion.material_id == mid).order_by(MaterialVersion.version_no).all()
    if len(vers) < 1:
        return ok({"from": None, "to": None, "stats": {}, "hunks": []})
    fv = db.query(MaterialVersion).filter(MaterialVersion.id == from_version, MaterialVersion.material_id == mid).first() if from_version else None
    tv = db.query(MaterialVersion).filter(MaterialVersion.id == to_version, MaterialVersion.material_id == mid).first() if to_version else None
    if fv is None:
        fv = vers[-2] if len(vers) > 1 else vers[0]
    if tv is None:
        tv = vers[-1]
    ft = (db.query(ParseResult).filter(ParseResult.version_id == fv.id).first() or ParseResult(full_text=""))
    tt = (db.query(ParseResult).filter(ParseResult.version_id == tv.id).first() or ParseResult(full_text=""))
    d = text_diff(getattr(ft, "full_text", "") or "", getattr(tt, "full_text", "") or "")
    return ok({"from": {"version_no": fv.version_no}, "to": {"version_no": tv.version_no}, **d})


@router.post("/materials/batch-upload")
async def batch_upload(file: UploadFile = File(...), batch_id: str | None = Form(None), stage_code: str | None = Form(None),
                       db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    data = await file.read()
    cfg = get_setting(db, "upload", {"max_zip_mb": 500})
    if len(data) > int(cfg.get("max_zip_mb") or 500) * 1024 * 1024:
        from errors import too_large
        raise too_large("ZIP 超过上限")
    rel = save_tmp(data, file.filename or "batch.zip")
    job = enqueue_job(db, "BATCH_UPLOAD", actor.id, "batch", int(batch_id) if batch_id else None,
                      {"zip_path": rel, "batch_id": int(batch_id) if batch_id else None, "stage_code": int(stage_code) if stage_code else None})
    return ok({"job_id": job.id})


@router.put("/materials/batch-upload/{job_id}/assign")
def assign(job_id: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("BRANCH_REVIEWER", "COLLEGE_REVIEWER", "ORG_ADMIN"):
        raise forbidden()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise not_found()
    result = assign_batch_items(db, job, actor, body.get("assignments") or [], body.get("skip_item_ids") or [])
    return ok(result)
