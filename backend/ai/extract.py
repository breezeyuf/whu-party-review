from __future__ import annotations

import re
from typing import Any, Optional

from ai.dates import find_dates, parse_date


FIELD_PATTERNS = [
    ("name", r"(?:姓名|申请人)[:：\s]*([^\s，。；]{2,10})"),
    ("gender", r"(?:性别)[:：\s]*(男|女)"),
    ("ethnicity", r"(?:民族)[:：\s]*([^\s，。]{1,10})"),
    ("birth_date", r"(?:出生日期|出生年月|生于)[:：\s]*([0-9〇零一二三四五六七八九年月日.\-/]{4,16})"),
    ("native_place", r"(?:籍贯)[:：\s]*([^\s，。]{2,20})"),
    ("student_no", r"(?:学号)[:：\s]*([A-Za-z0-9]{4,20})"),
    ("branch", r"(?:党支部|所在支部)[:：\s]*([^\n]{2,30})"),
]


def extract_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    if not text:
        return fields
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        title = lines[0]
        if len(title) <= 30:
            fields["title"] = title
    for ln in lines[:8]:
        if any(k in ln for k in ("党组织", "党支部", "敬爱的")):
            fields["salutation"] = ln
            break
    for ln in lines[-12:]:
        if "此致" in ln or "敬礼" in ln:
            fields["closing"] = ln
        if any(k in ln for k in ("汇报人", "申请人", "志愿人", "签名")):
            m = re.search(r"(?:汇报人|申请人|志愿人|签名)[:：\s]*([^\s，。]{2,10})", ln)
            if m:
                fields["signature_name"] = m.group(1)
    dates = find_dates(text)
    if dates:
        last = dates[-1]
        if last.get("date"):
            fields["signature_date"] = last["date"].isoformat()
            fields["signature_date_raw"] = last.get("raw")
    for key, pat in FIELD_PATTERNS:
        m = re.search(pat, text)
        if m:
            fields[key] = m.group(1).strip()
    if "birth_date" in fields:
        d, raw, err = parse_date(fields["birth_date"])
        if d:
            fields["birth_date"] = d.isoformat()
        elif err:
            fields["birth_date_invalid"] = err
    fields["char_count"] = len(re.sub(r"\s+", "", text))
    return fields


def extract_nodes(text: str, pages: list, type_row, node_defs: list) -> list[dict]:
    results = []
    if not text:
        return results
    date_map = {}
    if type_row and type_row.date_node_map:
        date_map = type_row.date_node_map or {}
    fields = extract_fields(text)
    dates = find_dates(text)
    for field_key, node_code in date_map.items():
        raw = None
        if field_key == "signature_date":
            raw = fields.get("signature_date_raw") or fields.get("signature_date")
        elif field_key.startswith("field:"):
            name = field_key.split(":", 1)[1]
            raw = fields.get({"出生日期": "birth_date"}.get(name, name))
        d, raw_s, err = parse_date(str(raw)) if raw else (None, None, "未抽取到")
        loc = _locate(pages, raw_s or (raw or ""))
        results.append({
            "node_code": node_code,
            "seq_index": 0,
            "value_date": d,
            "value_end_date": None,
            "hours": _find_hours(text) if node_code == "T10" else None,
            "raw_text": raw_s or raw,
            "invalid_reason": err if not d else None,
            "page_no": loc[0],
            "bbox": loc[1],
            "confidence": 0.9 if d else 0.4,
            "method": "RULE",
        })
    for nd in node_defs:
        kws = nd.extract_keywords or []
        if not kws:
            continue
        if any(r["node_code"] == nd.code for r in results):
            continue
        hits = []
        for d in dates:
            ctx = text[max(0, d["start"] - 30): d["end"] + 12]
            if any(k in ctx for k in kws):
                hits.append(d)
        # Do not guess a thought-report date from an unrelated date elsewhere
        # in the document (for example, a birth date in an autobiography).
        # False positives contaminate the archive timeline and can affect rules.
        for i, h in enumerate(hits):
            loc = _locate(pages, h.get("raw") or "")
            results.append({
                "node_code": nd.code,
                "seq_index": i if nd.value_kind == "DATE_SEQ" else 0,
                "value_date": h.get("date"),
                "value_end_date": None,
                "hours": _find_hours(text) if nd.code == "T10" else None,
                "raw_text": h.get("raw"),
                "invalid_reason": h.get("invalid_reason"),
                "page_no": loc[0],
                "bbox": loc[1],
                "confidence": 0.85 if h.get("date") else 0.4,
                "method": "RULE",
            })
    if any(nd.code == "T10" for nd in node_defs):
        rng = _find_range(dates)
        if rng:
            for r in results:
                if r["node_code"] == "T10":
                    r["value_date"], r["value_end_date"] = rng
    return results


def _find_hours(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*学时", text or "")
    return float(m.group(1)) if m else None


def _find_range(dates: list) -> Optional[tuple]:
    valid = [d["date"] for d in dates if d.get("date")]
    if len(valid) >= 2:
        return min(valid), max(valid)
    return None


def _locate(pages: list, snippet: str) -> tuple[Optional[int], Optional[list]]:
    if not snippet or not pages:
        return None, None
    for p in pages:
        for b in p.get("blocks") or []:
            if snippet and snippet in (b.get("text") or ""):
                return p.get("page_no"), b.get("bbox")
        if snippet in (p.get("text") or ""):
            return p.get("page_no"), None
    return pages[0].get("page_no") if pages else None, None
