from __future__ import annotations

from datetime import date

from ai.dsl import DSLContext, NodeVal, required_for_stage, run_checks
from ai.types import IssueDraft, loc
from models import TimeRule
from utils import as_date, get_setting


def nodes_from_map(node_map: dict) -> dict[str, NodeVal]:
    out = {}
    for code, n in node_map.items():
        out[code] = NodeVal(
            code=code,
            date=as_date(n.get("date") or n.get("value_date")),
            end=as_date(n.get("end") or n.get("end_date") or n.get("value_end_date")),
            hours=n.get("hours"),
            seq=[as_date(x) for x in (n.get("seq") or []) if as_date(x)],
            has_conflict=bool(n.get("has_conflict")),
            invalid_reason=n.get("invalid_reason"),
            missing=not bool(as_date(n.get("date") or n.get("value_date")) or n.get("seq")),
        )
    return out


def run_timeline(db, submission, node_map: dict, upload_date: date | None = None, *, rule_set=None, context=None):
    cal = context.calendar if context else get_setting(db, "calendar", {})
    holidays = {as_date(x) for x in (cal.get("holidays") or []) if as_date(x)}
    extra = {as_date(x) for x in (cal.get("extra_workdays") or []) if as_date(x)}
    nodes = nodes_from_map(node_map)
    today = context.today if context else date.today()
    ctx = DSLContext(nodes, today, upload_date or today, holidays, extra)
    rules = rule_set.rows("time_rules") if rule_set else db.query(TimeRule).filter(TimeRule.is_active.is_(True)).order_by(TimeRule.sort_order).all()
    drafts: list[IssueDraft] = []
    results = []
    derived = {}
    stage = submission.stage_code
    for rule in rules:
        applies = rule.applies_stages or []
        if applies and stage not in applies and str(stage) not in [str(x) for x in applies]:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "不适用当前阶段"})
            continue
        checks = (rule.params or {}).get("checks") or []
        # inject stage for required
        cres = []
        skip_all = False
        fail = False
        last_fail = None
        for chk in checks:
            if chk.get("op") == "required":
                r = required_for_stage(ctx, chk.get("nodes_by_stage") or {}, stage)
            else:
                r = run_checks(ctx, [chk])[0]
            cres.append(r)
            if r.skipped:
                skip_all = True
                continue
            if not r.ok:
                fail = True
                last_fail = r
        if any(chk.get("op") == "derive" for chk in checks):
            derived.update({k: v.isoformat() for k, v in ctx.derived.items()})
            results.append({"rule_code": rule.code, "result": "PASS", "derived": derived})
            continue
        if fail:
            r = last_fail
            msg = (rule.message_template or rule.name)
            for code, n in ctx.nodes.items():
                if n.date:
                    msg = msg.replace("{" + code + "}", n.date.isoformat())
            drafts.append(IssueDraft(
                category="TIME",
                severity=rule.severity if rule.severity != "CALC" else "INFO",
                title=rule.name,
                description=r.reason or msg,
                rule_code=rule.code,
                rule_basis=rule.basis,
                location=loc(node_code=r.node_code),
                actual_value=r.actual,
                expected_value=r.expected,
                fingerprint_parts=(rule.code, r.node_code or "", r.actual or ""),
            ))
            results.append({"rule_code": rule.code, "result": "FAIL", "issue_ids": []})
        elif skip_all and not any(not x.skipped and x.ok for x in cres):
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "节点缺失"})
        else:
            results.append({"rule_code": rule.code, "result": "PASS"})
    snapshot = {
        "nodes": {c: (n.date.isoformat() if n.date else None) for c, n in ctx.nodes.items()},
        "derived": derived,
    }
    return snapshot, drafts, results
