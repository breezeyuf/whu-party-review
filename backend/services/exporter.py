from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote

from fastapi.responses import Response
from sqlalchemy.orm import Session

from models import ExportFile, Issue, Notice
from services import storage as store
from services.stats import FILTER_KEYS, ai_quality, apply_filters, normalize_filters, overview
from errors import unprocessable
from utils import now, get_setting
from datetime import timedelta


def run_export_job(db: Session, job) -> None:
    params = job.params or {}
    export_type = params.get("export_type") or "STATS_REPORT"
    filters = normalize_filters(params.get("filters") or {})
    # 服务端注入的作用域优先于客户端 filters，防止越权导出
    scope_college = params.get("scope_college_id")
    if scope_college is not None:
        filters["college_id"] = int(scope_college)
    if export_type not in ("AI_QUALITY", "DESENSITIZED_DATA", "STATS_REPORT"):
        raise unprocessable("不支持的导出类型")
    from models import Archive, Submission
    actor = SimpleNamespace(role="ORG_ADMIN", org_id=None)
    from openpyxl import Workbook
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(export_type[:20])
    row_count = 0
    q = apply_filters(db.query(Submission), Submission, **filters)

    def append_detail(values):
        nonlocal ws, row_count
        # A worksheet has 1,048,576 rows including its header. Start another
        # sheet instead of silently dropping packages or emitting invalid XLSX.
        if row_count and row_count % 1_048_575 == 0:
            ws = wb.create_sheet(f"{export_type[:16]}_{row_count // 1_048_575 + 1}")
            ws.append(headers)
        ws.append([_safe_cell(v) for v in values])
        row_count += 1

    if export_type == "AI_QUALITY":
        quality = ai_quality(db, actor, **filters)
        headers = ["rule_code", "title", "total", "reviewed", "confirmed", "rejected", "modified", "precision"]
        ws.append(headers)
        for group in quality["by_rule"]:
            append_detail([group["rule_code"], group["name"], group["total"], group["reviewed"],
                           group["confirmed"], group["rejected"], group["modified"], group["precision"]])
        summary = wb.create_sheet("AI效能汇总")
        summary.append(["metric", "value"])
        for key, value in quality.items():
            if not isinstance(value, (dict, list)):
                summary.append([key, _safe_cell(value)])
        types = wb.create_sheet("按材料类型")
        types.append(["material_type_code", "name", "total", "reviewed", "confirmed", "rejected", "modified", "precision"])
        for group in quality["by_material_type"]:
            types.append([_safe_cell(group.get(k)) for k in ("material_type_code", "name", "total", "reviewed", "confirmed", "rejected", "modified", "precision")])
    elif export_type == "DESENSITIZED_DATA":
        headers = ["anon_code", "stage", "status", "is_demo"]
        ws.append(headers)
        # Use matching submissions: filtering on Archive.current_stage would
        # lose historical stages and archives have no submitted_at column.
        rows = (q.join(Archive, Archive.id == Submission.archive_id)
                .with_entities(Archive.anon_code, Submission.stage_code, Submission.status, Archive.is_demo)
                .order_by(Submission.id))
        for row in rows.yield_per(1000):
            append_detail(row)
    else:
        headers = ["submission_id", "stage", "status", "round_no"]
        ws.append(headers)
        for s in q.order_by(Submission.id).yield_per(1000):
            append_detail([s.id, s.stage_code, s.status, s.round_no])
        metrics = overview(db, actor, **filters)
        summary = wb.create_sheet("统计汇总")
        summary.append(["metric", "value"])
        for key, value in metrics.items():
            if not isinstance(value, (dict, list)):
                summary.append([key, value])
        for name, rows in (("按阶段", metrics["by_stage"]), ("按支部", metrics["by_branch"]), ("审核趋势", metrics["trend"])):
            sheet = wb.create_sheet(name)
            if rows:
                keys = list(rows[0])
                sheet.append(keys)
                for row in rows:
                    sheet.append([_safe_cell(row.get(k)) for k in keys])
    criteria = wb.create_sheet("筛选说明")
    criteria.append(["filter", "value"])
    criteria.append(["date_basis", "提交时间，Asia/Shanghai，含起止日期"])
    criteria.append(["row_count", row_count])
    for key in FILTER_KEYS:
        criteria.append([key, _safe_cell(str(filters[key])) if key in filters else ""])
    buf = BytesIO()
    wb.save(buf)
    data = buf.getvalue()
    rel = f"exports/{job.id}_{export_type}.xlsx"
    path = store.abs_path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    days = int(get_setting(db, "retention", {}).get("export_days") or 7)
    ef = ExportFile(
        export_type=export_type, params={k: str(v) if k.startswith("date_") else v for k, v in filters.items()}, file_name=f"{export_type}.xlsx",
        stored_path=rel, row_count=row_count, created_by=job.created_by,
        created_at=now(), expires_at=now() + timedelta(days=days),
    )
    db.add(ef)
    db.flush()
    job.result = {"export_id": ef.id, "file_name": ef.file_name, "row_count": row_count,
                  "download_url": f"/api/exports/{ef.id}/download"}


def _safe_cell(v):
    """规避 xlsx 公式注入：以 = + - @ 开头的文本加前缀。"""
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@"):
        return "'" + v
    return v


def xlsx_response(filename: str, wb) -> Response:
    buf = BytesIO()
    wb.save(buf)
    data = buf.getvalue()
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


def export_notice_file(notice: Notice, fmt: str = "pdf") -> Response:
    student = (notice.content or {}).get("student") or {}
    anon = student.get("student_no") or str(notice.id)
    title = notice.title
    items = (notice.content or {}).get("items") or []
    comps = (notice.content or {}).get("completion_items") or []
    note = (notice.content or {}).get("note") or ""
    if fmt == "docx":
        from docx import Document
        doc = Document()
        doc.add_heading(title, 0)
        intro = (notice.content or {}).get("intro") or ""
        doc.add_paragraph(intro)
        for it in items:
            doc.add_paragraph(f"{it.get('no')}. [{it.get('severity')}] {it.get('problem')}")
            if it.get("suggestion"):
                doc.add_paragraph(f"修改建议：{it.get('suggestion')}")
        for it in comps:
            doc.add_paragraph(f"缺项：{it.get('material')} 缺 {it.get('missing')} 份")
        if note:
            doc.add_paragraph(f"审核意见：{note}")
        buf = BytesIO()
        doc.save(buf)
        name = f"整改通知_{anon}_第{notice.round_no}轮.docx"
        return Response(
            content=buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"},
        )
    import fitz

    def html_text(value):
        # 问题原文中的标签和换行属于正文，不能作为排版 HTML 执行。
        text = "" if value is None else str(value)
        return escape(text).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")

    parts = [f"<h2>{html_text(title)}</h2>", f"<p>{html_text((notice.content or {}).get('intro'))}</p>"]
    for it in items:
        parts.append(
            f"<p>{html_text(it.get('no'))}. [{html_text(it.get('severity'))}] "
            f"{html_text(it.get('problem'))}<br/>建议：{html_text(it.get('suggestion'))}</p>"
        )
    for it in comps:
        parts.append(f"<p>缺项：{html_text(it.get('material'))} 缺 {html_text(it.get('missing'))} 份</p>")
    if note:
        parts.append(f"<p>审核意见：{html_text(note)}</p>")

    # Story 将未排完的正文续写到下一页，保持字号，避免单页缩放到无法阅读。
    story = fitz.Story(
        html="".join(parts), em=11,
        user_css="body { font-size: 11pt; line-height: 1.5; margin: 0; } "
                 "h2 { font-size: 16pt; margin: 0 0 14pt; } p { margin: 0 0 10pt; }",
    )
    page_rect = fitz.paper_rect("a4")
    content_rect = page_rect + (42, 42, -42, -48)
    buf = BytesIO()
    with fitz.DocumentWriter(buf) as writer:
        story.write(writer, lambda _index, _filled: (page_rect, content_rect, None))
    with fitz.open(stream=buf.getvalue(), filetype="pdf") as doc:
        for page in doc:
            label = f"{page.number + 1} / {len(doc)}"
            label_width = fitz.get_text_length(label, fontname="helv", fontsize=9)
            page.insert_text(((page.rect.width - label_width) / 2, page.rect.height - 24), label, fontsize=9)
        data = doc.tobytes(garbage=4, deflate=True)
    name = f"整改通知_{anon}_第{notice.round_no}轮.pdf"
    return Response(
        content=data, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(name)}"},
    )
