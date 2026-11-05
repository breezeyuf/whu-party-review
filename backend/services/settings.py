from __future__ import annotations

from copy import deepcopy
import math

from sqlalchemy.orm import Session

from errors import forbidden, unprocessable
from models import SystemSetting
from security import encrypt_field
from utils import get_setting, now
from ai.ocr import available_engines
from ai.llm import chat_json, validate_credential_options


ORG_KEYS = {"upload", "retention", "notification", "calendar"}
ADMIN_ONLY = {"ai", "ocr", "ocr_vision", "security", "worker", "delivery", "auth"}


def public_settings(db: Session) -> dict:
    out = {}
    for key in ("upload", "retention", "notification", "ai", "ocr", "ocr_vision", "security", "worker", "calendar", "delivery", "auth"):
        val = deepcopy(get_setting(db, key, {}))
        if key == 'auth':
            val = {'mode': 'demo', **val}
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
            from ai.ocr import configured_engine
            val['engine'] = configured_engine(val)
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
            raise unprocessable("配置组必须是对象")
        patch = dict(patch)
        if key == 'security':
            for name, upper in [('max_failed_login', 50), ('lock_minutes', 1440), ('access_token_minutes', 1440)]:
                if name in patch and (type(patch[name]) is not int or not 1 <= patch[name] <= upper):
                    raise unprocessable(f'{name} 须为 1 至 {upper} 的整数')
        if key == 'auth':
            from services.sessions import validate_auth_config
            from models import AuthSession, CasLoginState
            if set(patch) - {'mode', 'login_url', 'validate_url'}:
                raise unprocessable('认证配置包含未知字段')
            validate_auth_config({'mode': 'demo', **cur, **patch})
            if any(cur.get(name) != value for name, value in patch.items()):
                db.query(AuthSession).delete(synchronize_session=False)
                db.query(CasLoginState).delete(synchronize_session=False)
        if key == 'ai':
            for name in ('llm_enabled', 'desensitize'):
                if name in patch and type(patch[name]) is not bool:
                    raise unprocessable(f'{name} 须为开关值')
            for name, lower, upper in [('timeout_s',1,600),('max_concurrency',1,32),
                                       ('temperature',0,2),('classify_confidence_threshold',0,1)]:
                if name in patch and (type(patch[name]) not in (int,float) or not math.isfinite(patch[name]) or not lower <= patch[name] <= upper):
                    raise unprocessable(f'{name} 超出允许范围')
            if 'max_concurrency' in patch and type(patch['max_concurrency']) is not int:
                raise unprocessable('最大并发须为整数')
            if 'model' in patch and not isinstance(patch['model'], str):
                raise unprocessable('模型名须为文字')
        if key == 'retention' and 'material_years' in patch:
            if type(patch['material_years']) is not int or not 1<=patch['material_years']<=100:
                raise unprocessable('材料保留年数须为 1 至 100 的整数')
        if key == 'delivery':
            from services.delivery import update_config
            cur=update_config(cur,patch)
            patch={}
        if key == 'ocr':
            if 'engine' in patch and patch['engine'] not in ('none','auto','rapidocr'):
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
            if next_base:
                from services.model_network import destination
                destination(next_base)
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
    if target == 'ocr_vision':
        if override is not None:
            raise unprocessable('视觉 OCR 测试使用已保存配置，请先保存')
        from ai.ocr_review import test_connection
        return test_connection(db)
    if target == "ocr":
        if override is not None and not isinstance(override,dict):
            raise unprocessable('OCR 测试配置须为对象')
        from ai.ocr import probe
        return probe({**get_setting(db,'ocr',{}),**(override or {})})
    if target == "ocr_proofread_demo":
        # Fixed synthetic input only. No material ID, uploaded text, or image is
        # accepted by this settings test endpoint.
        sample = "今年是2025年，也是抗5战胜利80周年。"
        from time import monotonic
        start = monotonic()
        result, err, _ = chat_json(db, "OCR_PROOFREAD_DEMO", {"text": sample}, override)
        if err:
            return {"ok": False, "latency_ms": int((monotonic() - start) * 1000),
                    "sample": sample, "corrections": [], "message": err}
        corrections = result.get("corrections", [])
        if any(item["original"] not in sample for item in corrections):
            return {"ok": False, "latency_ms": int((monotonic() - start) * 1000),
                    "sample": sample, "corrections": [], "message": "模型建议未能对应虚构 OCR 原文"}
        return {"ok": True, "latency_ms": int((monotonic() - start) * 1000),
                "model": get_setting(db, "ai", {}).get("model"), "sample": sample,
                "corrections": corrections, "message": "虚构文本校对完成；结果仅为建议，未修改任何材料"}
    parsed, err, ms = chat_json(db, "CONNECTION_TEST", {"text": "Return a JSON object: {\"ok\":true}"}, override)
    return {"ok": err is None, "latency_ms": int(ms), "model": (override or {}).get("model") or get_setting(db, "ai", {}).get("model"), "message": err or "ok"}
