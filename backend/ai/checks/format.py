from __future__ import annotations

from ai.types import IssueDraft, loc
from models import CheckRule, ParseResult


def _applies(rule: CheckRule, type_code: str | None) -> bool:
    applies = rule.applies_to or []
    if not applies:
        return True
    return type_code in applies


def run_format(db, materials: list, versions: dict, parses: dict[int, ParseResult], types: dict):
    rules = (
        db.query(CheckRule)
        .filter(CheckRule.category == "FORMAT", CheckRule.is_active.is_(True))
        .order_by(CheckRule.sort_order)
        .all()
    )
    drafts: list[IssueDraft] = []
    results = []
    for rule in rules:
        hit = False
        skipped = False
        for m in materials:
            if m.status != "ACTIVE":
                continue
            t = types.get(m.type_id)
            code = t.code if t else None
            if not _applies(rule, code):
                continue
            ver = versions.get(m.id)
            pr = parses.get(ver.id) if ver else None
            issues = _check_one(rule, m, ver, pr, t)
            if issues is None:
                skipped = True
                continue
            for d in issues:
                drafts.append(d)
                hit = True
        if skipped and not hit:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "参数未设定或无可检材料"})
        else:
            results.append({"rule_code": rule.code, "result": "FAIL" if hit else "PASS"})
    return drafts, results


def _check_one(rule: CheckRule, m, ver, pr: ParseResult | None, t) -> list[IssueDraft] | None:
    fmt = (t.format_requirements if t else {}) or {}
    text = ""
    fields = {}
    pages = []
    visual = {"seals": [], "signatures": []}
    features = {}
    if pr:
        text = pr.corrected_text or pr.full_text or ""
        fields = pr.corrected_fields or pr.extracted_fields or {}
        pages = pr.pages or []
        visual = pr.visual_marks or visual
        features = pr.format_features or {}
    code = rule.code
    if code == "R-F01":
        need = (fmt.get("doc_elements") or [])
        missing = []
        mapping = {
            "title": fields.get("title") or (text.splitlines()[0] if text.strip() else None),
            "salutation": fields.get("salutation") or ("党组织" in text[:200]),
            "body": len(text) > 80,
            "closing": fields.get("closing") or ("此致" in text or "敬礼" in text),
            "signature": fields.get("signature_name") or any(k in text[-200:] for k in ("签名", "汇报人", "申请人")),
            "date": fields.get("signature_date") or any(ch in text[-120:] for ch in ("年", "-")),
        }
        for k in need:
            if not mapping.get(k):
                missing.append(k)
        if missing:
            return [_draft(rule, m, ver, f"缺少文书要素：{','.join(missing)}", ",".join(missing), "应包含 " + ",".join(need))]
        return []
    if code == "R-F02":
        raw = fields.get("signature_date_raw") or ""
        if fields.get("signature_date") and "年" not in str(raw) and raw:
            return [_draft(rule, m, ver, "落款日期未按“××××年××月××日”书写", raw, "××××年××月××日")]
        return []
    if code == "R-F03":
        slots = fmt.get("signature_slots") or []
        if not slots:
            return []
        presents = visual.get("signatures") or []

        def _slot_present(s):
            kws = [k for k in (s.get("keywords") or []) if k]
            for p in presents:
                if not p.get("present"):
                    continue
                pslot = p.get("slot") or ""
                if not kws or any(k in pslot or pslot in k for k in kws):
                    return True
            return False

        missing = []
        for s in slots:
            if _slot_present(s) or fields.get("signature_name"):
                continue
            missing.append(s.get("slot") or "签名")
        if missing:
            return [_draft(rule, m, ver, f"{missing[0]}未检测到签名", "无", "应有签名",
                           suggestion=f"《{m.title}》{missing[0]} 未检测到签名，请本人（或相关负责人）补签。")]
        return []
    if code == "R-F04":
        slots = fmt.get("seal_slots") or []
        if not slots:
            return []
        seals = visual.get("seals") or []
        low = [s for s in seals if (s.get("conf") or 0) < 0.6]
        if not seals:
            return [_draft(rule, m, ver, "未检测到党组织印章", "无", "应有印章",
                           suggestion=f"《{m.title}》盖章位未检测到党组织印章，请联系相应党组织补盖。")]
        if low:
            d = _draft(rule, m, ver, "印章置信度较低，请人工核对", str(low[0].get("conf")), "≥ 0.6")
            d.needs_human_judgement = True
            d.confidence = 0.55
            return [d]
        return []
    if code == "R-F05":
        if not fmt.get("handwriting_required"):
            return []
        if pr and pr.char_count < 80:
            return [_draft(rule, m, ver, "手写材料可识别文本过少", str(pr.char_count), "可辨识正文")]
        return []
    if code == "R-F06":
        mins = (rule.params or {}).get("min_chars") or {}
        tcode = t.code if t else None
        need = mins.get(tcode)
        if not need:
            return None
        n = (pr.char_count if pr else 0) or 0
        if n < int(need):
            return [_draft(rule, m, ver, f"正文字数 {n}，不足 {need}", str(n), str(need))]
        return []
    if code == "R-F07":
        params = rule.params or {}
        blur_th = params.get("blur_threshold", 60)
        for p in pages:
            q = p.get("quality") or {}
            if q.get("is_blurry") or (q.get("blur_score") is not None and q["blur_score"] < blur_th):
                return [_draft(rule, m, ver, f"第 {p.get('page_no')} 页清晰度不足", str(q.get("blur_score")), f"拉普拉斯方差 ≥ {blur_th}")]
            if p.get("source") in ("scan", "image") and not (p.get("text") or "").strip():
                d = _draft(rule, m, ver, "扫描件文本缺失，需人工核对", "空", "可识别文本")
                d.needs_human_judgement = True
                d.confidence = 0.5
                return [d]
        return []
    if code in ("R-F08", "R-F09"):
        if not rule.is_active:
            return None
        if code == "R-F08" and features:
            layout = (fmt.get("docx_layout") or (rule.params or {}).get("docx_layout") or {})
            problems = []
            if layout.get("font") and features.get("font") and features["font"] != layout["font"]:
                problems.append(f"字体 {features['font']}")
            if problems:
                return [_draft(rule, m, ver, "版式与模板不一致：" + ",".join(problems), str(features), str(layout))]
        return []
    return []


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
