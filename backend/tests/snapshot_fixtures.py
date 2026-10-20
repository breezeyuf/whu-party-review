from types import SimpleNamespace as NS

from ai.rule_snapshot import RULE_GROUPS


def version(snapshot=None, number=1):
    return NS(id=number, version_no=number,
              snapshot=snapshot if snapshot is not None else {key: [] for key in RULE_GROUPS})


def material_type(**changes):
    row = dict(id=1, code="THOUGHT_REPORT", name="思想汇报", is_active=True, sort_order=0,
                title_keywords=["思想汇报"], exclude_keywords=[], element_template=[],
               format_requirements={}, date_node_map={})
    row.update(changes)
    return row


def check_rule(code, category="CONTENT", **changes):
    row = dict(id=1, code=code, category=category, is_active=True, sort_order=0,
               engine="RULE", applies_to=[], params={}, severity="WARN", name=code,
               basis="基线依据", message_template=None, needs_human_judgement=False)
    row.update(changes)
    return row


def checklist(count=1, **changes):
    row = dict(id=1, stage_code=1, material_type_id=1, quantity_mode="FIXED", fixed_count=count,
               period_months=3, period_start_node="T01", period_end_node=None,
               is_required=True, requirement_text="提交思想汇报", is_active=True, sort_order=0)
    row.update(changes)
    return row


def time_rule(checks, **changes):
    row = dict(id=1, code="R-T21", name="日期检查", rule_type="DSL", params={"checks": checks},
               applies_stages=[], severity="WARN", basis="基线", message_template=None,
               is_active=True, sort_order=0)
    row.update(changes)
    return row
