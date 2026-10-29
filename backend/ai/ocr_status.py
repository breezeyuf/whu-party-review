"""Page review state is separate from technical parse completion."""
from __future__ import annotations

from ai.types import IssueDraft, loc


EMPTY_OCR_WARNING = 'OCR 未识别到可用文字；空白页、照片或手写内容需对照原图人工核对'
REVIEW_CODE = 'OCR-REVIEW'


def needs_review(page):
    status = page.get('ocr_status')
    if status is not None:
        return status == 'NEEDS_REVIEW'
    # Old parsed documents predate the explicit page state.
    return page.get('source') in ('scan', 'image', 'ocr') and not (page.get('text') or '').strip()


def pending_pages(parsed):
    return [page for page in (parsed.pages or []) if needs_review(page)]


def review_warning(page_no, *, retained=False):
    message = f'第 {page_no} 页{EMPTY_OCR_WARNING}'
    if retained:
        message = f'本次重新解析第 {page_no} 页未识别到可用文字；当前仍显示此前保留的解析及人工校正，请对照原图核对'
    return {'code': REVIEW_CODE, 'page_no': page_no, 'message': message, 'retained_previous': retained}


def refresh_warnings(parsed):
    previous = list(parsed.warnings or [])
    retained = {warning.get('page_no') for warning in previous if isinstance(warning, dict)
                and warning.get('code') == REVIEW_CODE and warning.get('retained_previous')}
    parsed.warnings = [warning for warning in previous if not (
        isinstance(warning, dict) and warning.get('code') == REVIEW_CODE)] + [
        review_warning(page['page_no'], retained=page['page_no'] in retained) for page in pending_pages(parsed)]


def run_ocr_review(materials, versions, parses):
    """Always run, independently of optional image-quality rule R-F07."""
    drafts, results = [], []
    for material in materials:
        version = versions.get(material.id)
        parsed = parses.get(version.id) if version else None
        if parsed is None:
            continue
        for page in pending_pages(parsed):
            number = page.get('page_no')
            drafts.append(IssueDraft(
                category='FORMAT', severity='WARN', title='OCR 待人工复核',
                description=f'第 {number} 页未识别到可用文字，可能为空白页、照片或手写内容，请对照原图核对。',
                rule_code=REVIEW_CODE, material_id=material.id, material_version_id=version.id,
                location=loc(material_id=material.id, page_no=number),
                actual_value='OCR 文本待核对', expected_value='人工核实页面内容',
                suggestion='请在解析文本面板核对原图，必要时补充校正文本，并保存该页的核对确认。',
                needs_human_judgement=True, confidence=0.5,
                fingerprint_parts=(REVIEW_CODE, material.id, number),
            ))
            results.append({'rule_code': REVIEW_CODE, 'result': 'FAIL', 'material_id': material.id,
                            'page_no': number, 'reason': 'OCR 文本待人工核对，不自动判定材料不合格'})
    return drafts, results
