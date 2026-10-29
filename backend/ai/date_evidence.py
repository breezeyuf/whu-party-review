"""Recognition certainty and date syntax are separate evidence properties."""
from math import isfinite

from sqlalchemy import and_
from models import ParseResult, TimeNodeExtraction, Material, Submission, ArchiveTimeNode

MIN_CONFIDENCE = .7
REVIEW_CODE = 'DATE-REVIEW'
REVIEW_PREFIX = '待人工确认日期：'


def _get(row, key, default=None):
    return row.get(key, default) if isinstance(row, dict) else getattr(row, key, default)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        return None
    try:
        number = float(value)
    except (ValueError, OverflowError):
        return None
    return number if isfinite(number) and 0 <= number <= 1 else None


def evidence_state(row, pages=None):
    """Return usable, reason, and recognition-bounded confidence; never erase values."""
    confidence = _number(_get(row, 'confidence'))
    if _get(row, 'method') == 'MANUAL':
        return True, None, confidence
    has_value = any(_get(row, key) is not None for key in ('value_date', 'value_end_date', 'hours'))
    if not has_value:
        return True, None, confidence  # Invalid syntax still needs the valid-date rule.
    reason = None
    existing = _get(row, 'invalid_reason') or ''
    if existing.startswith(REVIEW_PREFIX):
        reason = existing[len(REVIEW_PREFIX):]
    if _get(row, 'confidence') is not None and (confidence is None or confidence < MIN_CONFIDENCE):
        reason = '抽取置信度不足，须对照原图确认'
    page_no, raw, box = _get(row, 'page_no'), _get(row, 'raw_text') or '', _get(row, 'bbox')
    range_values = {_get(row, 'value_date'), _get(row, 'value_end_date')} - {None} if _get(row, 'value_end_date') else set()
    found_range = set()
    has_ocr_range = False
    for page in pages or []:
        if range_values:
            from ai.dates import find_dates
            blocks = []
            for block in page.get('blocks') or []:
                matched = {hit['date'] for hit in find_dates(block.get('text') or '') if hit.get('date')} & range_values
                if matched:
                    blocks.append(block)
                    found_range.update(matched)
            if not blocks and page.get('page_no') != page_no:
                continue
        elif page.get('page_no') != page_no:
            continue
        if page.get('handwritten') or page.get('handwriting_hint'):
            reason = '原图含手写标记，须人工确认'
        ocr = page.get('source') in ('ocr', 'scan', 'image')
        if not range_values:
            blocks = [block for block in page.get('blocks') or [] if
                      (raw and raw in (block.get('text') or '')) or (box and block.get('bbox') == box)]
        if ocr:
            has_ocr_range = has_ocr_range or bool(range_values)
            scores = [_number(block.get('conf')) for block in blocks]
            if not scores or any(score is None for score in scores):
                reason = '缺少可核实的 OCR 日期置信度'
                confidence = 0.0
            else:
                confidence = min([score for score in scores] + ([confidence] if confidence is not None else []))
                if confidence < MIN_CONFIDENCE:
                    reason = 'OCR 日期识别置信度不足，须对照原图确认'
        if any(block.get('handwritten') or block.get('handwriting_hint') for block in blocks):
            reason = '原文块含手写标记，须人工确认'
        for review in page.get('vision_reviews') or []:
            if review.get('status') == 'pending' and (not box or not review.get('bbox') or _overlap(box, review['bbox'])):
                reason = '日期所在区域的视觉复核尚未确认'
    if has_ocr_range and not range_values.issubset(found_range):
        reason = "日期区间有端点缺少可核对原文，须人工确认完整区间"
    return not bool(reason), reason, confidence


def _overlap(a, b):
    try:
        return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])
    except (TypeError, IndexError):
        return True


def bound_extractions(rows, pages):
    for row in rows:
        usable, reason, confidence = evidence_state(row, pages)
        if confidence is not None:
            row['confidence'] = confidence
        if not usable:
            row['invalid_reason'] = REVIEW_PREFIX + reason
    return rows


def states_for(db, rows):
    ids = {_get(row, 'material_version_id') for row in rows} - {None}
    parsed = {row.version_id: row for row in db.query(ParseResult).filter(ParseResult.version_id.in_(ids)).all()} if ids else {}
    states, pending_ids = {}, []
    for row in rows:
        version = _get(row, 'material_version_id')
        state = evidence_state(row, parsed[version].pages if version in parsed else None)
        states[row.id] = state
        if not state[0] and _get(row, 'material_id') is not None:
            pending_ids.append(row.id)
    if pending_ids:
        approved = {result[0] for result in db.query(TimeNodeExtraction.id)
                    .join(Material, Material.id == TimeNodeExtraction.material_id)
                    .join(Submission, Submission.id == Material.submission_id)
                    .join(ArchiveTimeNode, and_(ArchiveTimeNode.archive_id == TimeNodeExtraction.archive_id,
                          ArchiveTimeNode.node_code == TimeNodeExtraction.node_code, ArchiveTimeNode.locked.is_(True)))
                    .filter(TimeNodeExtraction.id.in_(pending_ids), Submission.status == 'FILED').all()}
        for oid in approved:
            states[oid] = (True, None, states[oid][2])
    return states
