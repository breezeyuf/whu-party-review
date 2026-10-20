from __future__ import annotations

import re
from collections import defaultdict

from ai.types import IssueDraft, loc
from models import CheckRule, ParseResult, PoliticalTerm, SensitivePhrase


def run_content(db, submission, materials, versions, parses: dict[int, ParseResult], types, llm_enabled: bool):
    rules = (
        db.query(CheckRule)
        .filter(CheckRule.category == "CONTENT", CheckRule.is_active.is_(True))
        .order_by(CheckRule.sort_order)
        .all()
    )
    terms = db.query(PoliticalTerm).filter(PoliticalTerm.is_active.is_(True)).all()
    phrases = db.query(SensitivePhrase).filter(SensitivePhrase.is_active.is_(True)).all()
    drafts: list[IssueDraft] = []
    results = []
    texts = {}
    for m in materials:
        if m.status != "ACTIVE":
            continue
        ver = versions.get(m.id)
        pr = parses.get(ver.id) if ver else None
        texts[m.id] = (pr.corrected_text or pr.full_text or "") if pr else ""
    llm_error = None
    for rule in rules:
        if rule.engine == "LLM" and not llm_enabled:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "需大模型，当前为仅规则模式"})
            continue
        hit = False
        is_llm = (rule.engine or "RULE") == "LLM"
        applies = rule.applies_to or []
        for m in materials:
            if m.status != "ACTIVE":
                continue
            t = types.get(m.type_id)
            code = t.code if t else None
            if applies and code not in applies:
                continue
            ver = versions.get(m.id)
            pr = parses.get(ver.id) if ver else None
            text = texts.get(m.id) or ""
            if is_llm:
                # 首次调用失败后本份报告不再重复调用，避免任务长时间挂起
                if llm_error:
                    found = []
                else:
                    found, llm_error = _apply_llm_rule(db, rule, m, ver, text, submission.archive)
            else:
                found = _apply_rule(rule, m, ver, pr, t, text, terms, phrases, submission, texts, types)
            for d in found:
                drafts.append(d)
                hit = True
        if is_llm and llm_error:
            # 大模型不可用时降级为跳过，不产生语义结论，也不中断整份报告
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": f"大模型调用失败：{llm_error}"})
        else:
            results.append({"rule_code": rule.code, "result": "FAIL" if hit else "PASS"})
    return drafts, results


def _apply_llm_rule(db, rule, m, ver, text: str, archive=None) -> tuple[list[IssueDraft], "str | None"]:
    """按 CONTENT_CHECK 模板做语义核查。返回为空表示未发现或不可用。"""
    text = (text or "").strip()
    if not text:
        return [], None
    from ai.llm import chat_json

    variables = {
        "rules": f"{rule.code} {rule.name}：{rule.basis or rule.message_template or ''}",
        "text": text,
    }
    try:
        parsed, err, _ms = chat_json(
            db, "CONTENT_CHECK", variables, override={"max_attempts": 1}, archive=archive,
        )
    except Exception as exc:  # 大模型异常不得中断检查
        return [], str(exc)[:200]
    if err:
        return [], err
    if not isinstance(parsed, dict):
        return [], None
    out = []
    for item in (parsed.get("issues") or [])[:10]:
        if not isinstance(item, dict):
            continue
        snippet = str(item.get("snippet") or "")[:80]
        reason = str(item.get("reason") or rule.message_template or "疑似不规范表述")[:200]
        try:
            conf = float(item.get("confidence") or 0.6)
        except (TypeError, ValueError):
            conf = 0.6
        conf = min(1.0, max(0.0, conf))
        out.append(IssueDraft(
            category="CONTENT", severity=rule.severity, title=rule.name, description=reason,
            rule_code=rule.code, rule_basis=rule.basis, material_id=m.id,
            material_version_id=ver.id if ver else None,
            location=loc(material_id=m.id, snippet=snippet),
            actual_value=snippet, expected_value=rule.message_template,
            suggestion=rule.message_template,
            needs_human_judgement=True,  # 语义结论一律转人工研判，不下定性政治结论
            confidence=conf, source="AI_LLM",
            fingerprint_parts=(rule.code, m.id, snippet, reason),
        ))
    return out, None


def _apply_rule(rule, m, ver, pr, t, text, terms, phrases, submission, texts, types) -> list[IssueDraft]:
    code = rule.code
    out = []
    if code == "R-C01":
        for term in terms:
            if term.term_type == "VARIANT":
                for w in term.wrong_variants or []:
                    if w and w in text:
                        out.append(_d(rule, m, ver, f"不规范写法“{w}”", w, term.standard_text,
                                      suggestion=f"第页“{w}”表述不规范，标准写法为“{term.standard_text}”，请修改。"))
            elif term.term_type == "SEQUENCE":
                items = term.sequence_items or []
                present = [x for x in items if x in text]
                if len(present) >= 2:
                    idxs = [text.find(x) for x in present]
                    if idxs != sorted(idxs):
                        out.append(_d(rule, m, ver, "指导思想并列顺序不规范", "、".join(present), term.standard_text))
                    if len(present) < len(items) and any(x in text for x in items[:2]):
                        out.append(_d(rule, m, ver, "指导思想并列表述有缺项", "、".join(present), term.standard_text))
        return out
    if code == "R-C03":
        for ph in phrases:
            if ph.category != "IDEOLOGY":
                continue
            if _match_phrase(ph, text):
                d = _d(rule, m, ver, f"疑似存在需研判表述：“{ph.phrase}”", ph.phrase, ph.risk_note or "人工研判",
                       suggestion=f"第页“{ph.phrase}”需审核员研判：{ph.risk_note or ''}。")
                d.needs_human_judgement = True
                out.append(d)
        return out
    if code == "R-C04":
        for ph in phrases:
            if ph.category != "MOTIVATION":
                continue
            if _match_phrase(ph, text):
                d = _d(rule, m, ver, f"入党动机表述需关注：“{ph.phrase}”", ph.phrase, "理想信念导向",
                       suggestion=ph.suggestion)
                d.needs_human_judgement = True
                out.append(d)
        return out
    if code == "R-C05":
        elems = (t.element_template if t else None) or []
        missing = []
        for el in elems:
            if not el.get("required"):
                continue
            kws = el.get("keywords") or [el.get("name")]
            if not any(k and k in text for k in kws):
                missing.append(el.get("name") or el.get("key"))
        if missing:
            out.append(_d(rule, m, ver, f"缺少内容要素：{'、'.join(missing)}", "缺", "应包含 " + "、".join(missing)))
        return out
    if code == "R-C06":
        arch = submission.archive
        fields = (pr.corrected_fields or pr.extracted_fields or {}) if pr else {}
        if fields.get("name") and arch.real_name and fields["name"] != arch.real_name:
            out.append(_d(rule, m, ver, "姓名与档案不一致", fields["name"], arch.real_name))
        if fields.get("student_no") and arch.student_no and fields["student_no"] != arch.student_no:
            out.append(_d(rule, m, ver, "学号与档案不一致", fields["student_no"], arch.student_no))
        if fields.get("birth_date") and arch.birth_date and fields["birth_date"] != arch.birth_date.isoformat():
            out.append(_d(rule, m, ver, "出生日期与档案不一致", str(fields["birth_date"]), arch.birth_date.isoformat()))
        if fields.get("gender") and arch.gender and fields["gender"] != arch.gender:
            out.append(_d(rule, m, ver, "性别与档案不一致", fields["gender"], arch.gender))
        return out
    if code == "R-C10":
        th = float((rule.params or {}).get("threshold") or 0.8)
        grams = _ngrams(text)
        if not grams:
            return out
        for oid, ot in texts.items():
            if oid == m.id:
                continue
            sim = _jaccard(grams, _ngrams(ot))
            if sim >= th:
                out.append(_d(rule, m, ver, f"与材料 {oid} 文本相似度 {sim:.2f}", f"{sim:.2f}", f"<{th}"))
        return out
    return out


def _match_phrase(ph, text: str) -> bool:
    if ph.match_type == "REGEX":
        try:
            return re.search(ph.phrase, text) is not None
        except re.error:
            return False
    return ph.phrase in text


def _ngrams(text: str, n: int = 3) -> set[str]:
    s = re.sub(r"\s+", "", text or "")
    if len(s) < n:
        return set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _d(rule, m, ver, desc, actual, expected, suggestion=None) -> IssueDraft:
    return IssueDraft(
        category="CONTENT", severity=rule.severity, title=rule.name, description=desc,
        rule_code=rule.code, rule_basis=rule.basis, material_id=m.id,
        material_version_id=ver.id if ver else None,
        location=loc(material_id=m.id, snippet=str(actual)[:80]),
        actual_value=str(actual), expected_value=str(expected),
        suggestion=suggestion or rule.message_template,
        needs_human_judgement=rule.needs_human_judgement,
        fingerprint_parts=(rule.code, m.id, desc),
    )
