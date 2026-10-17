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
            if ocr_text:
                page_text = ocr_text
                blocks = ocr_blocks
                source = "ocr"
                parser = "MIXED" if parser == "PDF_TEXT" else "OCR"
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
        warnings.append("图片型材料未启用 OCR，需人工核对文本")
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
        "page_count": 1,
    }


def _parse_docx(path: Path) -> dict:
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        return _empty("NONE", warnings=["未安装 python-docx"])
    try:
        doc = Document(str(path))
    except Exception as e:
        return _empty("NONE", warnings=[f"DOCX 无法打开：{e}"])
    paras = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
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
    pages = [{
        "page_no": 1,
        "width": 595.3,
        "height": 841.9,
        "text": full,
        "source": "docx",
        "blocks": [{"text": t, "bbox": None, "conf": 1.0} for t in paras[:80]],
        "quality": {"dpi": None, "blur_score": None, "is_blurry": False},
    }]
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
        "warnings": ["由 DOCX 转换预览，坐标为文本版估算"],
        "page_count": 1,
    }


def _docx_to_preview_pdf(path: Path, text: str) -> str:
    rel = f"previews/{path.stem}.pdf"
    out = STORAGE_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        html = "<div style='font-size:11pt;line-height:1.6;font-family:sans-serif'>"
        html += "<p style='color:#666'>由 DOCX 转换</p>"
        for line in text.splitlines()[:80]:
            esc = (line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            html += f"<p>{esc or '&nbsp;'}</p>"
        html += "</div>"
        page.insert_htmlbox(page.rect + (36, 36, -36, -36), html)
        doc.save(out)
        doc.close()
    except Exception:
        out.write_bytes(b"%PDF-1.4\n% converted\n")
    return rel


def _ocr_page(page) -> tuple[str, list, Optional[str], Optional[str]]:
    try:
        from ai.ocr import ocr_pixmap
        pix = page.get_pixmap(dpi=150)
        return ocr_pixmap(pix)
    except Exception as e:
        return "", [], None, f"OCR 不可用：{e}"


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
