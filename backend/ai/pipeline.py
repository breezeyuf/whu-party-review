from __future__ import annotations

from datetime import date
from typing import Optional
from diagnostics import log_exception

from sqlalchemy.orm import Session

from ai.checks.completeness import run_completeness
from ai.checks.content import run_content
from ai.checks.format import run_format
from ai.checks.timeline import run_timeline
from ai.classify import classify_material
from ai.extract import extract_fields, extract_nodes
from ai.llm import llm_enabled
from ai.parser import parse_version_file
from ai.ocr_status import needs_review, review_warning, run_ocr_review
from ai.report import issue_fp, recommend, summarize
from ai.rule_snapshot import EvaluationContext, RuleSet
from ai.suggest import fill_suggestions
from models import (
    AiReport,
    AuditLog,
    Archive,
    ArchiveTimeNode,
    CheckRule,
    Issue,
    Job,
    Material,
    MaterialType,
    MaterialVersion,
    ParseResult,
    RuleVersion,
    Submission,
    TimeNodeDef,
    TimeNodeExtraction,
)
from services.timeline import merge_archive_nodes, node_map_for_archive
from utils import now, get_setting


def parse_version(db: Session, version_id: int, *, rule_set=None, context=None, use_llm=True) -> ParseResult:
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == version_id).first()
    if not ver:
        raise ValueError("version not found")
    material = db.query(Material).filter(Material.id == ver.material_id).first()
    # Use the same lock order as run_check: submission, then material version.
    db.query(Submission).filter(Submission.id == material.submission_id).with_for_update().one()
    db.refresh(material)
    db.refresh(ver)
    ver.parse_status = "RUNNING"
    db.flush()
    try:
        from ai.ocr import settings as ocr_settings
        token = ocr_settings.set(get_setting(db, 'ocr', {}))
        try:
            result = parse_version_file(ver.stored_path, ver.file_ext)
        finally:
            ocr_settings.reset(token)
        if result.get('ocr_failed'):
            # Keep diagnostic evidence, but do not replace current classification
            # or time-node extractions with an incomplete OCR attempt.
            partial=db.query(ParseResult).filter(ParseResult.version_id==ver.id).first()
            kept_previous = partial is not None
            if partial is None:
                partial=ParseResult(version_id=ver.id,created_at=now())
                db.add(partial)
                for field,default in [('parser','NONE'),('ocr_engine',None),('preview_pdf_path',None),('full_text',''),
                                      ('char_count',0),('pages',[]),('visual_marks',{}),('format_features',{}),('warnings',[])]:
                    setattr(partial,field,result.get(field,default))
                partial.extracted_fields=extract_fields(result.get('full_text') or '')
                ver.page_count=result.get('page_count') or len(result.get('pages') or [])
            else:
                warning='本次重新解析未完成，当前显示此前保留的解析及人工校正；请重试解析'
                warnings = list(partial.warnings or [])
                if warning not in warnings:
                    warnings.append(warning)
                partial.warnings = warnings
            partial.updated_at=now()
            db.flush()
            from ai.ocr import OCRProcessingError
            raise OCRProcessingError('本地 OCR 识别未完成，' + ('此前解析及人工校正已保留' if kept_previous else '部分结果已保留') + '；请检查引擎后重新解析')
        pending = [page for page in result.get('pages', []) if needs_review(page)]
        previous = db.query(ParseResult).filter(ParseResult.version_id == ver.id).first()
        has_manual_nodes = db.query(TimeNodeExtraction.id).filter(
            TimeNodeExtraction.material_version_id == ver.id,
            TimeNodeExtraction.is_current.is_(True), TimeNodeExtraction.method == 'MANUAL').first()
        if pending and previous is not None and ((previous.full_text or '').strip()
                or previous.corrected_text is not None or previous.corrected_fields is not None or has_manual_nodes):
            # Empty OCR is reviewable, not an engine failure. Never replace usable
            # evidence or retire its time-node sources with this incomplete retry.
            page_map = {page['page_no']: dict(page) for page in previous.pages or []}
            for page in pending:
                page_map.setdefault(page['page_no'], dict(page))['ocr_status'] = 'NEEDS_REVIEW'
            previous.pages = list(page_map.values())
            warnings = [warning for warning in previous.warnings or [] if not (
                isinstance(warning, dict) and warning.get('code') == 'OCR-REVIEW'
                and warning.get('page_no') in {page['page_no'] for page in pending})]
            previous.warnings = warnings + [review_warning(page['page_no'], retained=True) for page in pending]
            previous.updated_at = now()
            ver.parse_status, ver.parse_error, ver.parsed_at = 'DONE', None, now()
            db.flush()
            return previous
        if use_llm:
            from ai.ocr_review import review_result
            review_result(db, result)
        is_current = material.current_version_id == ver.id and material.status == "ACTIVE"
        types = rule_set.rows("material_types") if rule_set else db.query(MaterialType).filter(MaterialType.is_active.is_(True)).all()
        declared = (rule_set.types.get(material.declared_type_id) if rule_set else
                    db.query(MaterialType).filter(MaterialType.id == material.declared_type_id).first()) if material.declared_type_id else None
        threshold = context.classify_confidence_threshold if context else float(get_setting(db, "ai", {}).get("classify_confidence_threshold") or 0.7)
        cls = classify_material(result.get("full_text") or "", declared, types,
                                threshold)
        enrich = use_llm and llm_enabled(db)
        if enrich and material.type_status != 'CONFIRMED':
            from ai.enrichment import classify_fallback
            cls, error = classify_fallback(db, result.get('full_text') or '', cls, types, threshold,
                archive=material.archive, rule_set=rule_set)
            if error: result.setdefault('warnings', []).append('模型分类未采用：'+error)
        if is_current and material.type_status != "CONFIRMED":
            material.type_id = cls["type_id"]
            material.type_source = cls["type_source"]
            material.type_confidence = cls["type_confidence"]
            material.type_status = cls["type_status"]
        type_row = (rule_set.types.get(material.type_id) if rule_set else
                    db.query(MaterialType).filter(MaterialType.id == material.type_id).first()) if material.type_id else None
        fields = extract_fields(result.get("full_text") or "")
        result["extracted_fields"] = fields
        nodes = rule_set.rows("time_node_defs") if rule_set else db.query(TimeNodeDef).filter(TimeNodeDef.is_active.is_(True)).all()
        extractions = extract_nodes(result.get("full_text") or "", result.get("pages") or [], type_row, nodes)
        if enrich:
            from ai.enrichment import extract_fallback
            extractions, error = extract_fallback(db, result.get('full_text') or '', result.get('pages') or [], extractions, nodes,
                archive=material.archive, rule_set=rule_set)
            if error: result.setdefault('warnings', []).append('模型补抽未采用：'+error)
        # A retry of the same file must keep manually checked node values. New
        # file versions still replace all sources from the old version.
        manual = db.query(TimeNodeExtraction).filter(
            TimeNodeExtraction.material_version_id == ver.id,
            TimeNodeExtraction.is_current.is_(True),
            TimeNodeExtraction.method == 'MANUAL',
        ).all()
        manual_keys = {(row.node_code, row.seq_index or 0) for row in manual}
        deleted_keys = set()
        for entry in db.query(AuditLog).filter(AuditLog.action == 'PARSE_CORRECT',
                AuditLog.object_type == 'material', AuditLog.object_id == str(material.id)).order_by(AuditLog.id).all():
            detail = entry.detail if isinstance(entry.detail, dict) else {}
            if detail.get('version_id') != ver.id:
                continue
            for change in detail.get('extractions') or []:
                if not isinstance(change, dict):
                    continue
                before = change.get('before') or {}
                if change.get('action') == 'DELETE' and before.get('node_code'):
                    deleted_keys.add((before['node_code'], before.get('seq_index') or 0))
                after = change.get('after') or {}
                if change.get('action') in ('CREATE', 'UPDATE') and after.get('node_code'):
                    deleted_keys.discard((after['node_code'], after.get('seq_index') or 0))
        db.query(TimeNodeExtraction).filter(
            TimeNodeExtraction.material_id == material.id,
            TimeNodeExtraction.is_current.is_(True),
            True if is_current else TimeNodeExtraction.material_version_id == ver.id,
        ).update({"is_current": False})
        for row in manual:
            row.is_current = is_current
        for ex in extractions:
            key = (ex['node_code'], ex.get('seq_index') or 0)
            if key in manual_keys or key in deleted_keys:
                continue
            db.add(TimeNodeExtraction(
                archive_id=material.archive_id,
                node_code=ex["node_code"],
                material_id=material.id,
                material_version_id=ver.id,
                seq_index=ex.get("seq_index") or 0,
                value_date=ex.get("value_date"),
                value_end_date=ex.get("value_end_date"),
                hours=ex.get("hours"),
                raw_text=ex.get("raw_text"),
                invalid_reason=ex.get("invalid_reason"),
                page_no=ex.get("page_no"),
                bbox=ex.get("bbox"),
                confidence=ex.get("confidence"),
                method=ex.get("method") or "RULE",
                is_current=is_current,
                created_at=now(),
            ))
        existing = db.query(ParseResult).filter(ParseResult.version_id == ver.id).first()
        payload = dict(
            parser=result.get("parser") or "NONE",
            ocr_engine=result.get("ocr_engine"),
            preview_pdf_path=result.get("preview_pdf_path"),
            full_text=result.get("full_text") or "",
            char_count=result.get("char_count") or 0,
            pages=result.get("pages") or [],
            visual_marks=result.get("visual_marks") or {},
            extracted_fields=fields,
            format_features=result.get("format_features") or {},
            warnings=result.get("warnings") or [],
            created_at=now(),
            updated_at=now(),
        )
        if existing:
            for k, v in payload.items():
                if k != "created_at":
                    setattr(existing, k, v)
            pr = existing
        else:
            pr = ParseResult(version_id=ver.id, **payload)
            db.add(pr)
        ver.parse_status = "DONE"
        ver.parse_error = None
        ver.parsed_at = now()
        ver.page_count = result.get("page_count") or len(result.get("pages") or [])
        db.flush()
        if is_current:
            merge_archive_nodes(db, material.archive_id, node_defs=nodes)
        return pr
    except Exception as e:
        log_exception("material.parse_failed", e, version_id=version_id)
        ver.parse_status = "FAILED"
        from ai.ocr import OCRProcessingError
        ver.parse_error = str(e) if isinstance(e, OCRProcessingError) else "材料解析失败，请联系管理员并提供材料版本编号"
        db.flush()
        raise


def run_check(db: Session, submission_id: int, trigger_type: str = "SELF_CHECK", user_id: Optional[int] = None, job_id: Optional[int] = None, use_llm: bool = True, *,
              rule_version_id: int | None = None, evaluation_context: EvaluationContext | None = None) -> AiReport:
    # 行锁串行化同一提交包的并发检查，避免 report_no 冲突与问题表交错写
    sub = db.query(Submission).filter(Submission.id == submission_id).with_for_update().first()
    if not sub:
        raise ValueError("submission not found")
    rv = (db.query(RuleVersion).filter(RuleVersion.id == rule_version_id).first() if rule_version_id is not None else
          db.query(RuleVersion).order_by(RuleVersion.version_no.desc()).first())
    if not rv:
        raise ValueError("no rule version")
    rules = RuleSet.from_version(rv)
    batch = sub.archive.batch if sub.archive else None
    context = evaluation_context or EvaluationContext.capture(
        rules, get_setting(db, "calendar", {}), batch.end_date if batch else None,
        get_setting(db, "ai", {}).get("classify_confidence_threshold") or 0.7,
    )
    context.validate(rules)
    last_no = (
        db.query(AiReport.report_no).filter(AiReport.submission_id == submission_id)
        .order_by(AiReport.report_no.desc()).first()
    )
    report_no = (last_no[0] + 1) if last_no else 1
    enabled = bool(use_llm) and llm_enabled(db)
    mode = "RULE_LLM" if enabled else "RULE_ONLY"
    degrade = None if enabled else ("本次未启用大模型" if not use_llm else "未配置大模型")
    # 保留尝试使用的模型名称；mode 表示最终报告采用的结果来源。
    model_name = (get_setting(db, "ai", {}) or {}).get("model") if enabled else None
    report = AiReport(
        submission_id=submission_id,
        report_no=report_no,
        trigger_type=trigger_type,
        triggered_by=user_id,
        job_id=job_id,
        rule_version_id=rv.id,
        mode=mode,
        llm_model=model_name,
        degrade_reason=degrade,
        status="RUNNING",
        handover_status="REQUIRED",
        handover_reasons=[],
        started_at=now(),
        timeline_snapshot={"evaluation_context": context.to_dict()},
    )
    prev = None
    try:
        db.add(report)
        db.flush()
        if trigger_type == "RECHECK":
            prev = (
                db.query(AiReport)
                .filter(AiReport.submission_id == submission_id, AiReport.id != report.id, AiReport.status == "DONE")
                .order_by(AiReport.report_no.desc())
                .first()
            )
            report.recheck_of_report_id = prev.id if prev else None
        materials = db.query(Material).filter(Material.submission_id == submission_id, Material.status == "ACTIVE").all()
        versions = {}
        parses = {}
        types = rules.types
        used_versions = []
        for m in materials:
            if not m.current_version_id:
                continue
            ver = db.query(MaterialVersion).filter(MaterialVersion.id == m.current_version_id).first()
            if not ver:
                continue
            versions[m.id] = ver
            if ver.parse_status != "DONE":
                parse_version(db, ver.id, rule_set=rules, context=context, use_llm=enabled)
                db.refresh(ver)
            pr = db.query(ParseResult).filter(ParseResult.version_id == ver.id).first()
            if pr:
                parses[ver.id] = pr
            used_versions.append({"material_id": m.id, "version_id": ver.id, "version_no": ver.version_no})
        node_map = node_map_for_archive(db, sub.archive_id, node_defs=rules.rows("time_node_defs", active=False))
        completeness, d1, r1 = run_completeness(db, sub, materials, _to_nodevals(node_map), rule_set=rules, context=context, versions=versions)
        snapshot, d2, r2 = run_timeline(db, sub, node_map, rule_set=rules, context=context)
        snapshot["evaluation_context"] = context.to_dict()
        snapshot["node_inputs"] = node_map
        d3, r3 = run_format(db, materials, versions, parses, types, rule_set=rules)
        d4, r4 = run_content(db, sub, materials, versions, parses, types, enabled, rule_set=rules, timeline=node_map)
        ocr_drafts, ocr_results = run_ocr_review(materials, versions, parses)
        if enabled:
            errors = list(dict.fromkeys(r["error"] for r in r4 if r.get("engine") == "LLM" and r.get("error")))
            if errors:
                mode = "RULE_ONLY"
                degrade = "大模型检查失败，已降级为仅规则模式：" + "；".join(errors)
            elif not any(r.get("engine") == "LLM" and r.get("result") in ("PASS", "FAIL") for r in r4):
                mode = "RULE_ONLY"
                degrade = "无适用材料或语义规则，未执行大模型检查"
                report.llm_model = None
        report.mode = mode
        report.degrade_reason = degrade
        drafts = d1 + d2 + d3 + d4 + ocr_drafts
        fill_suggestions(db, drafts, rule_set=rules)
        if enabled and mode == 'RULE_LLM':
            from ai.enrichment import polish_suggestions
            suggestion_error = polish_suggestions(db, drafts, archive=sub.archive, rule_set=rules)
            if suggestion_error:
                r4.append({'rule_code':'SUGGEST','engine':'LLM','result':'SKIPPED',
                    'reason':'建议润色不可用，已保留模板建议：'+suggestion_error})
        rule_results = r1 + r2 + r3 + r4 + ocr_results
        summary = summarize(drafts, len(materials), rule_results)
        rec = recommend(summary, drafts)
        classification = {
            "materials": [
                {
                    "material_id": m.id,
                    "title": m.title,
                    "type_code": types[m.type_id].code if m.type_id in types else None,
                    "confidence": m.type_confidence,
                    "type_source": m.type_source,
                    "status": m.type_status,
                }
                for m in materials
            ],
            "counts": _type_counts(materials, types),
        }
        reasons = _handover_reasons(sub, materials, drafts, mode, node_map)
        hs = "REQUIRED" if reasons else "NOT_REQUIRED"
        report.material_versions = used_versions
        if prev:
            before = {v['material_id']: v for v in (prev.material_versions or [])}
            after = {v['material_id']: v for v in used_versions}
            report.changed_materials = [
                {'material_id': mid, 'old_version_id': before.get(mid, {}).get('version_id'),
                 'new_version_id': after.get(mid, {}).get('version_id'),
                 'change': 'ADDED' if mid not in before else 'REMOVED' if mid not in after else 'UPDATED'}
                for mid in sorted(before.keys() | after.keys())
                if before.get(mid, {}).get('version_id') != after.get(mid, {}).get('version_id')
            ]
        report.classification = classification
        report.completeness = completeness
        report.timeline_snapshot = snapshot
        report.rule_results = rule_results
        report.summary = summary
        report.recommendation = rec
        report.handover_status = hs
        report.handover_reasons = reasons
        report.effective_recommendation = None if hs == "REQUIRED" else rec
        report.status = "DONE"
        report.finished_at = now()
        report.duration_ms = int((report.finished_at - report.started_at).total_seconds() * 1000)
        # 问题重写放入保存点：中途失败时回滚"停用旧问题"，避免问题清单被清空
        with db.begin_nested():
            db.query(Issue).filter(Issue.submission_id == submission_id, Issue.source != "MANUAL", Issue.is_active.is_(True)).update(
                {"is_active": False}
            )
            old_by_fp = {}
            if prev:
                olds = db.query(Issue).filter(Issue.report_id == prev.id).all()
                old_by_fp = {i.fingerprint: i for i in olds if i.fingerprint}
            new_fps = set()
            for d in drafts:
                fp = issue_fp(d)
                new_fps.add(fp)
                old = old_by_fp.get(fp)
                issue = Issue(
                    submission_id=submission_id,
                    report_id=report.id,
                    material_id=d.material_id,
                    material_version_id=d.material_version_id,
                    source=d.source,
                    category=d.category,
                    severity=d.severity,
                    rule_code=d.rule_code,
                    rule_basis=d.rule_basis,
                    title=d.title,
                    description=d.description,
                    location=d.location or {},
                    actual_value=d.actual_value,
                    expected_value=d.expected_value,
                    suggestion=d.suggestion,
                    suggestion_example=d.suggestion_example,
                    needs_human_judgement=d.needs_human_judgement,
                    confidence=d.confidence,
                    fingerprint=fp,
                    is_active=True,
                    review_status=old.review_status if old else "PENDING",
                    resolution="UNRESOLVED" if old else "OPEN",
                    prev_issue_id=old.id if old else None,
                    is_new_in_recheck=bool(prev and not old),
                    created_at=now(),
                    updated_at=now(),
                )
                db.add(issue)
            if prev:
                resolved = unresolved = newc = not_rechecked = 0
                for fp, old in old_by_fp.items():
                    if fp in new_fps:
                        unresolved += 1
                    elif (old.source == "AI_LLM" and mode == "RULE_ONLY"
                          and old.review_status != "REJECTED" and old.resolution not in ("RESOLVED", "WAIVED")):
                        # A skipped/failed model check is not evidence that an old issue was fixed.
                        old.resolution = "OPEN"
                        old.resolved_by_report_id = None
                        unresolved += 1
                        not_rechecked += 1
                    else:
                        old.resolution = "RESOLVED"
                        old.resolved_by_report_id = report.id
                        resolved += 1
                newc = sum(1 for d in drafts if issue_fp(d) not in old_by_fp)
                report.recheck_summary = {"resolved": resolved, "unresolved": unresolved, "new": newc}
                if not_rechecked:
                    report.recheck_summary["not_rechecked"] = not_rechecked
            db.flush()
            # fill issue ids into rule_results loosely
            sub.latest_report_id = report.id
            sub.ai_status = "DONE"
        db.flush()
        return report
    except Exception as e:
        log_exception("review.check_failed", e, submission_id=submission_id, report_id=report.id)
        report.status = "FAILED"
        report.error = "审核执行失败，请联系管理员并提供报告编号"
        report.finished_at = now()
        sub.ai_status = "FAILED"
        db.flush()
        raise


def _to_nodevals(node_map: dict):
    from ai.dsl import NodeVal
    from utils import as_date
    out = {}
    for code, n in node_map.items():
        d = as_date(n.get("date") or n.get("value_date"))
        out[code] = type("N", (), {
            "date": d,
            "end": as_date(n.get("end") or n.get("end_date")),
            "hours": n.get("hours"),
            "seq": [as_date(x) for x in (n.get("seq") or []) if as_date(x)],
            "has_conflict": n.get("has_conflict"),
            "missing": not bool(d or n.get("seq")),
        })()
    return out


def _type_counts(materials, types):
    from collections import Counter
    c = Counter()
    names = {}
    for m in materials:
        if m.type_id in types:
            c[types[m.type_id].code] += 1
            names[types[m.type_id].code] = types[m.type_id].name
    return [{"type_code": k, "type_name": names[k], "count": v} for k, v in c.items()]


def _handover_reasons(sub, materials, drafts, mode, node_map) -> list[str]:
    reasons = []
    if mode == "RULE_ONLY":
        reasons.append("LOW_CONFIDENCE")
    if any((m.type_status == "NEEDS_CONFIRM") or (m.type_confidence is not None and m.type_confidence < 0.7) for m in materials):
        reasons.append("LOW_CONFIDENCE")
    if any((d.confidence if d.confidence is not None else 1) < 0.7 for d in drafts):
        reasons.append("LOW_CONFIDENCE")
    if any(n.get("has_conflict") for n in node_map.values()):
        reasons.append("MATERIAL_CONFLICT")
    if any(d.needs_human_judgement for d in drafts):
        reasons.append("NEEDS_JUDGEMENT")
    rec = recommend(summarize(drafts, len(materials), []), drafts)
    if rec == "NEEDS_REVIEW":
        reasons.append("NEEDS_JUDGEMENT")
    if sub.stage_code in (1, 2, 3, 4, 5):
        reasons.append("KEY_STAGE")
    # unique preserve order
    seen = []
    for r in reasons:
        if r not in seen:
            seen.append(r)
    return seen
