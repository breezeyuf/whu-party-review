from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from errors import forbidden, not_found, too_large, unprocessable
from models import (
    CheckRule,
    ChecklistItem,
    MaterialType,
    PoliticalTerm,
    PromptTemplate,
    RuleVersion,
    SensitivePhrase,
    SuggestionTemplate,
    TimeNodeDef,
    TimeRule,
    AiReport,
)
from schemas.common import ok, page_params
from services.exporter import xlsx_response
from services.rules import (
    create_and_snapshot,
    delete_and_snapshot,
    export_kind,
    import_kind,
    list_checklists,
    orm_dict,
    update_and_snapshot,
    version_diff,
    _checklist_dict,
)
from utils import now
import re

router = APIRouter(prefix="/rules", tags=["rules"])


def _writer(actor: Actor):
    if actor.role != "ORG_ADMIN":
        raise forbidden("仅组织部可维护规则库")


def _page(q, page, page_size):
    page, page_size = page_params(page, page_size)
    total = q.count()
    rows = q.offset((page - 1) * page_size).limit(page_size).all()
    return page, page_size, total, rows


@router.get("/checklists")
def get_checklists(stage_code: int | None = None, q: str | None = None, is_active: bool | None = None,
                   db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    return ok(list_checklists(db, stage_code, q, is_active))


@router.post("/checklists")
def post_checklist(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = ChecklistItem(
        stage_code=body["stage_code"], material_type_id=body["material_type_id"],
        quantity_mode=body.get("quantity_mode") or "FIXED", fixed_count=body.get("fixed_count") or 1,
        period_months=body.get("period_months"), period_start_node=body.get("period_start_node"),
        period_end_node=body.get("period_end_node"), is_required=body.get("is_required", True),
        requirement_text=body.get("requirement_text"), sort_order=body.get("sort_order") or 0,
        is_active=body.get("is_active", True), created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "checklists", obj, "新增清单条目")
    d = _checklist_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/checklists/{oid}")
def put_checklist(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(ChecklistItem).filter(ChecklistItem.id == oid).first()
    if not obj:
        raise not_found()
    obj, ver = update_and_snapshot(db, actor, "checklists", obj, body, "更新清单")
    d = _checklist_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/checklists/{oid}")
def del_checklist(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(ChecklistItem).filter(ChecklistItem.id == oid).first()
    if not obj:
        raise not_found()
    ver = delete_and_snapshot(db, actor, "checklists", obj, "删除清单")
    return ok({"rule_version_no": ver})


def _crud(list_path, model, kind, code_field="code"):
    pass


@router.get("/material-types")
def list_mt(q: str | None = None, is_active: bool | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    rows = db.query(MaterialType).order_by(MaterialType.sort_order).all()
    if q:
        rows = [r for r in rows if q in (r.name or "") or q in (r.code or "")]
    if is_active is not None:
        rows = [r for r in rows if r.is_active == is_active]
    return ok([orm_dict(r) for r in rows])


@router.post("/material-types")
def post_mt(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    code = body.get("code") or ""
    if not re.match(r"^[A-Z][A-Z0-9_]{2,40}$", code):
        raise unprocessable("code 格式不正确")
    obj = MaterialType(
        code=code, name=body["name"], stage_codes=body.get("stage_codes") or [],
        title_keywords=body.get("title_keywords") or [], exclude_keywords=body.get("exclude_keywords") or [],
        element_template=body.get("element_template") or [], format_requirements=body.get("format_requirements") or {},
        date_node_map=body.get("date_node_map") or {}, description=body.get("description"),
        is_active=body.get("is_active", True), created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "material-types", obj, f"新增材料类型 {code}")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/material-types/{oid}")
def put_mt(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(MaterialType).filter(MaterialType.id == oid).first()
    if not obj:
        raise not_found()
    body = dict(body)
    body.pop("code", None)
    obj, ver = update_and_snapshot(db, actor, "material-types", obj, body, "更新材料类型")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/material-types/{oid}")
def del_mt(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(MaterialType).filter(MaterialType.id == oid).first()
    if not obj:
        raise not_found()
    if db.query(ChecklistItem).filter(ChecklistItem.material_type_id == oid).first():
        from errors import conflict
        raise conflict("已被清单引用，请改为停用")
    ver = delete_and_snapshot(db, actor, "material-types", obj, "删除材料类型")
    return ok({"rule_version_no": ver})


@router.get("/time-nodes")
def list_tn(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    return ok([orm_dict(r) for r in db.query(TimeNodeDef).order_by(TimeNodeDef.sort_order).all()])


@router.post("/time-nodes")
def post_tn(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = TimeNodeDef(
        code=body["code"], name=body["name"], value_kind=body["value_kind"], has_hours=body.get("has_hours") or False,
        stage_code=body.get("stage_code"), required_from_stage=body.get("required_from_stage"),
        source_material_codes=body.get("source_material_codes") or [], extract_keywords=body.get("extract_keywords") or [],
        derive_expr=body.get("derive_expr"), sort_order=body.get("sort_order") or 0, is_active=body.get("is_active", True),
        created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "time-nodes", obj, f"新增节点 {obj.code}")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/time-nodes/{oid}")
def put_tn(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(TimeNodeDef).filter(TimeNodeDef.id == oid).first()
    if not obj:
        raise not_found()
    body = dict(body)
    body.pop("code", None)
    if body.get("value_kind", obj.value_kind) != "DERIVED":
        body["derive_expr"] = None
    obj, ver = update_and_snapshot(db, actor, "time-nodes", obj, body, "更新节点")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.get("/time-rules")
def list_tr(q: str | None = None, is_active: bool | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    rows = db.query(TimeRule).order_by(TimeRule.sort_order).all()
    if q:
        rows = [r for r in rows if q in r.code or q in r.name]
    if is_active is not None:
        rows = [r for r in rows if r.is_active == is_active]
    return ok([orm_dict(r) for r in rows])


@router.post("/time-rules")
def post_tr(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = TimeRule(
        code=body["code"], name=body["name"], rule_type=body["rule_type"], params=body.get("params") or {"checks": []},
        applies_stages=body.get("applies_stages") or [], severity=body["severity"], basis=body.get("basis"),
        message_template=body["message_template"], suggestion_template_id=body.get("suggestion_template_id"),
        is_active=body.get("is_active", True), sort_order=body.get("sort_order") or 0, created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "time-rules", obj, f"新增时间规则 {obj.code}")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/time-rules/{oid}")
def put_tr(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(TimeRule).filter(TimeRule.id == oid).first()
    if not obj:
        raise not_found()
    obj, ver = update_and_snapshot(db, actor, "time-rules", obj, body, "更新时间规则")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/time-rules/{oid}")
def del_tr(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(TimeRule).filter(TimeRule.id == oid).first()
    if not obj:
        raise not_found()
    ver = delete_and_snapshot(db, actor, "time-rules", obj, "删除时间规则")
    return ok({"rule_version_no": ver})


@router.get("/check-rules")
def list_cr(category: str | None = None, q: str | None = None, is_active: bool | None = None,
            db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    rows = db.query(CheckRule).order_by(CheckRule.sort_order).all()
    if category:
        rows = [r for r in rows if r.category == category]
    if q:
        rows = [r for r in rows if q in r.code or q in r.name]
    if is_active is not None:
        rows = [r for r in rows if r.is_active == is_active]
    return ok([orm_dict(r) for r in rows])


@router.post("/check-rules")
def post_cr(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = CheckRule(
        code=body["code"], category=body["category"], name=body["name"], engine=body["engine"],
        applies_to=body.get("applies_to") or [], params=body.get("params") or {}, severity=body["severity"],
        needs_human_judgement=body.get("needs_human_judgement") or False, basis=body.get("basis"),
        message_template=body["message_template"], suggestion_template_id=body.get("suggestion_template_id"),
        is_optional=body.get("is_optional") or False, is_active=body.get("is_active", True),
        sort_order=body.get("sort_order") or 0, created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "check-rules", obj, f"新增规则 {obj.code}")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/check-rules/{oid}")
def put_cr(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(CheckRule).filter(CheckRule.id == oid).first()
    if not obj:
        raise not_found()
    obj, ver = update_and_snapshot(db, actor, "check-rules", obj, body, "更新校验规则")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/check-rules/{oid}")
def del_cr(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(CheckRule).filter(CheckRule.id == oid).first()
    if not obj:
        raise not_found()
    ver = delete_and_snapshot(db, actor, "check-rules", obj, "删除校验规则")
    return ok({"rule_version_no": ver})


@router.get("/terms")
def list_terms(q: str | None = None, is_active: bool | None = None, page: int = 1, page_size: int = 20,
               db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    query = db.query(PoliticalTerm)
    if q:
        query = query.filter(PoliticalTerm.standard_text.ilike(f"%{q}%"))
    if is_active is not None:
        query = query.filter(PoliticalTerm.is_active.is_(is_active))
    page, page_size, total, rows = _page(query.order_by(PoliticalTerm.id), page, page_size)
    return ok({"items": [orm_dict(r) for r in rows], "total": total, "page": page, "page_size": page_size})


@router.post("/terms")
def post_term(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = PoliticalTerm(
        term_type=body.get("term_type") or "VARIANT", standard_text=body["standard_text"],
        wrong_variants=body.get("wrong_variants") or [], sequence_items=body.get("sequence_items") or [],
        category=body.get("category"), severity=body.get("severity") or "WARN", note=body.get("note"),
        is_active=body.get("is_active", True), created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "terms", obj, "新增术语")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/terms/{oid}")
def put_term(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(PoliticalTerm).filter(PoliticalTerm.id == oid).first()
    if not obj:
        raise not_found()
    obj, ver = update_and_snapshot(db, actor, "terms", obj, body, "更新术语")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/terms/{oid}")
def del_term(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(PoliticalTerm).filter(PoliticalTerm.id == oid).first()
    if not obj:
        raise not_found()
    ver = delete_and_snapshot(db, actor, "terms", obj, "删除术语")
    return ok({"rule_version_no": ver})


@router.get("/sensitive-phrases")
def list_sp(q: str | None = None, is_active: bool | None = None, page: int = 1, page_size: int = 20,
            db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    query = db.query(SensitivePhrase)
    if q:
        query = query.filter(SensitivePhrase.phrase.ilike(f"%{q}%"))
    if is_active is not None:
        query = query.filter(SensitivePhrase.is_active.is_(is_active))
    page, page_size, total, rows = _page(query.order_by(SensitivePhrase.id), page, page_size)
    return ok({"items": [orm_dict(r) for r in rows], "total": total, "page": page, "page_size": page_size})


@router.post("/sensitive-phrases")
def post_sp(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    if body.get("match_type") == "REGEX":
        try:
            re.compile(body.get("phrase") or "")
        except re.error:
            raise unprocessable("非法正则")
    obj = SensitivePhrase(
        phrase=body["phrase"], match_type=body.get("match_type") or "KEYWORD", category=body["category"],
        risk_level=body.get("risk_level") or "MEDIUM", risk_note=body.get("risk_note"), suggestion=body.get("suggestion"),
        is_active=body.get("is_active", True), created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "sensitive-phrases", obj, "新增敏感表述")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/sensitive-phrases/{oid}")
def put_sp(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(SensitivePhrase).filter(SensitivePhrase.id == oid).first()
    if not obj:
        raise not_found()
    if body.get("match_type") == "REGEX" or (obj.match_type == "REGEX" and body.get("phrase")):
        try:
            re.compile(body.get("phrase") or obj.phrase)
        except re.error:
            raise unprocessable("非法正则")
    obj, ver = update_and_snapshot(db, actor, "sensitive-phrases", obj, body, "更新敏感表述")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/sensitive-phrases/{oid}")
def del_sp(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(SensitivePhrase).filter(SensitivePhrase.id == oid).first()
    if not obj:
        raise not_found()
    ver = delete_and_snapshot(db, actor, "sensitive-phrases", obj, "删除敏感表述")
    return ok({"rule_version_no": ver})


@router.get("/suggestion-templates")
def list_st(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    return ok([orm_dict(r) for r in db.query(SuggestionTemplate).order_by(SuggestionTemplate.id).all()])


@router.post("/suggestion-templates")
def post_st(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = SuggestionTemplate(
        code=body["code"], rule_code=body.get("rule_code"), title=body["title"],
        template_text=body["template_text"], example_text=body.get("example_text"),
        is_active=body.get("is_active", True), created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "suggestion-templates", obj, "新增建议模板")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/suggestion-templates/{oid}")
def put_st(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(SuggestionTemplate).filter(SuggestionTemplate.id == oid).first()
    if not obj:
        raise not_found()
    obj, ver = update_and_snapshot(db, actor, "suggestion-templates", obj, body, "更新建议模板")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.delete("/suggestion-templates/{oid}")
def del_st(oid: int, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(SuggestionTemplate).filter(SuggestionTemplate.id == oid).first()
    if not obj:
        raise not_found()
    ver = delete_and_snapshot(db, actor, "suggestion-templates", obj, "删除建议模板")
    return ok({"rule_version_no": ver})


@router.get("/prompt-templates")
def list_pt(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    return ok([orm_dict(r) for r in db.query(PromptTemplate).all()])


@router.post("/prompt-templates")
def post_pt(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = PromptTemplate(
        code=body["code"], name=body["name"], system_prompt=body["system_prompt"], user_prompt=body["user_prompt"],
        output_schema=body.get("output_schema") or {}, is_active=body.get("is_active", True),
        created_at=now(), updated_at=now(),
    )
    obj, ver = create_and_snapshot(db, actor, "prompt-templates", obj, "新增提示词")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.put("/prompt-templates/{oid}")
def put_pt(oid: int, body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    obj = db.query(PromptTemplate).filter(PromptTemplate.id == oid).first()
    if not obj:
        raise not_found()
    obj, ver = update_and_snapshot(db, actor, "prompt-templates", obj, body, "更新提示词")
    d = orm_dict(obj)
    d["rule_version_no"] = ver
    return ok(d)


@router.get("/versions")
def list_versions(change_kind: str | None = None, page: int = 1, page_size: int = 20,
                  db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    q = db.query(RuleVersion)
    if change_kind:
        q = q.filter(RuleVersion.change_kind == change_kind)
    page, page_size, total, rows = _page(q.order_by(RuleVersion.version_no.desc()), page, page_size)
    items = []
    for r in rows:
        cnt = db.query(AiReport).filter(AiReport.rule_version_id == r.id).count()
        from models import User
        u = db.query(User).filter(User.id == r.created_by).first() if r.created_by else None
        items.append({
            "id": r.id, "version_no": r.version_no, "change_kind": r.change_kind, "change_action": r.change_action,
            "change_object_id": r.change_object_id, "change_summary": r.change_summary,
            "created_by_name": u.real_name if u else None,
            "created_at": r.created_at.isoformat() if r.created_at else None, "report_count": cnt,
        })
    return ok({"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/versions/{vid}")
def get_version(vid: int, diff_with: int | None = None, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    r = db.query(RuleVersion).filter(RuleVersion.id == vid).first()
    if not r:
        raise not_found()
    data = orm_dict(r)
    if diff_with:
        other = db.query(RuleVersion).filter(RuleVersion.id == diff_with).first()
        if other:
            data["changes"] = version_diff(other.snapshot or {}, r.snapshot or {})
    return ok(data)


@router.post("/dry-run")
def dry_run(body: dict, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    from services.rule_trial import trial_rules
    return ok(trial_rules(db, body, actor))


@router.post("/{kind}/import")
async def import_rules(kind: str, file: UploadFile = File(...), mode: str = Form("upsert"), dry_run: str = Form("true"),
                       db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024:
        raise too_large("导入文件超过 10 MB")
    dry = str(dry_run).lower() in ("1", "true", "yes")
    return ok(import_kind(db, actor, kind, data, mode, dry))


@router.get("/{kind}/export")
def export_rules(kind: str, db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    _writer(actor)
    wb = export_kind(db, kind)
    return xlsx_response(f"{kind}.xlsx", wb)
