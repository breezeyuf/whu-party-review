from __future__ import annotations

import re
import math
from collections import defaultdict

from ai.types import IssueDraft, loc
from ai.evidence import effective_text, effective_fields
from models import CheckRule, ParseResult, PoliticalTerm, SensitivePhrase


def run_content(db, submission, materials, versions, parses: dict[int, ParseResult], types, llm_enabled: bool, *, rule_set=None, timeline=None, similarity_cache=None):
    rules = [r for r in rule_set.rows("check_rules") if r.category == "CONTENT"] if rule_set else (
        db.query(CheckRule)
        .filter(CheckRule.category == "CONTENT", CheckRule.is_active.is_(True))
        .order_by(CheckRule.sort_order)
        .all()
    )
    terms = rule_set.rows("political_terms") if rule_set else db.query(PoliticalTerm).filter(PoliticalTerm.is_active.is_(True)).all()
    phrases = rule_set.rows("sensitive_phrases") if rule_set else db.query(SensitivePhrase).filter(SensitivePhrase.is_active.is_(True)).all()
    drafts: list[IssueDraft] = []
    results = []
    texts = {}
    field_sets = {}
    for m in materials:
        if m.status != "ACTIVE":
            continue
        ver = versions.get(m.id)
        pr = parses.get(ver.id) if ver else None
        texts[m.id] = effective_text(pr)
        field_sets[m.id] = effective_fields(pr)
    llm_error = None
    # Keep rule evidence and semantic evidence as separate results for mixed rules.
    expanded = []
    for rule in rules:
        if rule.engine not in ('RULE', 'LLM', 'RULE_LLM'):
            results.append({'rule_code': rule.code, 'result': 'SKIPPED', 'reason': '不支持的规则引擎'})
            continue
        if rule.engine == 'RULE_LLM':
            from types import SimpleNamespace
            values = {key: getattr(rule, key, None) for key in ('code','name','basis','message_template','severity','applies_to','params','needs_human_judgement')}
            expanded.extend([SimpleNamespace(**values, engine='RULE'), SimpleNamespace(**values, engine='LLM')])
        else:
            expanded.append(rule)
    rules = expanded
    for rule in rules:
        if rule.engine == "LLM" and not llm_enabled:
            results.append({"rule_code": rule.code, "engine": "LLM", "result": "SKIPPED", "reason": "需大模型，当前为仅规则模式"})
            continue
        hit = False
        is_llm = (rule.engine or "RULE") == "LLM"
        checked = False
        skipped = False
        similarity_evidence = []
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
            if pr is None:
                skipped = True
                continue
            if is_llm:
                if not text.strip():
                    continue
                # 首次调用失败后本份报告不再重复调用，避免任务长时间挂起
                if llm_error:
                    found = []
                else:
                    found, llm_error = _apply_llm_rule(db, rule, m, ver, text, submission.archive, rule_set=rule_set, timeline=timeline)
                    checked = True
            else:
                if rule.code == 'R-C10':
                    from ai.similarity import compare_batch
                    try:
                        threshold = float((rule.params or {}).get('threshold', 0.8))
                    except (TypeError, ValueError, AttributeError):
                        skipped = True
                        continue
                    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
                        skipped = True
                        continue
                    cache_key = (m.id, ver.id)
                    if similarity_cache is not None and cache_key in similarity_cache:
                        compared = similarity_cache[cache_key]
                    else:
                        compared = compare_batch(db, submission, m, text, threshold)
                        if similarity_cache is not None:
                            similarity_cache[cache_key] = compared
                    if compared:
                        similarity_evidence.append({
                            'material_id': m.id, 'version_id': ver.id,
                            'threshold': threshold, 'score': compared['score'], 'count': compared['count'],
                            **compared['comparison'],
                        })
                    found = None if compared is None else []
                    if compared and compared['score'] >= threshold:
                        found = [_d(rule, m, ver, f"与同批次其他学生同类材料的最高相似度 {compared['score']:.2f}，请人工核对",
                                    f"{compared['score']:.2f}", f'<{threshold}')]
                        found[0].needs_human_judgement = True
                else:
                    try:
                        found = _apply_rule(rule, m, ver, pr, t, text, terms, phrases, submission, texts, types, field_sets)
                    except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
                        found = None
                if found is None:
                    skipped = True
                    continue
                checked = True
            for d in found:
                drafts.append(d)
                hit = True
        if is_llm and llm_error:
            # 大模型不可用时降级为跳过，不产生语义结论，也不中断整份报告
            results.append({"rule_code": rule.code, "engine": "LLM", "result": "SKIPPED",
                            "reason": f"大模型调用失败：{llm_error}", "error": llm_error})
        elif not checked or (skipped and not hit):
            result = {"rule_code": rule.code, "engine": rule.engine, "result": "SKIPPED",
                      "reason": "无适用材料、必要参数或可验证证据"}
            if similarity_evidence:
                result["comparison_snapshot"] = similarity_evidence
            results.append(result)
        else:
            result = {"rule_code": rule.code, "result": "FAIL" if hit else "PASS"}
            if is_llm:
                result["engine"] = "LLM"
            if similarity_evidence:
                result["comparison_snapshot"] = similarity_evidence
            results.append(result)
    if llm_error:
        # A RULE_ONLY report must not retain partial semantic findings or claim they passed.
        drafts = [d for d in drafts if d.source != "AI_LLM"]
        for result in results:
            if result.get("engine") == "LLM":
                result.update(result="SKIPPED", error=llm_error,
                              reason=f"大模型检查未完成，本报告仅保留规则结果：{llm_error}")
    return drafts, results


def _apply_llm_rule(db, rule, m, ver, text: str, archive=None, *, rule_set=None, timeline=None) -> tuple[list[IssueDraft], "str | None"]:
    """按 CONTENT_CHECK 模板做语义核查。返回为空表示未发现或不可用。"""
    text = (text or "").strip()
    if not text:
        return [], None
    from ai.llm import chat_json

    variables = {
        "rules": f"{rule.code} {rule.name}：{rule.basis or rule.message_template or ''}",
        "text": text,
    }
    if rule.code == 'R-C07':
        variables['timeline'] = timeline or {}
    try:
        parsed, err, _ms = chat_json(
            db, "CONTENT_CHECK", variables, archive=archive, rule_set=rule_set,
        )
    except Exception as exc:  # 大模型异常不得中断检查，也不回传可能包含敏感信息的异常原文
        from diagnostics import log_exception
        log_exception("model.content_check_failed", exc, material_id=m.id)
        return [], "大模型调用异常"
    if err:
        return [], err
    out = []
    for item in parsed["issues"]:
        if item.get("rule_code") and item["rule_code"] != rule.code:
            return [], "大模型返回的问题规则编号不匹配"
        conf = item["confidence"]
        if conf < 0.5:
            continue
        snippet = item["snippet"][:80]
        reason = item["reason"][:200]
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
        if len(out) >= 10:
            break
    return out, None


def _apply_rule(rule, m, ver, pr, t, text, terms, phrases, submission, texts, types, field_sets=None) -> list[IssueDraft]:
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
        if not isinstance(elems, list) or any(not isinstance(el, dict) for el in elems):
            return None
        required = [el for el in elems if el.get('required')]
        if not required:
            return None
        missing = []
        for el in required:
            kws = el.get("keywords") or [el.get("name")]
            if not isinstance(kws, list) or not kws or any(not isinstance(k, str) or not k for k in kws):
                return None
            label = el.get('name') or el.get('key')
            if not isinstance(label, str) or not label:
                return None
            if not any(k and k in text for k in kws):
                missing.append(label)
        if missing:
            out.append(_d(rule, m, ver, f"缺少内容要素：{'、'.join(missing)}", "缺", "应包含 " + "、".join(missing)))
        return out
    if code == "R-C06":
        arch = submission.archive
        fields = effective_fields(pr)
        compared = False
        for field,attr,label in [('name','real_name','姓名'),('student_no','student_no','学号'),('birth_date','birth_date','出生日期'),
                                 ('gender','gender','性别'),('ethnicity','ethnicity','民族'),('native_place','native_place','籍贯'),('branch','branch','支部')]:
            expected=getattr(arch,attr,None)
            if field=='birth_date' and expected: expected=expected.isoformat()
            if field=='branch' and expected: expected=getattr(expected,'name',None)
            actual=fields.get(field)
            if not actual: continue
            normalize=lambda value: re.sub(r'\s+','',str(value))
            if expected:
                compared = True
            if expected and normalize(actual)!=normalize(expected):
                issue=_d(rule,m,ver,f'{label}与档案不一致，请人工核对',str(actual),str(expected))
                issue.location['field']=field; issue.needs_human_judgement=True
                out.append(issue)
            elif not expected:
                peers={normalize(f[field]) for mid,f in (field_sets or {}).items() if mid!=m.id and f.get(field)}
                compared |= bool(peers)
                if any(value!=normalize(actual) for value in peers):
                    issue=_d(rule,m,ver,f'{label}在同一提交包材料间存在冲突，档案尚未提供基准',str(actual),'核对原件并完善档案基准')
                    issue.location['field']=field; issue.needs_human_judgement=True
                    out.append(issue)
        return out if compared else None
    if code == "R-C10":
        return None  # Requires the batch query performed by run_content.
    if code == 'R-C09':
        # Compare only explicitly attributed quotations to administrator-provided references.
        references = rule.params.get('references') if isinstance(rule.params, dict) else None
        if not isinstance(references, list):
            return None
        checked = False
        for ref in references:
            if not isinstance(ref, dict):
                continue
            title, standard = ref.get('title'), ref.get('text')
            if not all(isinstance(value, str) and value.strip() for value in (title, standard, ref.get('source'))):
                continue
            pattern = r'《' + re.escape(title) + r'》[^“”"\n]{0,40}[“"]([^”"\n]+)[”"]'
            for match in re.finditer(pattern, text):
                checked = True
                quote = match.group(1)
                normalize = lambda value: re.sub(r'\s+', '', value)
                if normalize(quote) not in normalize(standard):
                    issue = _d(rule, m, ver, f'《{title}》引用与配置原文不一致，请人工核对', quote, standard[:500])
                    issue.needs_human_judgement = True
                    issue.rule_basis = str(ref['source'])
                    out.append(issue)
        return out if checked else None
    return None


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
