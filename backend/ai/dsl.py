from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Optional

from ai.dates import (
    add_duration,
    age_years,
    describe_interval,
    duration_meets,
    is_workday,
    workdays_between,
)


@dataclass
class NodeVal:
    code: str
    date: Optional[date] = None
    end: Optional[date] = None
    hours: Optional[float] = None
    seq: list[date] = field(default_factory=list)
    has_conflict: bool = False
    invalid_reason: Optional[str] = None
    missing: bool = True


@dataclass
class CheckResult:
    ok: bool
    skipped: bool = False
    reason: str = ""
    actual: str = ""
    expected: str = ""
    node_code: Optional[str] = None


class DSLContext:
    def __init__(self, nodes: dict[str, NodeVal], today: date, upload_date: Optional[date], holidays=None, extra=None):
        self.nodes = nodes
        self.today = today
        self.upload_date = upload_date
        self.holidays = holidays or set()
        self.extra = extra or set()
        self.derived: dict[str, date] = {}

    def resolve(self, ref: str) -> tuple[Optional[date], bool]:
        if not ref:
            return None, True
        if ref == "$today":
            return self.today, False
        if ref == "$upload_date":
            return self.upload_date, self.upload_date is None
        if ref.endswith(".end"):
            code = ref[:-4]
            node = self.nodes.get(code) or self._derived_node(code)
            if not node or node.missing or not (node.end or node.date):
                return None, True
            return node.end or node.date, False
        if ref.endswith(".hours"):
            return None, True
        if ref.endswith("[*]"):
            return None, True
        node = self.nodes.get(ref) or self._derived_node(ref)
        if not node or node.missing or not node.date:
            return None, True
        return node.date, False

    def _derived_node(self, code: str) -> Optional[NodeVal]:
        if code in self.derived:
            return NodeVal(code=code, date=self.derived[code], missing=False)
        return None

    def seq(self, ref: str) -> list[date]:
        code = ref.replace("[*]", "")
        node = self.nodes.get(code)
        if not node:
            return []
        return list(node.seq or [])


def run_checks(ctx: DSLContext, checks: list[dict]) -> list[CheckResult]:
    results = []
    for chk in checks:
        op = chk.get("op")
        fn = OPS.get(op)
        if not fn:
            results.append(CheckResult(ok=False, skipped=True, reason=f"未知算子 {op}"))
            continue
        results.append(fn(ctx, chk))
    return results


def _age_at_least(ctx: DSLContext, p: dict) -> CheckResult:
    birth, miss1 = ctx.resolve(p["birth"])
    at, miss2 = ctx.resolve(p["at"])
    if miss1 or miss2:
        return CheckResult(ok=True, skipped=True, reason="节点缺失", node_code=p.get("at"))
    years = int(p.get("years", 18))
    actual = age_years(birth, at)
    ok = actual >= years
    return CheckResult(
        ok=ok, actual=f"{actual} 周岁", expected=f"≥ {years} 周岁",
        node_code=p.get("at"), reason="" if ok else f"申请时 {actual} 周岁，不足 {years} 周岁",
    )


def _before(ctx: DSLContext, p: dict) -> CheckResult:
    a, m1 = ctx.resolve(p["a"])
    b, m2 = ctx.resolve(p["b"])
    if m1 or m2:
        return CheckResult(ok=True, skipped=True, reason="节点缺失")
    strict = bool(p.get("strict", True))
    ok = a < b if strict else a <= b
    if ok and p.get("min_gap"):
        ok = duration_meets(a, b, p["min_gap"]["value"], p["min_gap"]["unit"], ctx.holidays, ctx.extra)
    if ok and p.get("max_gap"):
        gap = p["max_gap"]
        ok = not duration_meets(a, b, gap["value"] + (0 if gap["unit"] != "DAY" else 0), gap["unit"], ctx.holidays, ctx.extra) or True
        # max_gap: b-a <= max
        from dateutil.relativedelta import relativedelta
        unit = gap["unit"].upper()
        val = gap["value"]
        if unit == "DAY":
            ok = (b - a).days <= val
        elif unit == "MONTH":
            ok = a + relativedelta(months=val) >= b
        elif unit == "YEAR":
            ok = a + relativedelta(years=val) >= b
        elif unit == "WORKDAY":
            ok = workdays_between(a, b, ctx.holidays, ctx.extra) <= val
    return CheckResult(
        ok=ok, actual=f"{a.isoformat()} vs {b.isoformat()}", expected="时间先后正确",
        reason="" if ok else f"{p['a']}={a} 应在 {p['b']}={b} 之前",
    )


def _between(ctx: DSLContext, p: dict) -> CheckResult:
    x, m0 = ctx.resolve(p["x"])
    lo, m1 = ctx.resolve(p["lower"])
    hi, m2 = ctx.resolve(p["upper"])
    if m0 or m1 or m2:
        return CheckResult(ok=True, skipped=True, reason="节点缺失")
    ok = lo <= x <= hi
    return CheckResult(ok=ok, actual=x.isoformat(), expected=f"{lo} ~ {hi}")


def _within(ctx: DSLContext, p: dict) -> CheckResult:
    a, m1 = ctx.resolve(p["a"])
    b, m2 = ctx.resolve(p["b"])
    if m1 or m2:
        return CheckResult(ok=True, skipped=True, reason="节点缺失")
    mx = p.get("max") or {}
    unit = mx.get("unit", "DAY")
    val = int(mx.get("value", 0))
    from dateutil.relativedelta import relativedelta
    if unit == "DAY":
        ok = (b - a).days <= val
    elif unit == "MONTH":
        ok = a + relativedelta(months=val) >= b
    elif unit == "YEAR":
        ok = a + relativedelta(years=val) >= b
    elif unit == "WORKDAY":
        ok = workdays_between(a, b, ctx.holidays, ctx.extra) <= val
    else:
        ok = (b - a).days <= val
    return CheckResult(
        ok=ok, actual=describe_interval(a, b), expected=f"≤ {val} {unit}",
        reason="" if ok else f"间隔 {describe_interval(a, b)} 超过 {val} {unit}",
    )


def _at_least(ctx: DSLContext, p: dict) -> CheckResult:
    a, m1 = ctx.resolve(p["a"])
    b, m2 = ctx.resolve(p["b"])
    if m1 or m2:
        return CheckResult(ok=True, skipped=True, reason="节点缺失")
    mn = p.get("min") or {}
    ok = duration_meets(a, b, int(mn.get("value", 0)), mn.get("unit", "DAY"), ctx.holidays, ctx.extra)
    return CheckResult(
        ok=ok, actual=describe_interval(a, b), expected=f"≥ {mn.get('value')} {mn.get('unit')}",
        node_code=p.get("b"),
        reason="" if ok else f"间隔 {describe_interval(a, b)}，不足 {mn.get('value')} {mn.get('unit')}",
    )


def _duration_min(ctx: DSLContext, p: dict) -> CheckResult:
    node_code = p.get("node")
    node = ctx.nodes.get(node_code)
    if node_code in ctx.derived:
        return CheckResult(ok=True, skipped=True, reason="派生节点无区间")
    if not node or node.missing:
        return CheckResult(ok=True, skipped=True, reason="节点缺失", node_code=node_code)
    mn = p.get("min") or {}
    or_hours = p.get("or_hours")
    ok_hours = or_hours is not None and node.hours is not None and node.hours >= or_hours
    start, end = node.date, node.end or node.date
    if not start or not end:
        if ok_hours:
            return CheckResult(ok=True, actual=f"{node.hours} 学时", expected=f"学时 ≥ {or_hours}", node_code=node_code)
        return CheckResult(ok=True, skipped=True, reason="区间不完整", node_code=node_code)
    ok_dur = duration_meets(start, end, int(mn.get("value", 0)), mn.get("unit", "DAY"), ctx.holidays, ctx.extra)
    ok = ok_dur or ok_hours
    actual = describe_interval(start, end)
    if node.hours:
        actual += f" / {node.hours} 学时"
    expected = f"≥ {mn.get('value')} {mn.get('unit')}"
    if or_hours:
        expected += f" 或学时 ≥ {or_hours}"
    return CheckResult(ok=ok, actual=actual, expected=expected, node_code=node_code,
                       reason="" if ok else "时长或学时不足")


def _seq_max_gap(ctx: DSLContext, p: dict) -> CheckResult:
    seq = ctx.seq(p.get("seq", "T06[*]"))
    start, m1 = ctx.resolve(p.get("from"))
    end, m2 = ctx.resolve(p.get("to"))
    if m1:
        start = seq[0] if seq else None
    if m2:
        end = seq[-1] if seq else None
    if start:
        seq = [d for d in seq if d >= start]
    if end:
        seq = [d for d in seq if d <= end]
    if start:
        seq = [start] + seq
    if end:
        seq = seq + [end]
    seq = sorted(set(seq))
    if len(seq) < 2:
        return CheckResult(ok=True, skipped=True, reason="序列不足")
    mx = p.get("max") or {"value": 3, "unit": "MONTH"}
    bad = []
    for a, b in zip(seq, seq[1:]):
        if not duration_meets(a, b, 0, "DAY"):
            continue
        # fail if gap > max
        from dateutil.relativedelta import relativedelta
        unit, val = mx.get("unit", "MONTH"), int(mx.get("value", 3))
        within = True
        if unit == "MONTH":
            within = a + relativedelta(months=val) >= b
        elif unit == "DAY":
            within = (b - a).days <= val
        if not within:
            bad.append((a, b))
    ok = not bad
    return CheckResult(ok=ok, actual=f"{len(bad)} 处超间隔" if bad else "间隔正常",
                       expected=f"相邻 ≤ {mx.get('value')} {mx.get('unit')}",
                       reason="" if ok else f"相邻间隔超过 {mx.get('value')} {mx.get('unit')}")


def _seq_period_count(ctx: DSLContext, p: dict) -> CheckResult:
    seq = ctx.seq(p.get("seq", "T06[*]"))
    start, m1 = ctx.resolve(p.get("from"))
    end, m2 = ctx.resolve(p.get("to"))
    if m1 or m2 or not start:
        return CheckResult(ok=True, skipped=True, reason="节点缺失")
    if not end:
        end = ctx.today
    months = max(1, int(p.get("period_months") or 3))
    min_n = int(p.get("min_per_period", 1))
    periods = []
    cur = start
    from dateutil.relativedelta import relativedelta
    while cur < end:
        nxt = cur + relativedelta(months=months)
        periods.append((cur, min(nxt, end)))
        cur = nxt
    if periods:
        last_start, last_end = periods[-1]
        if (last_end - last_start).days < 30 and len(periods) > 1:
            periods = periods[:-1]
    missing = 0
    for a, b in periods:
        n = sum(1 for d in seq if a <= d <= b)
        if n < min_n:
            missing += 1
    ok = missing == 0 and len(seq) >= len(periods)
    return CheckResult(
        ok=ok, actual=f"实交 {len(seq)} 份 / {len(periods)} 个周期",
        expected=f"每周期至少 {min_n} 份",
        reason="" if ok else f"{missing} 个周期不足",
    )


def _seq_in_range(ctx: DSLContext, p: dict) -> CheckResult:
    seq = ctx.seq(p.get("seq", "T06[*]"))
    start, m1 = ctx.resolve(p.get("from"))
    end, m2 = ctx.resolve(p.get("to"))
    if m1 or not seq:
        return CheckResult(ok=True, skipped=True, reason="节点缺失或无序列")
    if m2 or not end:
        end = ctx.today
    bad = [d for d in seq if d < start or d > end]
    ok = not bad
    return CheckResult(ok=ok, actual=f"{len(bad)} 份越界" if bad else "均在区间内",
                       expected=f"{start} ~ {end}")


def _consistent(ctx: DSLContext, p: dict) -> CheckResult:
    codes = p.get("nodes") or "*"
    bad = []
    if codes == "*":
        items = list(ctx.nodes.values())
    else:
        items = [ctx.nodes[c] for c in codes if c in ctx.nodes]
    for n in items:
        if n.has_conflict:
            bad.append(n.code)
    ok = not bad
    return CheckResult(ok=ok, actual=",".join(bad) if bad else "一致", expected="多来源一致",
                       reason="" if ok else f"节点冲突：{','.join(bad)}")


def _valid_date(ctx: DSLContext, p: dict) -> CheckResult:
    bad = []
    for n in ctx.nodes.values():
        if n.invalid_reason:
            bad.append(n.code)
        if ctx.upload_date is not None and n.date and n.date > ctx.upload_date:
            bad.append(n.code)
        if ctx.upload_date is not None and n.end and n.end > ctx.upload_date:
            bad.append(n.code)
    ok = not bad
    if ok and (ctx.upload_date is None or not ctx.nodes or all(n.missing for n in ctx.nodes.values())):
        return CheckResult(ok=True, skipped=True, reason="缺少真实材料上传日期或日期来源")
    return CheckResult(ok=ok, actual=",".join(sorted(set(bad))) if bad else "合法",
                       expected="日期合法且不晚于上传日")


def _required(ctx: DSLContext, p: dict) -> CheckResult:
    by_stage = p.get("nodes_by_stage") or {}
    stage = str(p.get("stage") or ctx.nodes.get("_stage") or "")
    # stage injected via ctx.derived['_stage_code'] optionally
    return CheckResult(ok=True, skipped=True, reason="由调用方注入阶段后执行")


def required_for_stage(ctx: DSLContext, nodes_by_stage: dict, stage: int) -> CheckResult:
    need = nodes_by_stage.get(str(stage)) or nodes_by_stage.get(stage) or []
    missing = []
    for code in need:
        n = ctx.nodes.get(code)
        if not n or n.missing or not n.date:
            missing.append(code)
    ok = not missing
    return CheckResult(ok=ok, actual="缺失 " + ",".join(missing) if missing else "齐全",
                       expected="阶段必填节点齐全", reason="" if ok else f"缺少 {','.join(missing)}")


def _monotonic(ctx: DSLContext, p: dict) -> CheckResult:
    codes = p.get("nodes") or []
    vals = []
    for c in codes:
        n = ctx.nodes.get(c)
        if n and n.date:
            vals.append((c, n.date))
    bad = []
    for (c1, d1), (c2, d2) in zip(vals, vals[1:]):
        if d2 <= d1:
            bad.append(f"{c1}->{c2}")
    ok = not bad
    return CheckResult(ok=ok, actual=",".join(bad) if bad else "递增", expected="关键节点严格递增")


def _derive(ctx: DSLContext, p: dict) -> CheckResult:
    base, miss = ctx.resolve(p.get("base"))
    if miss or not base:
        return CheckResult(ok=True, skipped=True, reason="基节点缺失")
    off = p.get("offset") or {}
    d = add_duration(base, int(off.get("value", 1)), off.get("unit", "YEAR"))
    name = p.get("name", "D01")
    ctx.derived[name] = d
    ctx.nodes[name] = NodeVal(code=name, date=d, missing=False)
    return CheckResult(ok=True, actual=d.isoformat(), expected="派生成功", node_code=name)


OPS: dict[str, Callable] = {
    "age_at_least": _age_at_least,
    "before": _before,
    "between": _between,
    "within": _within,
    "at_least": _at_least,
    "duration_min": _duration_min,
    "seq_max_gap": _seq_max_gap,
    "seq_period_count": _seq_period_count,
    "seq_in_range": _seq_in_range,
    "consistent": _consistent,
    "valid_date": _valid_date,
    "required": _required,
    "monotonic": _monotonic,
    "derive": _derive,
}
