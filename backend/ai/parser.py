from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any, Optional

from config import STORAGE_DIR, ensure_storage


def parse_version_file(stored_path: str, file_ext: str) -> dict[str, Any]:
    ensure_storage()
    path = STORAGE_DIR / stored_path
    if not path.is_file():
        return _empty("NONE", warnings=["原文件不存在"])
    ext = (file_ext or path.suffix.lstrip(".")).lower()
    if ext == "pdf":
        return _parse_pdf(path)
    if ext in ("jpg", "jpeg", "png"):
        return _parse_image(path, ext)
    if ext == "docx":
        return _parse_docx(path)
    return _empty("NONE", warnings=[f"不支持的类型 {ext}"])


def _empty(parser: str, warnings=None) -> dict:
    return {
        "parser": parser,
        "ocr_engine": None,
        "preview_pdf_path": None,
        "full_text": "",
        "char_count": 0,
        "pages": [],
        "visual_marks": {"seals": [], "signatures": []},
        "extracted_fields": {},
        "format_features": {},
        "warnings": warnings or [],
        "page_count": 0,
    }


def _parse_pdf(path: Path) -> dict:
    try:
        import fitz
    except ImportError:
        return _empty("NONE", warnings=["未安装 PyMuPDF"])
    doc = fitz.open(path)
    pages = []
    texts = []
    parser = "PDF_TEXT"
    ocr_engine = None
    warnings = []
    ocr_failed = False
    for i, page in enumerate(doc):
        info = page.get_text("dict")
        blocks = []
        page_text_parts = []
        for b in info.get("blocks", []):
            if b.get("type") != 0:
                continue
            for line in b.get("lines", []):
                line_text = "".join(s.get("text", "") for s in line.get("spans", []))
                if not line_text.strip():
                    continue
                bbox = line.get("bbox") or b.get("bbox")
                blocks.append({"text": line_text, "bbox": list(bbox) if bbox else None, "conf": 1.0})
                page_text_parts.append(line_text)
        page_text = "\n".join(page_text_parts)
        source = "text"
        if len(page_text.strip()) < 20:
            ocr_text, ocr_blocks, engine, warn = _ocr_page(page)
            if warn:
                warnings.append(warn)
                ocr_failed = True
            if ocr_text:
                page_text = ocr_text
                blocks = ocr_blocks
                source = "ocr"
                ocr_engine = engine
            else:
                warnings.append(f"第 {i+1} 页文本过少，可能为扫描件，需人工核对")
                source = "scan"
        texts.append(page_text)
        pages.append({
            "page_no": i + 1,
            "width": float(page.rect.width),
            "height": float(page.rect.height),
            "text": page_text,
            "source": source,
            "blocks": blocks,
            "quality": {"dpi": None, "blur_score": None, "is_blurry": False},
        })
    rel_preview = stored_rel_preview(path, "pdf")
    preview = STORAGE_DIR / rel_preview
    preview.parent.mkdir(parents=True, exist_ok=True)
    if path.resolve() != preview.resolve():
        try:
            import shutil
            shutil.copy2(path, preview)
        except OSError:
            rel_preview = str(path.relative_to(STORAGE_DIR)).replace("\\", "/")
    full = "\n".join(texts)
    sources = {page["source"] for page in pages}
    parser = "OCR" if sources == {"ocr"} else ("MIXED" if "ocr" in sources else "PDF_TEXT")
    visual = _visual_from_pdf(doc)
    doc.close()
    return {
        "parser": parser if pages else "NONE",
        "ocr_engine": ocr_engine,
        "preview_pdf_path": rel_preview,
        "full_text": full,
        "char_count": len(full.replace(" ", "")),
        "pages": pages,
        "visual_marks": visual,
        "extracted_fields": {},
        "format_features": {},
        "warnings": warnings,
        "ocr_failed": ocr_failed,
        "page_count": len(pages),
    }


def stored_rel_preview(src: Path, ext: str) -> str:
    stem = src.stem
    return f"previews/{stem}.pdf"


def _parse_image(path: Path, ext: str) -> dict:
    try:
        import fitz
    except ImportError:
        return _empty("NONE", warnings=["未安装 PyMuPDF"])
    doc = fitz.open()
    img_doc = fitz.open(path)
    try:
        pdfbytes = img_doc.convert_to_pdf()
    except Exception:
        page = doc.new_page(width=595, height=842)
        pix = fitz.Pixmap(str(path))
        page.insert_image(page.rect, pixmap=pix)
        pdfbytes = doc.tobytes()
        img_doc.close()
        doc.close()
        doc = fitz.open(stream=pdfbytes, filetype="pdf")
    else:
        img_doc.close()
        doc.close()
        doc = fitz.open(stream=pdfbytes, filetype="pdf")
    rel = f"previews/{path.stem}.pdf"
    out = STORAGE_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(doc.tobytes())
    page = doc[0]
    ocr_text, blocks, engine, warn = _ocr_page(page)
    warnings = [warn] if warn else []
    if not ocr_text:
        warnings.append("图片型材料未识别到文字，需人工核对文本")
    visual = _visual_from_pdf(doc)
    quality = _page_quality(page)
    pages = [{
        "page_no": 1,
        "width": float(page.rect.width),
        "height": float(page.rect.height),
        "text": ocr_text,
        "source": "ocr" if ocr_text else "image",
        "blocks": blocks,
        "quality": quality,
    }]
    doc.close()
    return {
        "parser": "OCR" if ocr_text else "NONE",
        "ocr_engine": engine,
        "preview_pdf_path": rel,
        "full_text": ocr_text,
        "char_count": len(ocr_text.replace(" ", "")),
        "pages": pages,
        "visual_marks": visual,
        "extracted_fields": {},
        "format_features": {},
        "warnings": warnings,
        "ocr_failed": bool(warn),
        "page_count": 1,
    }


def _parse_docx(path: Path) -> dict:
    try:
        from docx import Document
        from docx.oxml.ns import qn
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError:
        return _empty("NONE", warnings=["未安装 python-docx"])
    try:
        doc = Document(str(path))
    except Exception as e:
        return _empty("NONE", warnings=[f"DOCX 无法打开：{e}"])
    paras = []
    for block in doc.iter_inner_content():
        if isinstance(block, Paragraph) and block.text.strip():
            paras.append(block.text)
        elif isinstance(block, Table):
            for row in block.rows:
                paras.append("\t".join(c.text.strip() for c in row.cells))
    full = "\n".join(paras)
    fonts, sizes, spacings = [], [], []
    for p in doc.paragraphs:
        if p.runs:
            for r in p.runs:
                if r.font.name:
                    fonts.append(r.font.name)
                if r.font.size:
                    sizes.append(round(r.font.size.pt, 1))
        if p.paragraph_format.line_spacing:
            spacings.append(p.paragraph_format.line_spacing)
    section = doc.sections[0] if doc.sections else None
    margin = None
    if section:
        margin = round((section.left_margin.cm + section.right_margin.cm) / 2, 2) if section.left_margin else None
    features = {
        "font": fonts[0] if fonts else None,
        "size_pt": sizes[0] if sizes else None,
        "line_spacing": spacings[0] if spacings else None,
        "margin_cm": margin,
        "converted_from": "docx",
    }
    rel = _docx_to_preview_pdf(path, full)
    pages = _docx_preview_pages(STORAGE_DIR / rel)
    return {
        "parser": "DOCX",
        "ocr_engine": None,
        "preview_pdf_path": rel,
        "full_text": full,
        "char_count": len(full.replace(" ", "")),
        "pages": pages,
        "visual_marks": {"seals": [], "signatures": []},
        "extracted_fields": {},
        "format_features": features,
        "warnings": ["由 DOCX 重排生成文本预览，版式与原文件可能不同；坐标对应预览 PDF"],
        "page_count": len(pages),
    }


def _docx_to_preview_pdf(path: Path, text: str) -> str:
    from html import escape
    import fitz

    rel = f"previews/{path.stem}.pdf"
    out = STORAGE_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    html = "<p>由 DOCX 转换</p>" + "".join(f"<p>{escape(line) or '&nbsp;'}</p>" for line in text.splitlines())
    story = fitz.Story(html=html, em=11, user_css="body { margin: 0; font-size: 11pt; line-height: 1.5; } p { margin: 0 0 8pt; }")
    page_rect = fitz.paper_rect("a4")
    buf = io.BytesIO()
    with fitz.DocumentWriter(buf) as writer:
        story.write(writer, lambda _index, _filled: (page_rect, page_rect + (36, 36, -36, -36), None))
    # 仅在转换成功后写入完整 PDF；失败交给解析任务报告，不伪造可用预览。
    out.write_bytes(buf.getvalue())
    return rel


def _docx_preview_pages(path: Path) -> list[dict]:
    import fitz

    pages = []
    with fitz.open(path) as preview:
        for page in preview:
            blocks = []
            for block in page.get_text("dict").get("blocks", []):
                for line in block.get("lines", []):
                    text = "".join(span.get("text", "") for span in line.get("spans", []))
                    if text.strip():
                        blocks.append({"text": text, "bbox": list(line["bbox"]), "conf": 1.0})
            pages.append({
                "page_no": page.number + 1, "width": float(page.rect.width), "height": float(page.rect.height),
                "text": "\n".join(block["text"] for block in blocks), "source": "docx", "blocks": blocks,
                "quality": {"dpi": None, "blur_score": None, "is_blurry": False},
            })
    return pages


def _ocr_page(page) -> tuple[str, list, Optional[str], Optional[str]]:
    try:
        import fitz
        from ai.ocr import ocr_pixmap
        pix = page.get_pixmap(dpi=150, colorspace=fitz.csRGB, alpha=False)
        text, blocks, engine, warning = ocr_pixmap(pix)
        # OCR uses image pixels; every page block is stored in PDF points.
        sx, sy = page.rect.width / pix.width, page.rect.height / pix.height
        normalized = []
        for block in blocks:
            item = dict(block)
            box = item.get("bbox")
            if box and len(box) == 4:
                item["bbox"] = [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy]
            normalized.append(item)
        return text, normalized, engine, warning
    except Exception as e:
        from diagnostics import log_exception
        log_exception("ocr.page_failed", e)
        return "", [], None, "OCR 页面渲染或识别失败，请检查材料后重试"


def _visual_from_pdf(doc) -> dict:
    try:
        from ai.vision import detect_visual
        return detect_visual(doc)
    except Exception:
        return {"seals": [], "signatures": []}


def _page_quality(page) -> dict:
    try:
        from ai.vision import page_blur
        return page_blur(page)
    except Exception:
        return {"dpi": 150, "blur_score": None, "is_blurry": False}


def render_page_png(preview_pdf_path: str, page_no: int, scale: float = 1.5) -> tuple[bytes, int, float, float]:
    import fitz
    path = STORAGE_DIR / preview_pdf_path
    doc = fitz.open(path)
    idx = max(0, min(page_no - 1, doc.page_count - 1))
    page = doc[idx]
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    data = pix.tobytes("png")
    w, h, n = float(page.rect.width), float(page.rect.height), doc.page_count
    doc.close()
    return data, n, w, h
