"""Optional LLM enrichment; validated evidence, deterministic fallbacks."""
from ai.llm import chat_json
from ai.dates import parse_date, find_dates
from ai.extract import _locate
from ai.node_sources import eligible_nodes, bound_sources


def classify_fallback(db, text, result, types, threshold, *, archive=None, rule_set=None):
    if result['type_source'] == 'DECLARED' or result['type_confidence'] >= threshold or not text.strip():
        return result, None
    options = {t.code:t for t in types if t.is_active}
    answer, error, _ = chat_json(db, 'CLASSIFY', {'types': '\n'.join(f'{t.code}: {t.name}' for t in options.values()), 'text':text}, archive=archive, rule_set=rule_set)
    if error: return result, error
    chosen = options.get(answer['type_code'])
    confidence = answer['confidence']
    if not chosen or confidence < 0.5: return result, '模型分类无有效候选或置信度不足'
    return {'type_id':chosen.id,'type_code':chosen.code,'type_name':chosen.name,'type_source':'AI',
            'type_confidence':confidence,'type_status':'AUTO' if confidence >= threshold else 'NEEDS_CONFIRM'}, None


def extract_fallback(db, text, pages, extractions, nodes, *, archive=None, rule_set=None, material_type=None):
    nodes = eligible_nodes(nodes, material_type)
    found = {r['node_code'] for r in extractions if r.get('value_date')}
    missing = {n.code:n for n in nodes if n.code not in found and n.value_kind != 'DERIVED'}
    if not missing or not text.strip(): return extractions, None
    answer, error, _ = chat_json(db,'EXTRACT',{'nodes':'\n'.join(f'{n.code}: {n.name}' for n in missing.values()),'text':text},archive=archive,rule_set=rule_set)
    if error: return extractions, error
    result = list(extractions)
    accepted = set()
    for item in answer['dates']:
        code, raw = item['node_code'], item['raw_text']
        day, _, invalid = parse_date(item['date'])
        # Model cannot invent evidence, dates, codes, coordinates or override rule dates.
        if code not in missing or item['confidence'] < 0.5 or raw not in text or invalid or not day:
            continue
        if not any(hit.get('date') == day for hit in find_dates(raw)): continue
        if (code, day) in accepted or (missing[code].value_kind != 'DATE_SEQ' and any(c==code for c,d in accepted)): continue
        page, box = _locate(pages, raw)
        result = [r for r in result if not (r['node_code']==code and not r.get('value_date'))]
        from ai.date_evidence import REVIEW_PREFIX
        review = REVIEW_PREFIX + '模型仅提供单个日期，须核对完整起止区间' if missing[code].value_kind == 'DATE_RANGE' else None
        result.append({'node_code':code,'seq_index':sum(1 for r in result if r['node_code']==code),
            'value_date':day,'raw_text':raw,'confidence':item['confidence'],'method':'LLM','page_no':page,'bbox':box,
            'invalid_reason': review})
        accepted.add((code,day))
    return bound_sources(result, nodes, material_type), None


def polish_suggestions(db, drafts, *, archive=None, rule_set=None):
    max_calls = 5
    completed = {}
    calls = 0
    for draft in drafts:
        if draft.category != 'CONTENT' or not draft.suggestion: continue
        original = draft.suggestion
        key = (original,draft.description)
        if key in completed:
            draft.suggestion = completed[key]
            continue
        if calls >= max_calls:
            continue  # Keep the deterministic rule template beyond this budget.
        calls += 1
        answer, error, _ = chat_json(db,'SUGGEST',{'template':original,'vars':'','issue':draft.description},archive=archive,rule_set=rule_set)
        if error: return error
        from ai.desensitize import desensitize_text
        # Compare against exactly the redacted requirement sent to the model.
        from ai.llm import llm_config
        required = desensitize_text(original,archive) if llm_config(db).get('desensitize') is not False else original
        if required in answer['suggestion'] and len(answer['suggestion']) <= 2000:
            draft.suggestion = answer['suggestion']
        completed[key] = draft.suggestion
    return None
