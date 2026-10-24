from __future__ import annotations

import json
import re
import time
from typing import Any, Optional

import httpx
from pydantic import ValidationError

from ai.desensitize import desensitize_text
from ai.llm_output import ChatCompletionOutput, validate_task_output
from models import Archive, PromptTemplate
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


def chat_json(
    db, code: str, variables: dict, override: Optional[dict] = None, *,
    archive: Optional[Archive] = None,
    rule_set=None,
) -> tuple[Optional[dict], Optional[str], float]:
    cfg = dict(llm_config(db))
    saved_base = (cfg.get("base_url") or "").rstrip("/")
    if override:
        cfg.update({k: v for k, v in override.items() if v is not None})
    base = (cfg.get("base_url") or "").rstrip("/")
    model = cfg.get("model") or ""
    if not base or not model:
        return None, "未配置大模型", 0
    if override is not None and override.get("api_key") is not None:
        # An explicit empty key means an unauthenticated endpoint, never fallback.
        key = override["api_key"]
    elif base == saved_base:
        key = llm_api_key(db)
    else:
        # Bind stored credentials to the complete configured endpoint, including
        # scheme and path. Do not decrypt or send them to an overridden URL.
        return None, "更换大模型接口地址时，请显式提供 API 密钥（无认证接口请传空字符串）", 0
    redact = cfg.get("desensitize") is not False
    # 先替换完整变量中的身份信息，再截取长度，避免截断后留下身份信息片段。
    safe_variables = _prepare_variables(variables, archive, redact)
    tpl = (next((t for t in rule_set.rows("prompt_templates") if t.code == code), None)
           if rule_set else db.query(PromptTemplate).filter(PromptTemplate.code == code, PromptTemplate.is_active.is_(True)).first())
    if not tpl:
        sys_p, user_p = "只输出 JSON。", json.dumps(safe_variables, ensure_ascii=False)
    else:
        sys_p = tpl.system_prompt
        user_p = tpl.user_prompt
        for k, v in safe_variables.items():
            user_p = user_p.replace("{" + k + "}", str(v)[:6000])
    if redact:
        # 模板本身也可能包含身份信息；此处统一处理最终发送的两段提示词。
        sys_p = desensitize_text(sys_p, archive)
        user_p = desensitize_text(user_p, archive)
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
    t0 = time.time()
    max_attempts = max(1, int(cfg.get("max_attempts") or 3))
    # Invalid JSON/schema gets one repair attempt, independently of network retries.
    last_err = "大模型返回无效 JSON 对象"
    for _ in range(2):
        resp, err = _post_chat(base, payload, headers, timeout, max_attempts)
        if err:
            return None, err, (time.time() - t0) * 1000
        try:
            envelope = ChatCompletionOutput.model_validate(resp.json())
            content = envelope.choices[0].message.content
        except (ValueError, ValidationError):
            last_err = "大模型响应结构无效"
            continue
        try:
            parsed = _parse_json(content)
            if parsed is None:
                last_err = "大模型返回无效 JSON 对象"
                continue
            validated = validate_task_output(code, parsed)
        except ValidationError:
            # Do not echo model output (or Pydantic input values) into report errors.
            last_err = "大模型内容检查结果结构无效"
            continue
        return validated, None, (time.time() - t0) * 1000
    return None, last_err, (time.time() - t0) * 1000


def _post_chat(base, payload, headers, timeout, max_attempts):
    last_err = "大模型调用失败"
    for attempt in range(max_attempts):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(f"{base}/chat/completions", json=payload, headers=headers)
            if resp.status_code < 400:
                return resp, None
            last_err = f"大模型接口 HTTP {resp.status_code}"
            if resp.status_code < 500:
                return None, last_err
        except httpx.TimeoutException:
            last_err = "大模型请求超时"
        except httpx.RequestError:
            last_err = "大模型连接失败"
        if attempt + 1 < max_attempts:
            time.sleep(0.5 * (2 ** attempt))
    return None, last_err


def _prepare_variables(value: Any, archive: Optional[Archive], redact: bool) -> Any:
    if isinstance(value, str):
        return (desensitize_text(value, archive) if redact else value)[:6000]
    if isinstance(value, dict):
        return {key: _prepare_variables(item, archive, redact) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_prepare_variables(item, archive, redact) for item in value]
    return value


def _parse_json(content: str) -> Optional[dict]:
    if not content:
        return None
    fenced = re.fullmatch(r"```(?:json)?\s*\n?(.*?)\n?```", content.strip(), re.DOTALL | re.IGNORECASE)
    if fenced:
        content = fenced.group(1)
    try:
        value = json.loads(content, parse_constant=_reject_json_constant)
        return value if isinstance(value, dict) else None
    except ValueError:
        pass
    return None


def _reject_json_constant(value):
    raise ValueError("JSON 包含非标准数值")
