from __future__ import annotations

import json
import time
from typing import Any, Optional

import httpx

from models import PromptTemplate, SystemSetting
from security import decrypt_field
from utils import get_setting


def llm_config(db) -> dict:
    cfg = get_setting(db, "ai", {})
    return cfg


def llm_enabled(db) -> bool:
    cfg = llm_config(db)
    return bool(cfg.get("llm_enabled") and (cfg.get("base_url") or "") and cfg.get("api_key_enc"))


def llm_api_key(db) -> str:
    cfg = llm_config(db)
    enc = cfg.get("api_key_enc") or ""
    if not enc:
        return ""
    return decrypt_field(enc) or ""


def chat_json(db, code: str, variables: dict, override: Optional[dict] = None) -> tuple[Optional[dict], Optional[str], float]:
    cfg = dict(llm_config(db))
    if override:
        cfg.update({k: v for k, v in override.items() if v is not None})
    base = (cfg.get("base_url") or "").rstrip("/")
    model = cfg.get("model") or ""
    key = override.get("api_key") if override and override.get("api_key") else llm_api_key(db)
    if not base or not model:
        return None, "未配置大模型", 0
    tpl = db.query(PromptTemplate).filter(PromptTemplate.code == code, PromptTemplate.is_active.is_(True)).first()
    if not tpl:
        sys_p, user_p = "只输出 JSON。", json.dumps(variables, ensure_ascii=False)
    else:
        sys_p = tpl.system_prompt
        user_p = tpl.user_prompt
        for k, v in variables.items():
            user_p = user_p.replace("{" + k + "}", str(v)[:6000])
    payload = {
        "model": model,
        "temperature": float(cfg.get("temperature") or 0.1),
        "messages": [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": user_p + "\n只输出 JSON。"},
        ],
    }
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    timeout = float(cfg.get("timeout_s") or 60)
    last_err = None
    t0 = time.time()
    # 调用方可通过 override 限制重试次数：批量语义核查失败即降级，不让任务长时间挂起
    for attempt in range(int(cfg.get("max_attempts") or 3)):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(f"{base}/chat/completions", json=payload, headers=headers)
            if resp.status_code >= 500:
                last_err = f"HTTP {resp.status_code}"
                time.sleep(0.5 * (2 ** attempt))
                continue
            if resp.status_code >= 400:
                return None, f"HTTP {resp.status_code}: {resp.text[:200]}", (time.time() - t0) * 1000
            data = resp.json()
            content = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
            parsed = _parse_json(content)
            if parsed is None and attempt == 0:
                last_err = "JSON 解析失败"
                continue
            return parsed, None, (time.time() - t0) * 1000
        except Exception as e:
            last_err = str(e)
            time.sleep(0.5 * (2 ** attempt))
    return None, last_err or "调用失败", (time.time() - t0) * 1000


def _parse_json(content: str) -> Optional[dict]:
    if not content:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None
