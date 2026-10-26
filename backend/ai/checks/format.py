from __future__ import annotations

from ai.types import IssueDraft, loc
from ai.evidence import effective_text, effective_fields, char_count
from models import CheckRule, ParseResult
from ai.layout import _measurement


def _applies(rule: CheckRule, type_code: str | None) -> bool:
    applies = rule.applies_to or []
    if not applies:
        return True
    return type_code in applies


def run_format(db, materials: list, versions: dict, parses: dict[int, ParseResult], types: dict, *, rule_set=None):
    rules = [r for r in rule_set.rows("check_rules") if r.category == "FORMAT"] if rule_set else (
        db.query(CheckRule)
        .filter(CheckRule.category == "FORMAT", CheckRule.is_active.is_(True))
        .order_by(CheckRule.sort_order)
        .all()
    )
    drafts: list[IssueDraft] = []
    results = []
    for rule in rules:
        if getattr(rule,'engine','RULE') != 'RULE':
            results.append({'rule_code':rule.code,'result':'SKIPPED','reason':'形式规则仅支持规则检查'})
            continue
        hit = False
        skipped = False
        checked = False
        for m in materials:
            if m.status != "ACTIVE":
                continue
            t = types.get(m.type_id)
            code = t.code if t else None
            if not _applies(rule, code):
                continue
            ver = versions.get(m.id)
            pr = parses.get(ver.id) if ver else None
            try:
                issues = _check_one(rule, m, ver, pr, t)
            except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
                issues = None
            if issues is None:
                skipped = True
                continue
            checked = True
            for d in issues:
                drafts.append(d)
                hit = True
        if (skipped or not checked) and not hit:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "参数未设定或无可检材料"})
        else:
            results.append({"rule_code": rule.code, "result": "FAIL" if hit else "PASS"})
    return drafts, results


def _check_one(rule: CheckRule, m, ver, pr: ParseResult | None, t) -> list[IssueDraft] | None:
    if pr is None:
        return None
    fmt = (t.format_requirements if t else {}) or {}
    text = ""
    fields = {}
    pages = []
    visual = {"seals": [], "signatures": []}
    features = {}
    if pr:
        text = effective_text(pr)
        fields = effective_fields(pr)
        pages = pr.pages or []
        visual = pr.visual_marks or visual
        features = pr.format_features or {}
    code = rule.code
    if code == "R-F01":
        need = (fmt.get("doc_elements") or [])
        if not isinstance(need, list) or not need:
            return None
        missing = []
        mapping = {
            "title": fields.get("title") or (text.splitlines()[0] if text.strip() else None),
            "salutation": fields.get("salutation") or ("党组织" in text[:200]),
            "body": len(text) > 80,
            "closing": fields.get("closing") or ("此致" in text or "敬礼" in text),
            "signature": fields.get("signature_name") or any(k in text[-200:] for k in ("签名", "汇报人", "申请人")),
            "date": fields.get("signature_date") or any(ch in text[-120:] for ch in ("年", "-")),
        }
        if any(not isinstance(k, str) or k not in mapping for k in need):
            return None
        for k in need:
            if not mapping.get(k):
                missing.append(k)
        if missing:
            return [_draft(rule, m, ver, f"缺少文书要素：{','.join(missing)}", ",".join(missing), "应包含 " + ",".join(need))]
        return []
    if code == "R-F02":
        raw = fields.get("signature_date_raw") or ""
        if not fields.get('signature_date') or not raw:
            return None
        if fields.get("signature_date") and "年" not in str(raw) and raw:
            return [_draft(rule, m, ver, "落款日期未按“××××年××月××日”书写", raw, "××××年××月××日")]
        return []
    if code == "R-F03":
        slots = fmt.get("signature_slots") or []
        if not slots:
            return None
        return _check_marks(rule,m,ver,slots,visual,'signature')
    if code == "R-F04":
        slots = fmt.get("seal_slots") or []
        if not slots:
            return None
        return _check_marks(rule,m,ver,slots,visual,'seal')
    if code == "R-F05":
        if not fmt.get("handwriting_required"):
            return None
        if char_count(text) < 80:
            return [_draft(rule, m, ver, "手写材料可识别文本过少", str(char_count(text)), "可辨识正文")]
        return []
    if code == "R-F06":
        mins = (rule.params or {}).get("min_chars") or {}
        tcode = t.code if t else None
        need = mins.get(tcode)
        required = _measurement(need)
        if required is None or not required.is_integer():
            return None
        n = char_count(text)
        if n < required:
            return [_draft(rule, m, ver, f"正文字数 {n}，不足 {need}", str(n), str(need))]
        return []
    if code == "R-F07":
        params = rule.params or {}
        measured, unknown = False, False
        for p in pages:
            q = p.get("quality") or {}
            if p.get('source') not in ('scan','image','ocr'):
                continue
            blur_th = _measurement(q.get('blur_threshold', params.get('blur_threshold',60)), allow_zero=True)
            min_dpi = _measurement(q.get('min_dpi',params.get('min_dpi',150)))
            if blur_th is None or min_dpi is None:
                return None
            score = _measurement(q.get('blur_score'), allow_zero=True)
            measured |= score is not None
            unknown |= score is None
            source_dpi = _measurement(q.get('source_dpi'))
            if q.get('source_dpi') is not None and source_dpi is None:
                unknown = True
            if source_dpi is not None and source_dpi < min_dpi:
                return [_draft(rule, m, ver, f"第 {p.get('page_no')} 页原始扫描分辨率不足", f'{source_dpi:.0f} DPI', f"≥ {min_dpi} DPI")]
            if q.get("is_blurry") or (score is not None and score < blur_th):
                return [_draft(rule, m, ver, f"第 {p.get('page_no')} 页清晰度不足", str(q.get("blur_score")), f"拉普拉斯方差 ≥ {blur_th}")]
            if p.get("source") in ("scan", "image") and not (p.get("text") or "").strip():
                d = _draft(rule, m, ver, "扫描件文本缺失，需人工核对", "空", "可识别文本")
                d.needs_human_judgement = True
                d.confidence = 0.5
                return [d]
        return [] if measured and not unknown else None
    if code == 'R-F08':
        from ai.layout import check_layout
        layout = fmt.get('docx_layout') or (rule.params or {}).get('docx_layout') or {}
        if not layout or not features:
            return None
        problems, complete = check_layout(features, layout)
        if problems:
            return [_draft(rule, m, ver, '版式与模板不一致：' + '；'.join(problems[:8]), '；'.join(problems[:8]), str(layout))]
        return [] if complete else None
    if code == 'R-F09':
        params = rule.params or {}
        orientation, side, minimum = params.get('orientation'), params.get('binding_side', 'left'), params.get('min_binding_margin_cm')
        if orientation not in (None, 'portrait', 'landscape') or side not in ('left','right','top','bottom'):
            return None
        if not orientation and minimum is None:
            return None
        if minimum is not None:
            minimum = _measurement(minimum, allow_zero=True)
            if minimum is None:
                return None
        complete, problems = True, []
        sections = features.get('sections') or []
        if orientation:
            measured = [s.get('orientation') for s in sections] if sections else [
                ('landscape' if p['width'] > p['height'] else 'portrait') for p in pages if p.get('width') and p.get('height') and p.get('source') != 'docx']
            if not measured or any(value not in ('portrait', 'landscape') for value in measured): complete = False
            if any(value in ('portrait', 'landscape') and value != orientation for value in measured): problems.append('页面方向不符合要求')
        if minimum is not None:
            margins = [_measurement((s.get('margins_cm') or {}).get(side), allow_zero=True) for s in sections]
            if not margins or any(value is None for value in margins): complete = False
            if any(value is not None and value < minimum for value in margins): problems.append('装订侧页边距不足')
        if problems:
            return [_draft(rule, m, ver, '；'.join(problems), '；'.join(problems), str(params))]
        return [] if complete else None
    return None


def _check_marks(rule,m,ver,slots,visual,kind):
    import fitz
    marks = visual.get('signatures' if kind=='signature' else 'seals') or []
    anchors = visual.get('signatures' if kind=='signature' else 'anchors') or []
    used_marks, used_anchors, out = set(), set(), []
    for slot in slots:
        keywords = [k for k in slot.get('keywords',[]) if k]
        found = next(((i,a) for i,a in enumerate(anchors) if i not in used_anchors
                      and any(k in a.get('slot','') for k in keywords)), None)
        anchor = found[1] if found else None
        if found: used_anchors.add(found[0])
        if slot.get('bbox') and slot.get('page_no'):
            anchor={'bbox':slot['bbox'],'page_no':slot['page_no']}
        matched = None
        if anchor:
            area=fitz.Rect(anchor['bbox'])
            if kind=='seal': area=area+(-55,-35,55,65)
            matched = next(((i,mark) for i,mark in enumerate(marks) if i not in used_marks
                            and mark.get('page_no')==anchor['page_no'] and mark.get('bbox')
                            and not (area & fitz.Rect(mark['bbox'])).is_empty
                            and (kind=='seal' or mark.get('present'))),None)
        if matched: used_marks.add(matched[0])
        label=slot.get('slot') or ('签名' if kind=='signature' else '印章')
        status='检测到候选墨迹' if matched else '未可靠定位到所需墨迹'
        # Presence/shape is not identity or authenticity. All heuristic outcomes
        # require explicit human handling, rather than blocking on uncertain absence.
        issue=_draft(rule,m,ver,f'{label}：{status}，请对照原图核对',status,'逐个核对签名/盖章位')
        issue.needs_human_judgement=True; issue.confidence=0.6; issue.severity='WARN'
        if anchor: issue.location.update(page_no=anchor['page_no'],bbox=anchor['bbox'])
        issue.fingerprint_parts=(rule.code,m.id,label,anchor.get('page_no') if anchor else None)
        out.append(issue)
    return out


def _draft(rule, m, ver, desc, actual, expected, suggestion=None) -> IssueDraft:
    return IssueDraft(
        category="FORMAT", severity=rule.severity, title=rule.name, description=desc,
        rule_code=rule.code, rule_basis=rule.basis, material_id=m.id,
        material_version_id=ver.id if ver else None,
        location=loc(material_id=m.id),
        actual_value=actual, expected_value=expected,
        suggestion=suggestion or rule.message_template,
        needs_human_judgement=rule.needs_human_judgement,
        fingerprint_parts=(rule.code, m.id, desc),
    )
