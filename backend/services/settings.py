from __future__ import annotations

from copy import deepcopy

from sqlalchemy.orm import Session

from errors import forbidden, unprocessable
from models import SystemSetting
from security import encrypt_field
from utils import get_setting, now
from ai.ocr import available_engines
from ai.llm import chat_json, validate_credential_options


ORG_KEYS = {"upload", "retention", "notification", "calendar"}
ADMIN_ONLY = {"ai", "ocr", "ocr_vision", "security", "worker", "delivery"}


def public_settings(db: Session) -> dict:
    out = {}
    for key in ("upload", "retention", "notification", "ai", "ocr", "ocr_vision", "security", "worker", "calendar", "delivery"):
        val = deepcopy(get_setting(db, key, {}))
        if key == 'delivery':
            from services.delivery import public_config
            val=public_config(val)
        if key == 'ocr_vision':
            from ai.ocr_review import DEFAULTS
            val = {**DEFAULTS, **val}
        if key in ("ai", "ocr_vision"):
            enc = val.pop("api_key_enc", None)
            val.pop("api_key_base_url", None)
            val["api_key_set"] = bool(enc)
            if key == 'ai':
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
        cur = deepcopy(row.value) if row and isinstance(row.value, dict) else {}
        if not isinstance(patch, dict):
            if key in ("ai", "ocr_vision"):
                raise unprocessable("大模型配置必须是对象")
            continue
        patch = dict(patch)
        if key == 'retention' and 'material_years' in patch:
            if type(patch['material_years']) is not int or not 1<=patch['material_years']<=100:
                raise unprocessable('材料保留年数须为 1 至 100 的整数')
        if key == 'delivery':
            from services.delivery import update_config
            cur=update_config(cur,patch)
            patch={}
        if key == 'ocr':
            import math
            if 'engine' in patch and patch['engine'] not in ('none','auto','rapidocr','paddleocr'):
                raise unprocessable('不支持的 OCR 引擎')
            for name, lower, upper in [('min_dpi',72,300),('blur_threshold',0,100000),('timeout_s',1,600)]:
                if name in patch and (type(patch[name]) not in (int,float) or not math.isfinite(patch[name]) or not lower <= patch[name] <= upper):
                    raise unprocessable(f'{name} 超出允许范围')
        if key == 'ocr_vision':
            from ai.ocr_review import validate_config
            validate_config(patch)
        if key in ("ai", "ocr_vision"):
            validate_credential_options(patch)
            # A stored credential belongs to its saved destination, including
            # scheme, port and tenant path. Saving settings must not rebind it.
            previous_raw = cur.get("base_url")
            previous_base = previous_raw.strip().rstrip("/") if isinstance(previous_raw, str) else ""
            next_base = (patch.get("base_url") if patch.get("base_url") is not None else previous_base)
            next_base = next_base.strip().rstrip("/")
            if cur.get("api_key_enc") and next_base != previous_base and patch.get("api_key") is None:
                raise unprocessable("更换模型接口地址时，请重新填写密钥；无认证接口请显式清空密钥")
            patch.pop("api_key_enc", None)
            patch.pop("api_key_base_url", None)
            if "base_url" in patch:
                patch["base_url"] = next_base
            if cur.get("api_key_enc"):
                cur.setdefault("api_key_base_url", previous_base)
            if patch.get("api_key") is not None:
                cur["api_key_base_url"] = next_base if patch["api_key"] else ""
        if key in ("ai", "ocr_vision") and "api_key" in patch:
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
    if target == 'ocr_vision':
        if override is not None:
            raise unprocessable('视觉 OCR 测试使用已保存配置，请先保存')
        from ai.ocr_review import test_connection
        return test_connection(db)
    if target == "ocr":
        engines = available_engines()
        if not engines:
            return {"ok": False, "latency_ms": int((time.time()-t0)*1000), "message": "未安装 OCR 引擎，尚不能执行识别测试"}
        import fitz
        from ai.ocr import ocr_pixmap
        document = fitz.open()
        try:
            page = document.new_page(width=500, height=180)
            page.insert_text((40,85), 'WORKBENCH OCR TEST 2026', fontsize=22)
            page.insert_text((40,125), '虚构学生材料 申请日期', fontname='china-s', fontsize=20)
            from ai.ocr import settings as ocr_settings
            token = ocr_settings.set({**get_setting(db, 'ocr', {}), **(override or {})})
            try:
                extracted, blocks, engine, error = ocr_pixmap(page.get_pixmap(matrix=fitz.Matrix(2,2)))
            finally:
                ocr_settings.reset(token)
            ok = not error and '2026' in extracted and '学生' in extracted
            return {"ok":bool(ok), "latency_ms":int((time.time()-t0)*1000), "message": error or (f"{engine} 已完成内置图片识别" if ok else "引擎未正确识别内置测试图片")}
        finally:
            document.close()
    parsed, err, ms = chat_json(db, "CONNECTION_TEST", {"text": "Return a JSON object: {\"ok\":true}"}, override)
    return {"ok": err is None, "latency_ms": int(ms), "model": (override or {}).get("model") or get_setting(db, "ai", {}).get("model"), "message": err or "ok"}
