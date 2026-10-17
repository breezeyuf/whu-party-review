from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import APP_VERSION
from database import get_db
from ai.llm import llm_enabled
from ai.ocr import available_engines
from schemas.common import ok

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db_ok = "ok"
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_ok = "error"
    ocr = available_engines()
    return ok({
        "status": "ok", "db": db_ok, "version": APP_VERSION,
        "llm_enabled": llm_enabled(db), "ocr_engine": ocr[0] if ocr else "none",
    })
