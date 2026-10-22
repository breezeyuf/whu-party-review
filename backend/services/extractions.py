"""Validate material-source node corrections before changing any record."""
from datetime import date
import math
import re

from errors import unprocessable
from models import TimeNodeDef, TimeNodeExtraction
from utils import now


def _date(value, label):
    if value is None or value == "":
        return None
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise unprocessable(f"{label}须为有效日期（YYYY-MM-DD）")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise unprocessable(f"{label}无效")


def _snapshot(row):
    return {"node_code": row.node_code, "date": row.value_date.isoformat() if row.value_date else None,
            "end_date": row.value_end_date.isoformat() if row.value_end_date else None,
            "hours": row.hours, "seq_index": row.seq_index, "method": row.method,
            "invalid_reason": row.invalid_reason, "is_current": row.is_current}


def correct_extractions(db, material, version, changes):
    if not isinstance(changes, list) or len(changes) > 200:
        raise unprocessable("节点校正须为列表，单次最多 200 条")
    if not changes:
        return []
    defs = {d.code: d for d in db.query(TimeNodeDef).all()}
    planned = []
    seen = set()
    for item in changes:
        if not isinstance(item, dict):
            raise unprocessable("节点记录格式无效")
        row = None
        oid = item.get("extraction_id")
        if oid is not None:
            if type(oid) is not int or oid <= 0 or oid in seen:
                raise unprocessable("抽取记录编号无效或重复")
            seen.add(oid)
            row = db.query(TimeNodeExtraction).filter(
                TimeNodeExtraction.id == oid, TimeNodeExtraction.material_id == material.id,
                TimeNodeExtraction.material_version_id == version.id,
                TimeNodeExtraction.is_current.is_(True),
            ).first()
            if not row:
                raise unprocessable("抽取记录不属于当前材料版本，或已停用，请刷新后重试")
        if item.get("delete"):
            if not row:
                raise unprocessable("删除节点须指定已有记录")
            planned.append((row, None))
            continue
        code = item.get("node_code") or (row.node_code if row else None)
        definition = defs.get(code) if isinstance(code, str) else None
        if not definition or definition.value_kind == "DERIVED" or (not row and not definition.is_active):
            raise unprocessable("节点不存在、已停用或为派生节点")
        if row and code != row.node_code:
            raise unprocessable("已有记录不能更换节点，请删除后新增")
        start = _date(item["date"], "节点日期") if "date" in item else (row.value_date if row else None)
        end = _date(item["end_date"], "结束日期") if "end_date" in item else (row.value_end_date if row else None)
        if not start:
            raise unprocessable(f"{code}须填写有效日期")
        if end and (definition.value_kind != "DATE_RANGE" or end < start):
            raise unprocessable("结束日期仅适用于日期区间，且不能早于开始日期")
        hours = item.get("hours", row.hours if row else None)
        if hours is not None and (not definition.has_hours or isinstance(hours, bool)
                                  or not isinstance(hours, (int, float)) or not math.isfinite(hours) or hours < 0):
            raise unprocessable("学时须为非负有限数，且节点须支持学时")
        index = item.get("seq_index", row.seq_index if row else 0)
        if type(index) is not int or index < 0 or (definition.value_kind != "DATE_SEQ" and index != 0):
            raise unprocessable("序号须为非负整数，仅序列节点可指定非零序号")
        planned.append((row, {"node_code": code, "value_date": start, "value_end_date": end,
                              "hours": hours, "seq_index": index}))
    audit = []
    for row, values in planned:
        before = _snapshot(row) if row else None
        if values is None:
            row.is_current = False
            action = "DELETE"
        else:
            action = "UPDATE" if row else "CREATE"
            if not row:
                row = TimeNodeExtraction(archive_id=material.archive_id, material_id=material.id,
                                         material_version_id=version.id, is_current=True, created_at=now())
                db.add(row)
            for key, value in values.items():
                setattr(row, key, value)
            row.method = "MANUAL"
            row.invalid_reason = None
            row.confidence = 1.0
        db.flush()
        audit.append({"action": action, "extraction_id": row.id, "before": before, "after": _snapshot(row)})
    return audit
