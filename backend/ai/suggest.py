from __future__ import annotations

import re

from models import SuggestionTemplate
from ai.types import IssueDraft


def fill_suggestions(db, drafts: list[IssueDraft], extra: dict | None = None, *, rule_set=None) -> None:
    rows = rule_set.rows("suggestion_templates") if rule_set else db.query(SuggestionTemplate).filter(SuggestionTemplate.is_active.is_(True)).all()
    tpls = {t.rule_code: t for t in rows if t.rule_code}
    by_code = {t.code: t for t in rows}
    extra = extra or {}
    for d in drafts:
        if d.suggestion:
            continue
        tpl = tpls.get(d.rule_code) or by_code.get({
            "COMPLETENESS": "SUG_MISSING_MATERIAL",
            "R-T21": "SUG_DATE_INVALID",
            "R-C01": "SUG_TERM",
            "R-F03": "SUG_SIGNATURE",
            "R-F04": "SUG_SEAL",
            "R-C03": "SUG_JUDGEMENT",
        }.get(d.rule_code or "", "SUG_FORMAT" if d.category == "FORMAT" else "SUG_TIME_INTERVAL" if d.category == "TIME" else "SUG_CONTENT"))
        if not tpl:
            d.suggestion = d.description
            continue
        vals = {
            "材料名": extra.get("material_name") or "",
            "节点名": (d.location or {}).get("node_code") or "",
            "实际值": d.actual_value or "",
            "要求值": d.expected_value or "",
            "页码": (d.location or {}).get("page_no") or "",
            "原文": (d.location or {}).get("snippet") or "",
            "标准写法": d.expected_value or "",
            "规则依据": d.rule_basis or "",
            "规则名": d.title,
            "问题描述": d.description,
        }
        text = tpl.template_text
        for k, v in vals.items():
            text = text.replace("{" + k + "}", str(v))
        text = re.sub(r"\{[^}]+\}", "", text)
        d.suggestion = text
        d.suggestion_example = tpl.example_text
