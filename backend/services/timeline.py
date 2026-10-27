from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from errors import conflict, forbidden, unprocessable
from models import (
    Archive,
    ArchiveTimeNode,
    Issue,
    Material,
    MaterialVersion,
    Submission,
    TimeNodeDef,
    TimeNodeExtraction,
)
from utils import now, stage_name, TZ8


def merge_archive_nodes(db: Session, archive_id: int, *, node_defs=None) -> None:
    defs = node_defs if node_defs is not None else db.query(TimeNodeDef).filter(TimeNodeDef.is_active.is_(True)).all()
    exs = (
        db.query(TimeNodeExtraction)
        .filter(TimeNodeExtraction.archive_id == archive_id, TimeNodeExtraction.is_current.is_(True))
        .all()
    )
    by_code: dict[str, list[TimeNodeExtraction]] = {}
    for e in exs:
        by_code.setdefault(e.node_code, []).append(e)
    existing = {n.node_code: n for n in db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == archive_id).all()}
    for d in defs:
        rows = by_code.get(d.code, [])
        dates = [r.value_date for r in rows if r.value_date]
        ends = [r.value_end_date for r in rows if r.value_end_date]
        hours = [r.hours for r in rows if r.hours is not None]
        # 冲突判定：手工校正优先；序列节点按多份材料汇总，日期天然不同不计冲突；
        # 其余节点按"同一字段出现多个不同取值"判定（含结束日期与学时）
        manual = [r for r in rows if (r.method or "") == "MANUAL"]
        basis = manual if manual else rows
        if d.value_kind == "DATE_SEQ":
            has_conflict = False
        else:
            def _multi(vals):
                return len({v.isoformat() if hasattr(v, "isoformat") else v for v in vals if v is not None}) > 1
            has_conflict = _multi([r.value_date for r in basis]) or _multi([r.value_end_date for r in basis]) or _multi([r.hours for r in basis])
        node = existing.get(d.code)
        if node and node.locked:
            continue
        if not node:
            node = ArchiveTimeNode(archive_id=archive_id, node_code=d.code, updated_at=now())
            db.add(node)
            existing[d.code] = node
        if d.value_kind == "DATE_SEQ":
            node.seq_count = len(dates)
            node.value_date = min(dates) if dates else None
            node.value_end_date = max(dates) if dates else None
        else:
            node.value_date = next((r.value_date for r in basis if r.value_date), None)
            node.value_end_date = next((r.value_end_date for r in basis if r.value_end_date), None)
            node.seq_count = len(dates)
        node.hours = next((r.hours for r in basis if r.hours is not None), None)
        node.source_count = len(rows)
        node.source_extraction_id = basis[0].id if basis else None
        node.has_conflict = has_conflict
        node.updated_at = now()
    db.flush()
    arch = db.query(Archive).filter(Archive.id == archive_id).first()
    if arch:
        arch.timeline_updated_at = now()


def effective_node(n: ArchiveTimeNode) -> dict:
    date_v = n.corrected_date or n.value_date
    end_v = n.corrected_end_date if n.corrected_date or n.corrected_end_date else n.value_end_date
    hours_v = n.corrected_hours if n.corrected_hours is not None else n.hours
    return {"date": date_v.isoformat() if date_v else None, "end_date": end_v.isoformat() if end_v else None, "hours": hours_v}


def node_map_for_archive(db: Session, archive_id: int, *, node_defs=None) -> dict:
    defs = {d.code: d for d in (node_defs if node_defs is not None else db.query(TimeNodeDef).all())}
    nodes = db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == archive_id).all()
    seqs = db.query(TimeNodeExtraction).filter(
        TimeNodeExtraction.archive_id == archive_id, TimeNodeExtraction.is_current.is_(True)
    ).all()
    version_ids = {getattr(e, "material_version_id", None) for e in seqs} - {None}
    versions = {v.id: v for v in db.query(MaterialVersion).filter(MaterialVersion.id.in_(version_ids)).all()} if version_ids else {}
    seq_map: dict[str, list] = {}
    invalid: dict[str, str] = {}
    sources: dict[str, list] = {}
    for e in seqs:
        if e.value_date:
            seq_map.setdefault(e.node_code, []).append(e.value_date.isoformat())
        if e.invalid_reason:
            invalid[e.node_code] = e.invalid_reason
        version_id = getattr(e, "material_version_id", None)
        version = versions.get(version_id)
        uploaded_at = version.uploaded_at if version else None
        if isinstance(uploaded_at, datetime):
            upload_day = (uploaded_at.replace(tzinfo=TZ8) if uploaded_at.tzinfo is None else uploaded_at).astimezone(TZ8).date()
        else:
            upload_day = uploaded_at
        sources.setdefault(e.node_code, []).append({
            "node_code": e.node_code, "extraction_id": getattr(e, "id", None),
            "material_id": getattr(e, "material_id", None), "version_id": version_id,
            "seq_index": getattr(e, "seq_index", None),
            "date": e.value_date.isoformat() if e.value_date else None,
            "end_date": e.value_end_date.isoformat() if e.value_end_date else None,
            "uploaded_at": uploaded_at.isoformat() if uploaded_at else None,
            "upload_date": upload_day.isoformat() if upload_day else None,
            "invalid_reason": e.invalid_reason, "page_no": getattr(e, "page_no", None),
            "bbox": getattr(e, "bbox", None),
        })
    out = {}
    for n in nodes:
        dfn = defs.get(n.node_code)
        eff = effective_node(n)
        node_sources = sources.get(n.node_code, [])
        # An explicit archive correction replaces the selected source value;
        # its upload date still comes from that source's original file version.
        for source in node_sources:
            if source["extraction_id"] == getattr(n, "source_extraction_id", None) and n.corrected_date:
                source.update(date=eff["date"], end_date=eff["end_date"], invalid_reason=None)
        out[n.node_code] = {
            "date": eff["date"],
            "end_date": eff["end_date"],
            "end": eff["end_date"],
            "hours": eff["hours"],
            "seq": seq_map.get(n.node_code, []),
            "has_conflict": n.has_conflict,
            "invalid_reason": invalid.get(n.node_code),
            "value_kind": dfn.value_kind if dfn else "DATE",
            "sources": node_sources,
        }
    return out


def timeline_view(db: Session, archive: Archive) -> dict:
    defs = db.query(TimeNodeDef).filter(TimeNodeDef.is_active.is_(True)).order_by(TimeNodeDef.sort_order).all()
    nodes = {n.node_code: n for n in db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == archive.id).all()}
    exs = (
        db.query(TimeNodeExtraction)
        .filter(TimeNodeExtraction.archive_id == archive.id, TimeNodeExtraction.is_current.is_(True))
        .all()
    )
    by_code: dict[str, list] = {}
    for e in exs:
        by_code.setdefault(e.node_code, []).append(e)
    subs = db.query(Submission).filter(Submission.archive_id == archive.id).all()
    sub_by_stage = {s.stage_code: s for s in subs}
    stages = []
    for code in range(1, 6):
        s = sub_by_stage.get(code)
        stages.append({
            "code": code,
            "name": stage_name(db, code),
            "status": s.status if s else ("FILED" if archive.current_stage > code else "PENDING"),
            "submission_id": s.id if s else None,
            "filed_at": s.filed_at.isoformat() if s and s.filed_at else None,
        })
    issues = (
        db.query(Issue)
        .join(Submission, Submission.id == Issue.submission_id)
        .filter(Submission.archive_id == archive.id, Issue.is_active.is_(True), Issue.category == "TIME")
        .all()
    )
    issues_by_node: dict[str, list] = {}
    for iss in issues:
        nc = (iss.location or {}).get("node_code")
        if nc:
            issues_by_node.setdefault(nc, []).append({
                "issue_id": iss.id, "rule_code": iss.rule_code, "severity": iss.severity, "message": iss.title,
            })
    node_out = []
    derived = []
    for d in defs:
        n = nodes.get(d.code)
        sources = []
        for e in by_code.get(d.code, []):
            mat = db.query(Material).filter(Material.id == e.material_id).first() if e.material_id else None
            ver = db.query(MaterialVersion).filter(MaterialVersion.id == e.material_version_id).first() if e.material_version_id else None
            sources.append({
                "extraction_id": e.id,
                "material_id": e.material_id,
                "material_title": mat.title if mat else None,
                "version_no": ver.version_no if ver else None,
                "page_no": e.page_no,
                "bbox": e.bbox,
                "raw_text": e.raw_text,
                "date": e.value_date.isoformat() if e.value_date else None,
                "end_date": e.value_end_date.isoformat() if e.value_end_date else None,
                "hours": e.hours,
                "method": e.method,
                "confidence": e.confidence,
            })
        if d.value_kind == "DERIVED":
            date_v = None
            if n and (n.corrected_date or n.value_date):
                date_v = (n.corrected_date or n.value_date).isoformat()
            derived.append({
                "code": d.code, "name": d.name, "date": date_v,
                "base": (d.derive_expr or {}).get("base"),
            })
            continue
        item = {
            "code": d.code,
            "name": d.name,
            "value_kind": d.value_kind,
            "stage_code": d.stage_code,
            "effective": effective_node(n) if n else {"date": None, "end_date": None, "hours": None},
            "extracted": {"date": n.value_date.isoformat() if n and n.value_date else None} if n else None,
            "corrected": {"date": n.corrected_date.isoformat() if n and n.corrected_date else None,
                          "reason": n.correction_reason} if n and n.corrected_date else None,
            "has_conflict": n.has_conflict if n else False,
            "locked": n.locked if n else False,
            "sources": sources,
            "anomalies": issues_by_node.get(d.code, []),
        }
        if d.value_kind == "DATE_SEQ":
            item["items"] = [
                {"seq_index": e.seq_index, "date": e.value_date.isoformat() if e.value_date else None, "material_id": e.material_id}
                for e in by_code.get(d.code, [])
            ]
        node_out.append(item)
    latest = None
    for s in subs:
        if s.stage_code == archive.current_stage:
            latest = s
            break
    report_id = latest.latest_report_id if latest else None
    stale = False
    if latest and archive.timeline_updated_at and latest.updated_at and archive.timeline_updated_at > latest.updated_at:
        stale = True
    return {
        "archive_id": archive.id,
        "current_stage": archive.current_stage,
        "stages": stages,
        "nodes": node_out,
        "derived": derived,
        "report_id": report_id,
        "report_is_stale": stale,
    }


def _strict_date(value, label: str) -> Optional[date]:
    """校正入口只接受完整的 YYYY-MM-DD；与主动清空区分开，避免非法输入把旧值抹掉。"""
    if value is None or value == "":
        return None
    if not isinstance(value, str) or len(value) != 10:
        raise unprocessable(f"{label}须为 YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise unprocessable(f"{label}不是有效日期")


def correct_node(db: Session, archive: Archive, node_code: str, body: dict, actor) -> ArchiveTimeNode:
    dfn = db.query(TimeNodeDef).filter(TimeNodeDef.code == node_code).first()
    if not dfn:
        from errors import not_found
        raise not_found("节点不存在")
    node = db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == archive.id, ArchiveTimeNode.node_code == node_code).first()
    if node and node.locked and actor.role != "ORG_ADMIN":
        raise forbidden("该节点已随备案锁定，仅组织部可改")
    reason = (body.get("reason") or "").strip()
    if not reason:
        raise unprocessable("必须填写校正原因")
    clear = bool(body.get("clear"))
    # 先完整校验再落库：非法日期、空日期或结束早于开始都不能改到原值
    value = end = hours = None
    if not clear:
        value = _strict_date(body.get("date"), "校正日期")
        if value is None:
            raise unprocessable("校正日期不能为空；如需清空请使用 clear")
        end = _strict_date(body.get("end_date"), "结束日期")
        if end and end < value:
            raise unprocessable("结束日期不能早于开始日期")
        raw_hours = body.get("hours")
        if raw_hours not in (None, ""):
            if not dfn.has_hours:
                raise unprocessable("该节点不接受学时")
            if isinstance(raw_hours, bool) or not isinstance(raw_hours, (int, float)):
                raise unprocessable("学时必须为数字")
            if raw_hours < 0 or raw_hours > 10000:
                raise unprocessable("学时须在 0 到 10000 之间")
            hours = raw_hours
    if not node:
        node = ArchiveTimeNode(archive_id=archive.id, node_code=node_code, updated_at=now())
        db.add(node)
        db.flush()
    # 反复校正时先停用旧的手工值，避免手工抽取记录累积、来源重复计数
    db.query(TimeNodeExtraction).filter(
        TimeNodeExtraction.archive_id == archive.id, TimeNodeExtraction.node_code == node_code,
        TimeNodeExtraction.method == "MANUAL", TimeNodeExtraction.is_current.is_(True),
    ).update({"is_current": False})
    node.correction_reason = reason
    node.corrected_by = actor.id
    node.corrected_at = now()
    if clear:
        node.corrected_date = None
        node.corrected_end_date = None
        node.corrected_hours = None
    else:
        node.corrected_date = value
        node.corrected_end_date = end
        node.corrected_hours = hours
        db.add(TimeNodeExtraction(
            archive_id=archive.id, node_code=node_code, seq_index=0,
            value_date=value, value_end_date=end, hours=hours,
            raw_text=reason, method="MANUAL", is_current=True, created_at=now(),
        ))
    archive.timeline_updated_at = now()
    db.flush()
    return node


def lock_stage_nodes(db: Session, archive: Archive, stage_code: int) -> None:
    defs = db.query(TimeNodeDef).filter(TimeNodeDef.stage_code == stage_code).all()
    for d in defs:
        node = db.query(ArchiveTimeNode).filter(ArchiveTimeNode.archive_id == archive.id, ArchiveTimeNode.node_code == d.code).first()
        if not node:
            node = ArchiveTimeNode(archive_id=archive.id, node_code=d.code, updated_at=now())
            db.add(node)
        node.locked = True
        node.locked_stage = stage_code
    db.flush()
