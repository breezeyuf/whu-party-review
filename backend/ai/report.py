from __future__ import annotations

from collections import Counter, defaultdict

from ai.types import IssueDraft
from security import fingerprint


def summarize(drafts: list[IssueDraft], materials_checked: int, rule_results: list[dict]) -> dict:
    by_cat = Counter(d.category for d in drafts)
    by_sev = Counter(d.severity for d in drafts)
    skipped = sum(1 for r in rule_results if r.get("result") == "SKIPPED")
    failed = sum(1 for r in rule_results if r.get("result") == "FAIL")
    ran = len(rule_results)
    return {
        "total": len(drafts),
        "by_category": dict(by_cat),
        "by_severity": dict(by_sev),
        "needs_judgement": sum(1 for d in drafts if d.needs_human_judgement),
        "materials_checked": materials_checked,
        "rules_run": ran,
        "rules_failed": failed,
        "rules_skipped": skipped,
    }


def recommend(summary: dict, drafts: list[IssueDraft]) -> str:
    if summary.get("by_severity", {}).get("BLOCK"):
        return "SUGGEST_RETURN"
    if summary.get("by_severity", {}).get("WARN") or any(d.needs_human_judgement for d in drafts):
        return "NEEDS_REVIEW"
    return "SUGGEST_PASS"


def issue_fp(d: IssueDraft) -> str:
    loc = d.location or {}
    snippet = (loc.get("snippet") or "")
    parts = d.fingerprint_parts or (d.rule_code, d.material_id, loc.get("node_code"), loc.get("field"), snippet)
    return fingerprint(*parts)


def group_by_category(issues: list) -> dict:
    grouped = defaultdict(list)
    for it in issues:
        grouped[it.category].append(it)
    return dict(grouped)
