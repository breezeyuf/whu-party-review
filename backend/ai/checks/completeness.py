from __future__ import annotations

from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta

from ai.types import IssueDraft, loc
from models import ChecklistItem, Material, MaterialType
from utils import as_date, get_setting


def expected_count(item: ChecklistItem, nodes: dict, batch_end: date | None, today: date, min_tail: int) -> int:
    if item.quantity_mode != "PER_PERIOD":
        return item.fixed_count or 1
    start_n = item.period_start_node
    end_n = item.period_end_node
    start = None
    end = None
    if start_n and start_n in nodes:
        start = nodes[start_n].date
    if end_n and end_n in nodes:
        end = nodes[end_n].date
    if not end:
        end = min([d for d in [batch_end, today] if d]) if (batch_end or today) else today
    if not start or not end or end < start:
        return 0
    months = max(1, int(item.period_months or 3))
    n = 0
    cur = start
    while cur < end:
        nxt = cur + relativedelta(months=months)
        if nxt > end and (end - cur).days < min_tail:
            break
        n += 1
        cur = nxt
    return n


def run_completeness(db, submission, materials: list[Material], nodes: dict) -> tuple[dict, list[IssueDraft], list[dict]]:
    today = date.today()
    batch_end = submission.archive.batch.end_date if submission.archive and submission.archive.batch else None
    min_tail = int(get_setting(db, "calendar", {}).get("period_min_tail_days", 30))
    items = (
        db.query(ChecklistItem)
        .filter(ChecklistItem.stage_code == submission.stage_code, ChecklistItem.is_active.is_(True))
        .order_by(ChecklistItem.sort_order)
        .all()
    )
    active = [m for m in materials if m.status == "ACTIVE"]
    used_ids = set()
    out_items = []
    drafts: list[IssueDraft] = []
    extra = []
    unclassified = []
    for it in items:
        mt: MaterialType = it.material_type
        matched = [m for m in active if m.type_id == it.material_type_id]
        used_ids.update(m.id for m in matched)
        expected = expected_count(it, nodes, batch_end, today, min_tail)
        actual = len(matched)
        missing = max(0, expected - actual)
        out_items.append({
            "checklist_item_id": it.id,
            "material_type": {"id": mt.id, "code": mt.code, "name": mt.name},
            "material_type_name": mt.name,
            "required": it.is_required,
            "quantity_mode": it.quantity_mode,
            "expected": expected,
            "actual": actual,
            "missing": missing,
            "requirement_text": it.requirement_text,
            "material_ids": [m.id for m in matched],
        })
        if missing and it.is_required:
            drafts.append(IssueDraft(
                category="COMPLETENESS", severity="BLOCK",
                title=f"缺少《{mt.name}》",
                description=f"应交 {expected} 份，已交 {actual} 份，缺少 {missing} 份。{it.requirement_text or ''}",
                rule_code="COMPLETENESS",
                rule_basis="党员发展各阶段材料清单",
                location=loc(checklist_item_id=it.id),
                actual_value=str(actual), expected_value=str(expected),
                suggestion=f"缺少《{mt.name}》{missing} 份（应交 {expected} 份，已交 {actual} 份）。请按要求补交：{it.requirement_text or ''}。",
                fingerprint_parts=("COMPLETENESS", mt.code, it.id),
            ))
        elif missing and not it.is_required:
            drafts.append(IssueDraft(
                category="COMPLETENESS", severity="INFO",
                title=f"可选项《{mt.name}》未交齐",
                description=f"可选项应交 {expected} 份，已交 {actual} 份。",
                rule_code="COMPLETENESS",
                location=loc(checklist_item_id=it.id),
                actual_value=str(actual), expected_value=str(expected),
                fingerprint_parts=("COMPLETENESS_OPT", mt.code, it.id),
            ))
    shas: dict[str, list[int]] = {}
    from models import MaterialVersion
    for m in active:
        if not m.type_id:
            unclassified.append({"material_id": m.id, "title": m.title, "reason": "类型待确认"})
        elif m.id not in used_ids:
            extra.append({"material_id": m.id, "title": m.title, "reason": "不在本阶段清单"})
        if m.current_version_id:
            ver = db.query(MaterialVersion).filter(MaterialVersion.id == m.current_version_id).first()
            if ver:
                shas.setdefault(ver.sha256, []).append(m.id)
    for sha, ids in shas.items():
        if len(ids) > 1:
            drafts.append(IssueDraft(
                category="COMPLETENESS", severity="INFO",
                title="检测到重复文件",
                description=f"材料 {ids} 文件哈希相同，可能为重复上传。",
                rule_code="COMPLETENESS_DUP",
                actual_value=sha[:12], expected_value="各材料文件不同",
                fingerprint_parts=("DUP", sha),
            ))
    completeness = {
        "stage_code": submission.stage_code,
        "items": out_items,
        "extra": extra,
        "unclassified": unclassified,
        "missing_total": sum(i["missing"] for i in out_items if i["required"]),
        "is_complete": all(i["missing"] == 0 for i in out_items if i["required"]),
    }
    rule_results = [{"rule_code": "COMPLETENESS", "result": "FAIL" if drafts else "PASS",
                     "issue_ids": []}]
    return completeness, drafts, rule_results
