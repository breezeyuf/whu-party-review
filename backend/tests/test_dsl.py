from datetime import date

from ai.dsl import DSLContext, NodeVal, required_for_stage, run_checks


def _ctx(**nodes):
    nv = {}
    for code, d in nodes.items():
        if isinstance(d, dict):
            nv[code] = NodeVal(code=code, date=d.get("date"), end=d.get("end"), hours=d.get("hours"),
                               seq=d.get("seq") or [], has_conflict=d.get("has_conflict", False),
                               invalid_reason=d.get("invalid_reason"), missing=d.get("date") is None and not d.get("seq"))
        else:
            nv[code] = NodeVal(code=code, date=d, missing=d is None)
    return DSLContext(nv, date(2026, 10, 16), date(2026, 10, 1))


def test_r_t01_age():
    ctx = _ctx(T01=date(2003, 5, 12), T02=date(2023, 3, 15))
    r = run_checks(ctx, [{"op": "age_at_least", "birth": "T01", "at": "T02", "years": 18}])[0]
    assert r.ok
    ctx = _ctx(T01=date(2008, 5, 12), T02=date(2023, 3, 15))
    r = run_checks(ctx, [{"op": "age_at_least", "birth": "T01", "at": "T02", "years": 18}])[0]
    assert not r.ok


def test_r_t05_interval():
    ctx = _ctx(T04=date(2024, 9, 10), T08=date(2025, 8, 30))
    r = run_checks(ctx, [{"op": "at_least", "a": "T04", "b": "T08", "min": {"value": 1, "unit": "YEAR"}}])[0]
    assert not r.ok
    ctx = _ctx(T04=date(2024, 8, 30), T08=date(2025, 8, 30))
    r = run_checks(ctx, [{"op": "at_least", "a": "T04", "b": "T08", "min": {"value": 1, "unit": "YEAR"}}])[0]
    assert r.ok


def test_r_t16_derive():
    ctx = _ctx(T14=date(2024, 10, 1))
    r = run_checks(ctx, [{"op": "derive", "name": "D01", "base": "T14", "offset": {"value": 1, "unit": "YEAR"}}])[0]
    assert r.ok
    assert ctx.derived["D01"] == date(2025, 10, 1)


def test_r_t20_conflict():
    ctx = _ctx(T14={"date": date(2025, 6, 1), "has_conflict": True})
    r = run_checks(ctx, [{"op": "consistent", "nodes": "*"}])[0]
    assert not r.ok


def test_r_t22_required_and_monotonic():
    ctx = _ctx(T02=date(2023, 3, 15), T04=date(2024, 9, 10), T08=date(2025, 9, 10))
    r = required_for_stage(ctx, {"3": ["T04", "T08"]}, 3)
    assert r.ok
    r = run_checks(ctx, [{"op": "monotonic", "nodes": ["T02", "T04", "T08", "T14", "T20"]}])[0]
    assert r.ok
    ctx = _ctx(T02=date(2023, 3, 15), T04=date(2022, 1, 1))
    r = run_checks(ctx, [{"op": "monotonic", "nodes": ["T02", "T04"]}])[0]
    assert not r.ok


def test_missing_node_skipped():
    ctx = _ctx(T04=date(2024, 9, 10))
    r = run_checks(ctx, [{"op": "at_least", "a": "T04", "b": "T08", "min": {"value": 1, "unit": "YEAR"}}])[0]
    assert r.skipped
