from __future__ import annotations

from copy import deepcopy

from sqlalchemy.orm import Session

from errors import forbidden, unprocessable
from models import SystemSetting
from security import encrypt_field
from utils import get_setting, now
from ai.ocr import available_engines
from ai.llm import chat_json, llm_enabled


ORG_KEYS = {"upload", "retention", "notification", "calendar"}
ADMIN_ONLY = {"ai", "ocr", "security", "worker"}


def public_settings(db: Session) -> dict:
    out = {}
    for key in ("upload", "retention", "notification", "ai", "ocr", "security", "worker", "calendar"):
        val = deepcopy(get_setting(db, key, {}))
        if key == "ai":
            enc = val.pop("api_key_enc", None)
            val["api_key_set"] = bool(enc)
            val["llm_enabled"] = bool(val.get("llm_enabled"))
        if key == "ocr":
            val["available_engines"] = available_engines()
        out[key] = val
    return out


def update_settings(db: Session, actor, body: dict) -> dict:
    for key, patch in (body or {}).items():
        if key in ADMIN_ONLY and actor.role != "SYS_ADMIN":
            raise forbidden("该项仅系统管理员可改")
        if key not in ORG_KEYS and key not in ADMIN_ONLY:
            raise unprocessable(f"未知配置 {key}")
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        cur = deepcopy(row.value) if row else {}
        if not isinstance(patch, dict):
            continue
        if key == "ai" and "api_key" in patch:
            raw = patch.pop("api_key")
            if raw == "":
                cur["api_key_enc"] = ""
            elif raw is not None:
                cur["api_key_enc"] = encrypt_field(raw)
        cur.update({k: v for k, v in patch.items() if v is not None})
        if row:
            row.value = cur
            row.updated_by = actor.id
            row.updated_at = now()
        else:
            db.add(SystemSetting(key=key, value=cur, updated_by=actor.id, updated_at=now()))
    db.flush()
    return public_settings(db)


def test_ai(db: Session, target: str, override: dict | None = None) -> dict:
    import time
    t0 = time.time()
    if target == "ocr":
        engines = available_engines()
        return {"ok": bool(engines), "latency_ms": int((time.time() - t0) * 1000), "message": "可用引擎：" + (",".join(engines) or "无")}
    parsed, err, ms = chat_json(db, "CLASSIFY", {"types": "TEST", "text": "ping"}, override)
    return {"ok": err is None, "latency_ms": int(ms), "model": (override or {}).get("model") or get_setting(db, "ai", {}).get("model"), "message": err or "ok"}
