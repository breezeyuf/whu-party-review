"""Read-only four-category preview using detached rule snapshots."""
from copy import deepcopy
from types import SimpleNamespace

from ai.rule_snapshot import RuleSet, EvaluationContext
from ai.pipeline import _to_nodevals
from ai.checks.completeness import run_completeness
from ai.checks.timeline import run_timeline
from ai.checks.format import run_format
from ai.checks.content import run_content
from errors import unprocessable
from models import RuleVersion, Batch, Material, MaterialVersion, ParseResult, Issue
from services.scope import ensure_submission_access
from services.timeline import node_map_for_archive
from security import fingerprint
from utils import get_setting


def trial_rules(db, body, actor):
    ids = body.get("submission_ids")
    if not isinstance(ids, list) or not 1 <= len(ids) <= 20 or any(type(i) is not int or i <= 0 for i in ids):
        raise unprocessable("须指定 1 至 20 个有效提交包编号")
    version = db.query(RuleVersion).order_by(RuleVersion.id.desc()).first()
    if not version:
        raise unprocessable("尚无规则版本")
    snapshot = deepcopy(version.snapshot)
    overrides = body.get("overrides") or {}
    if not isinstance(overrides, dict) or set(overrides) - {"time_rules", "check_rules"}:
        raise unprocessable("临时参数格式无效")
    for group, patches in overrides.items():
        if not isinstance(patches, list) or len(patches) > 200:
            raise unprocessable("临时规则须为数组，最多 200 条")
        rows = {row['code']: row for row in snapshot[group]}
        seen = set()
        for patch in patches:
            if not isinstance(patch, dict) or not isinstance(patch.get('code'), str) or patch['code'] not in rows or patch['code'] in seen:
                raise unprocessable("规则不存在或编码重复")
            seen.add(patch['code'])
            if set(patch) - {'code', 'params', 'severity', 'is_active'}:
                raise unprocessable("不支持的临时规则字段")
            if 'params' in patch and not isinstance(patch['params'], dict):
                raise unprocessable("params 须为对象")
            if 'severity' in patch and patch['severity'] not in ('BLOCK','WARN','INFO','CALC'):
                raise unprocessable("规则级别无效")
            if 'is_active' in patch and type(patch['is_active']) is not bool:
                raise unprocessable("is_active 须为布尔值")
            rows[patch['code']].update(patch)
    rules = RuleSet.from_version(SimpleNamespace(id=version.id, version_no=version.version_no, snapshot=snapshot))
    results = []
    for sid in dict.fromkeys(ids):
        sub = ensure_submission_access(db, actor, sid)
        mats = db.query(Material).filter(Material.submission_id == sid, Material.status == 'ACTIVE').all()
        versions, parses = {}, {}
        for material in mats:
            ver = db.query(MaterialVersion).filter(MaterialVersion.id == material.current_version_id).first()
            parsed = db.query(ParseResult).filter(ParseResult.version_id == ver.id).first() if ver else None
            if not ver or ver.parse_status != 'DONE' or not parsed:
                raise unprocessable(f"提交包 {sid} 的材料需完成解析后才能试运行")
            versions[material.id], parses[ver.id] = ver, parsed
        batch = db.query(Batch).filter(Batch.id == sub.batch_id).first() if sub.batch_id else None
        context = EvaluationContext.capture(rules, get_setting(db,'calendar',{}), batch.end_date if batch else None)
        nodes = node_map_for_archive(db, sub.archive_id, node_defs=rules.rows('time_node_defs', active=False))
        _, d1, _ = run_completeness(db, sub, mats, _to_nodevals(nodes), rule_set=rules, context=context, versions=versions)
        _, d2, _ = run_timeline(db, sub, nodes, rule_set=rules, context=context)
        d3, _ = run_format(db, mats, versions, parses, rules.types, rule_set=rules)
        d4, content_results = run_content(db, sub, mats, versions, parses, rules.types, False, rule_set=rules)
        skipped = {r['rule_code'] for r in content_results if r.get('result') == 'SKIPPED'}
        old = db.query(Issue).filter(Issue.report_id == sub.latest_report_id, Issue.source != 'MANUAL').all() if sub.latest_report_id else []
        current = {i.fingerprint: {'fingerprint':i.fingerprint,'rule_code':i.rule_code,'title':i.title,'description':i.description}
                   for i in old if i.fingerprint and i.source != 'AI_LLM' and i.rule_code not in skipped}
        trial = {}
        for draft in d1+d2+d3+d4:
            key = fingerprint(*(draft.fingerprint_parts or (draft.rule_code,draft.title)))
            trial[key] = {'fingerprint':key,'rule_code':draft.rule_code,'title':draft.title,'description':draft.description}
        added, removed = sorted(trial.keys()-current.keys()), sorted(current.keys()-trial.keys())
        results.append({'submission_id':sid,'current':{'issue_keys':list(current)},'trial':{'issue_keys':list(trial),'summary':{'total':len(trial)}},
                        'added':added,'removed':removed,'added_items':[trial[k] for k in added],'removed_items':[current[k] for k in removed]})
    return {'results':results,'note':'覆盖完整性、时间、形式和内容的规则检查；不调用大模型，语义检查不计入消失问题。本次不保存规则、报告或问题。'}
