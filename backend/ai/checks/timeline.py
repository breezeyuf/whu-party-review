from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date

from ai.dsl import CheckResult, DSLContext, NodeVal, required_for_stage, run_checks
from ai.types import IssueDraft, loc
from models import TimeRule
from utils import as_date, get_setting, now


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


def _valid_date_sources(ctx: DSLContext, node_map: dict, check: dict):
    selected = check.get("nodes") or "*"
    codes = list(node_map) if selected == "*" else ([selected] if isinstance(selected, str) else selected)
    results = []
    for code in codes:
        node = node_map.get(code)
        if not node:
            continue
        sources = node.get("sources") or []
        if not sources:
            # Older callers may supply a date explicitly. A missing upload date
            # cannot be replaced by the day the check happens to run.
            one = ctx.nodes[code]
            result = run_checks(DSLContext({code: one}, ctx.today, ctx.upload_date, ctx.holidays, ctx.extra), [check])[0]
            result.node_code = code
            results.append((result, None))
            continue
        for source in sources:
            value_date = as_date(source.get("date"))
            end_date = as_date(source.get("end_date"))
            upload_day = as_date(source.get("upload_date"))
            one = NodeVal(code=code, date=value_date, end=end_date,
                          invalid_reason=source.get("invalid_reason"),
                          missing=not bool(value_date or end_date))
            result = run_checks(DSLContext({code: one}, ctx.today, upload_day, ctx.holidays, ctx.extra), [check])[0]
            result.node_code = code
            if not result.ok:
                result.actual = (end_date or value_date).isoformat() if end_date or value_date else (one.invalid_reason or code)
                result.expected = f"≤ {upload_day.isoformat()}" if upload_day else "合法日期"
                result.reason = (one.invalid_reason or
                                 f"{code} 的材料日期 {result.actual} 晚于该材料版本上传日 {upload_day.isoformat()}")
            results.append((result, source))
    if not results:
        results.append((CheckResult(ok=True, skipped=True, reason="缺少日期来源"), None))
    return results


def _issue_evidence(node_map: dict, check: dict, result: CheckResult, source: dict | None):
    """Locate a failed check in the extraction records used for its nodes."""
    if source is not None:
        codes = [result.node_code or source.get("node_code")]
        sources = [source]
    else:
        actual_codes = re.findall(r"\bT\d{2}\b", result.actual or "")
        refs = actual_codes + [result.node_code]
        refs += [check.get(key) for key in ("b", "node", "x", "at", "seq", "a", "birth", "from", "to")]
        refs += check.get("nodes") if isinstance(check.get("nodes"), list) else []
        codes = []
        for ref in refs:
            if not isinstance(ref, str):
                continue
            code = ref.split(".", 1)[0].replace("[*]", "")
            if code in node_map and code not in codes:
                codes.append(code)
        sources = []
        for code in codes:
            node = node_map.get(code) or {}
            candidates = node.get("sources") or []
            effective = node.get("date") or node.get("value_date")
            candidates = sorted(candidates, key=lambda item: item.get("date") != effective)
            sources.extend(candidates)
    primary = sources[0] if sources else None
    code = codes[0] if codes else result.node_code
    location = loc(node_code=code,
                   extraction_id=primary.get("extraction_id") if primary else None,
                   material_id=primary.get("material_id") if primary else None,
                   version_id=primary.get("version_id") if primary else None,
                   page_no=primary.get("page_no") if primary else None,
                   bbox=primary.get("bbox") if primary else None)
    if len(sources) > 1:
        location["related_sources"] = [loc(node_code=row.get("node_code"), extraction_id=row.get("extraction_id"),
                                           material_id=row.get("material_id"), version_id=row.get("version_id"),
                                           page_no=row.get("page_no"), bbox=row.get("bbox")) for row in sources]
    return primary, location


def run_timeline(db, submission, node_map: dict, upload_date: date | None = None, *, rule_set=None, context=None):
    cal = context.calendar if context else get_setting(db, "calendar", {})
    holidays = {as_date(x) for x in (cal.get("holidays") or []) if as_date(x)}
    extra = {as_date(x) for x in (cal.get("extra_workdays") or []) if as_date(x)}
    nodes = nodes_from_map(node_map)
    today = context.today if context else now().date()
    ctx = DSLContext(nodes, today, upload_date, holidays, extra)
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
        params = rule.params or {}
        checks = params.get("checks") if isinstance(params, Mapping) else None
        if not isinstance(params, Mapping) or (checks is not None and not isinstance(checks, (list, tuple))):
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "时间规则参数无效"})
            continue
        checks = checks or []
        if not checks:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "未配置校验条件"})
            continue
        # inject stage for required
        cres = []
        skip_all = False
        fail = False
        required_failed = False
        last_fail = None
        date_failures = []
        date_incomplete = False
        for chk in checks:
            if not isinstance(chk, Mapping):
                cres.append(CheckResult(ok=False, skipped=True, reason="时间规则参数无效"))
                skip_all = True
                continue
            try:
                if chk.get("op") == "required":
                    required = chk.get("nodes_by_stage")
                    if not isinstance(required, Mapping) or any(
                        not isinstance(values, (list, tuple)) or any(not isinstance(code, str) for code in values)
                        for values in required.values()
                    ):
                        raise ValueError("invalid required nodes")
                    evaluated = [(required_for_stage(ctx, required, stage), None)]
                elif chk.get("op") == "valid_date":
                    selected = chk.get("nodes", "*")
                    if selected != "*" and (not isinstance(selected, (list, tuple)) or any(not isinstance(code, str) for code in selected)):
                        raise ValueError("invalid selected nodes")
                    evaluated = _valid_date_sources(ctx, node_map, chk)
                else:
                    evaluated = [(run_checks(ctx, [chk])[0], None)]
            except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
                evaluated = [(CheckResult(ok=False, skipped=True, reason="时间规则参数无效或日期计算超出范围"), None)]
            for r, source in evaluated:
                cres.append(r)
                if r.skipped:
                    skip_all = True
                    if chk.get("op") == "valid_date":
                        date_incomplete = True
                    continue
                if not r.ok:
                    fail = True
                    required_failed = required_failed or chk.get("op") == "required"
                    last_fail = (r, source, chk)
                    if chk.get("op") == "valid_date" and source is not None:
                        date_failures.append((r, source, chk))
        # Cross-node comparisons need all inputs. In contrast, a date-only rule
        # checks each material source independently: an unknown upload day must
        # not suppress a proven invalid date from another source.
        date_only = all(isinstance(chk, Mapping) and chk.get("op") == "valid_date" for chk in checks)
        invalid = next((r.reason for r in cres if r.skipped and r.reason.startswith("时间规则参数无效")), None)
        if skip_all and (invalid or not (required_failed or (date_only and fail))):
            reason = invalid or ("缺少真实材料上传日期或日期来源" if date_incomplete else "节点缺失")
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": reason})
            continue
        if fail:
            msg = (rule.message_template or rule.name)
            for code, n in ctx.nodes.items():
                if n.date:
                    msg = msg.replace("{" + code + "}", n.date.isoformat())
            failures = date_failures or [last_fail]
            for r, source, chk in failures:
                primary, location = _issue_evidence(node_map, chk, r, source)
                sourced = source is not None
                drafts.append(IssueDraft(
                    category="TIME",
                    severity=rule.severity if rule.severity != "CALC" else "INFO",
                    title=rule.name,
                    description=r.reason or msg,
                    rule_code=rule.code,
                    rule_basis=rule.basis,
                    material_id=primary.get("material_id") if primary else None,
                    material_version_id=primary.get("version_id") if primary else None,
                    location=location,
                    actual_value=r.actual,
                    expected_value=r.expected,
                    fingerprint_parts=(rule.code, r.node_code or "", source.get("material_id"),
                                       source.get("version_id"), source.get("seq_index"),
                                       source.get("date"), source.get("end_date"),
                                       source.get("upload_date"), r.actual) if sourced
                    else (rule.code, r.node_code or "", r.actual or ""),
                ))
            failed_result = {"rule_code": rule.code, "result": "FAIL", "issue_ids": []}
            if date_only and date_incomplete:
                failed_result["skipped_sources"] = sum(r.skipped for r in cres)
            results.append(failed_result)
        elif date_incomplete:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "缺少真实材料上传日期或日期来源"})
        elif skip_all:
            results.append({"rule_code": rule.code, "result": "SKIPPED", "reason": "节点缺失"})
        else:
            passed = {"rule_code": rule.code, "result": "PASS"}
            if any(chk.get("op") == "derive" for chk in checks):
                derived.update({k: v.isoformat() for k, v in ctx.derived.items()})
                passed["derived"] = dict(derived)
            results.append(passed)
    snapshot = {
        "nodes": {c: (n.date.isoformat() if n.date else None) for c, n in ctx.nodes.items()},
        "date_inputs": [source for node in node_map.values() for source in (node.get("sources") or [])],
        "derived": derived,
    }
    return snapshot, drafts, results
