from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden, gone, not_found
from models import ExportFile, Job
from schemas.common import ok
from services.audit import log
from services.dashboard import dashboard as dash
from services.materials import enqueue_job
from services.stats import ai_quality, overview, top_issues
from services.storage import read_bytes
from fastapi.responses import Response
from urllib.parse import quote
from utils import now

router = APIRouter(tags=["stats"])


@router.get("/dashboard")
def get_dashboard(batch_id: int | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    return ok(dash(db, actor, batch_id))


@router.get("/stats/overview")
def get_overview(batch_id: int | None = None, college_id: int | None = None, branch_id: int | None = None,
                 stage_code: int | None = None, date_from: str | None = None, date_to: str | None = None,
                 db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role == "STUDENT":
        raise forbidden()
    return ok(overview(db, actor, batch_id=batch_id, college_id=college_id, branch_id=branch_id, stage_code=stage_code,
                       date_from=date_from, date_to=date_to))


@router.get("/stats/top-issues")
def get_top(batch_id: int | None = None, college_id: int | None = None, branch_id: int | None = None,
            stage_code: int | None = None, date_from: str | None = None, date_to: str | None = None,
            limit: int = 10, group_by: str = "rule",
            db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role == "STUDENT":
        raise forbidden()
    return ok(top_issues(db, actor, limit, group_by, batch_id=batch_id, college_id=college_id, branch_id=branch_id,
                         stage_code=stage_code, date_from=date_from, date_to=date_to))


@router.get("/stats/ai-quality")
def get_aiq(batch_id: int | None = None, college_id: int | None = None, branch_id: int | None = None,
            stage_code: int | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role == "STUDENT":
        raise forbidden()
    return ok(ai_quality(db, actor, batch_id=batch_id, college_id=college_id, branch_id=branch_id, stage_code=stage_code))


@router.post("/stats/export")
def post_export(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    if actor.role not in ("ORG_ADMIN", "COLLEGE_REVIEWER"):
        raise forbidden()
    job = enqueue_job(db, "EXPORT", actor.id, "export", None, {
        "export_type": body.get("export_type") or "STATS_REPORT",
        "filters": body.get("filters") or {},
        "scope_college_id": actor.org_id if actor.role == "COLLEGE_REVIEWER" else None,
    })
    log(db, actor, "EXPORT", "export", job.id, body)
    return ok({"job_id": job.id})


@router.get("/exports/{eid}/download")
def download(eid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    ef = db.query(ExportFile).filter(ExportFile.id == eid).first()
    if not ef:
        raise not_found()
    if ef.created_by != actor.id and actor.role not in ("SYS_ADMIN", "ORG_ADMIN"):
        raise forbidden()
    if ef.expires_at and ef.expires_at < now():
        raise gone()
    data = read_bytes(ef.stored_path)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(ef.file_name)}"},
    )
