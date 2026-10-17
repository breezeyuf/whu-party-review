from __future__ import annotations

from typing import Optional


def classify_material(text: str, declared_type, types: list, threshold: float = 0.7) -> dict:
    if declared_type:
        return {
            "type_id": declared_type.id,
            "type_code": declared_type.code,
            "type_name": declared_type.name,
            "type_source": "DECLARED",
            "type_confidence": 1.0,
            "type_status": "AUTO",
        }
    head = (text or "")[:800]
    best = None
    best_score = 0.0
    for t in types:
        if not t.is_active:
            continue
        score = 0.0
        kws = t.title_keywords or []
        excl = t.exclude_keywords or []
        if any(k in head for k in excl):
            continue
        if kws:
            hits = sum(1 for k in kws if k and k in head)
            score = hits / max(1, len(kws))
            if t.name and t.name in head[:40]:
                score = max(score, 0.95)
        if score > best_score:
            best_score = score
            best = t
    if best and best_score >= threshold:
        return {
            "type_id": best.id,
            "type_code": best.code,
            "type_name": best.name,
            "type_source": "AI",
            "type_confidence": round(min(1.0, best_score), 3),
            "type_status": "AUTO",
        }
    if best:
        return {
            "type_id": best.id,
            "type_code": best.code,
            "type_name": best.name,
            "type_source": "AI",
            "type_confidence": round(best_score, 3),
            "type_status": "NEEDS_CONFIRM",
        }
    return {
        "type_id": None,
        "type_code": None,
        "type_name": None,
        "type_source": "AI",
        "type_confidence": 0.0,
        "type_status": "NEEDS_CONFIRM",
    }
