"""Read-only four-category preview using detached rule snapshots."""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace

from ai.rule_snapshot import RuleSet, EvaluationContext
from ai.pipeline import _to_nodevals
from ai.checks.completeness import run_completeness
from ai.checks.timeline import run_timeline
from ai.checks.format import run_format
from ai.checks.content import run_content
from ai.report import issue_fp, summarize
from ai.ocr_status import run_ocr_review
from errors import unprocessable
from schemas.time_rules import validate_time_params
from models import RuleVersion, Batch, Material, MaterialVersion, ParseResult
from services.scope import ensure_submission_access
from services.timeline import node_map_for_archive
from utils import get_setting


def _evaluate(db, sub, mats, versions, parses, nodes, rules, context, similarity_cache):
    """Evaluate one detached ruleset against the same captured submission inputs."""
    context.validate(rules)
    _, d1, completeness_results = run_completeness(
        db, sub, mats, _to_nodevals(nodes), rule_set=rules, context=context, versions=versions)
    _, d2, time_results = run_timeline(db, sub, nodes, rule_set=rules, context=context)
    d3, format_results = run_format(db, mats, versions, parses, rules.types, rule_set=rules)
    d4, content_results = run_content(db, sub, mats, versions, parses, rules.types, False,
                                      rule_set=rules, similarity_cache=similarity_cache)
    ocr_drafts, ocr_results = run_ocr_review(mats, versions, parses)
    drafts = {issue_fp(d): d for d in d1 + d2 + d3 + d4 + ocr_drafts if d.source != 'AI_LLM'}
    items = {key: {'fingerprint': key, 'rule_code': d.rule_code, 'title': d.title,
                   'description': d.description, 'category': d.category, 'severity': d.severity}
             for key, d in drafts.items()}
    results = completeness_results + time_results + format_results + content_results + ocr_results
    return items, summarize(list(drafts.values()), len(mats), results)


def trial_rules(db, body, actor):
    ids = body.get("submission_ids")
    if not isinstance(ids, list) or not 1 <= len(ids) <= 20 or any(type(i) is not int or i <= 0 for i in ids):
        raise unprocessable("须指定 1 至 20 个有效提交包编号")
    version = db.query(RuleVersion).order_by(RuleVersion.id.desc()).first()
    if not version:
        raise unprocessable("尚无规则版本")
    baseline = RuleSet.from_version(version)
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
            if group == 'time_rules':
                row = rows[patch['code']]
                row['params'] = validate_time_params(row['params'], (node['code'] for node in snapshot['time_node_defs']))
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
        context = EvaluationContext.capture(baseline, get_setting(db,'calendar',{}), batch.end_date if batch else None)
        nodes = node_map_for_archive(db, sub.archive_id, node_defs=rules.rows('time_node_defs', active=False))
        # A changing candidate corpus must not change between baseline and trial.
        # Only aggregate similarity evidence is retained in this request-local cache.
        similarity_cache = {}
        current, current_summary = _evaluate(db, sub, mats, versions, parses, nodes,
                                               baseline, context, similarity_cache)
        trial, trial_summary = _evaluate(db, sub, mats, versions, parses, nodes, rules,
                                           replace(context, snapshot_sha256=rules.digest), similarity_cache)
        added, removed = sorted(trial.keys()-current.keys()), sorted(current.keys()-trial.keys())
        results.append({'submission_id':sid,'current':{'issue_keys':sorted(current),'summary':current_summary},
                        'trial':{'issue_keys':sorted(trial),'summary':trial_summary},
                        'added':added,'removed':removed,'added_items':[trial[k] for k in added],'removed_items':[current[k] for k in removed]})
    return {'results':results,'rule_version_no':version.version_no,
            'note':'使用相同的当前材料、时间节点与比对数据，分别运行当前已发布规则和临时规则。覆盖完整性、时间、形式和内容，不调用大模型。本次不保存规则、报告或问题。'}
