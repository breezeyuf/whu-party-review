from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

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
    User,
)
from security import hash_password
from utils import now
from config import ADMIN_PASSWORD, ADMIN_USERNAME, BACKEND_DIR
import secrets

SEED_DIR = BACKEND_DIR / "seed_data"


def _load(name: str) -> Any:
    path = SEED_DIR / name
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _snapshot(db: Session) -> dict:
    def dump(rows, fields):
        out = []
        for r in rows:
            item = {}
            for f in fields:
                v = getattr(r, f)
                if hasattr(v, "isoformat"):
                    v = v.isoformat()
                item[f] = v
            out.append(item)
        return out

    return {
        "material_types": dump(db.query(MaterialType).order_by(MaterialType.id).all(),
            ["id", "code", "name", "stage_codes", "title_keywords", "exclude_keywords",
             "element_template", "format_requirements", "date_node_map", "description",
             "is_active", "sort_order"]),
        "checklist_items": dump(db.query(ChecklistItem).order_by(ChecklistItem.id).all(),
            ["id", "stage_code", "material_type_id", "quantity_mode", "fixed_count",
             "period_months", "period_start_node", "period_end_node", "is_required",
             "requirement_text", "sort_order", "is_active"]),
        "time_node_defs": dump(db.query(TimeNodeDef).order_by(TimeNodeDef.sort_order).all(),
            ["id", "code", "name", "value_kind", "has_hours", "stage_code",
             "required_from_stage", "source_material_codes", "extract_keywords",
             "derive_expr", "sort_order", "is_active"]),
        "time_rules": dump(db.query(TimeRule).order_by(TimeRule.sort_order).all(),
            ["id", "code", "name", "rule_type", "params", "applies_stages", "severity",
             "basis", "message_template", "suggestion_template_id", "is_active", "sort_order"]),
        "check_rules": dump(db.query(CheckRule).order_by(CheckRule.sort_order).all(),
            ["id", "code", "category", "name", "engine", "applies_to", "params", "severity",
             "needs_human_judgement", "basis", "message_template", "suggestion_template_id",
             "is_optional", "is_active", "sort_order"]),
        "political_terms": dump(db.query(PoliticalTerm).order_by(PoliticalTerm.id).all(),
            ["id", "term_type", "standard_text", "wrong_variants", "sequence_items",
             "category", "severity", "note", "is_active"]),
        "sensitive_phrases": dump(db.query(SensitivePhrase).order_by(SensitivePhrase.id).all(),
            ["id", "phrase", "match_type", "category", "risk_level", "risk_note",
             "suggestion", "is_active"]),
        "suggestion_templates": dump(db.query(SuggestionTemplate).order_by(SuggestionTemplate.id).all(),
            ["id", "code", "rule_code", "title", "template_text", "example_text", "is_active"]),
        "prompt_templates": dump(db.query(PromptTemplate).order_by(PromptTemplate.id).all(),
            ["id", "code", "name", "system_prompt", "user_prompt", "output_schema", "is_active"]),
    }


def snapshot_rules(db: Session, kind: str, action: str, summary: str, object_id=None, user_id=None) -> RuleVersion:
    last = db.query(RuleVersion).order_by(RuleVersion.version_no.desc()).first()
    no = (last.version_no + 1) if last else 1
    row = RuleVersion(
        version_no=no,
        change_kind=kind,
        change_action=action,
        change_object_id=object_id,
        change_summary=summary,
        snapshot=_snapshot(db),
        created_by=user_id,
        created_at=now(),
    )
    db.add(row)
    db.flush()
    return row


def seed_rules(db: Session) -> None:
    if db.query(MaterialType).first():
        if not db.query(RuleVersion).first():
            snapshot_rules(db, "init", "INIT", "补写初始规则快照")
        return
    _seed_templates(db)
    _seed_material_types(db)
    _seed_checklists(db)
    _seed_nodes(db)
    _seed_time_rules(db)
    _seed_check_rules(db)
    _seed_terms(db)
    _seed_prompts(db)
    snapshot_rules(db, "init", "INIT", "写入默认规则基线（R-T01–R-T23、R-F01–R-F09、R-C01–R-C10）")
    db.flush()


def ensure_admin(db: Session) -> str | None:
    from models import Org, UserRole

    school = db.query(Org).filter(Org.org_type == "SCHOOL").first()
    if not school:
        school = Org(
            parent_id=None, org_type="SCHOOL", name="武汉大学", code="WHU",
            sort_order=0, is_active=True, is_demo=False, created_at=now(), updated_at=now(),
        )
        db.add(school)
        db.flush()
    user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    printed = None
    if not user:
        pwd = ADMIN_PASSWORD or secrets.token_urlsafe(10) + "A1"
        printed = None if ADMIN_PASSWORD else pwd
        user = User(
            username=ADMIN_USERNAME,
            password_hash=hash_password(pwd),
            real_name="系统管理员",
            org_id=school.id,
            is_active=True,
            must_change_password=not bool(ADMIN_PASSWORD),
            is_demo=False,
            created_at=now(),
            updated_at=now(),
        )
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role="SYS_ADMIN", org_id=school.id, created_at=now()))
        db.add(UserRole(user_id=user.id, role="ORG_ADMIN", org_id=school.id, created_at=now()))
        db.flush()
    return printed


def _seed_templates(db: Session) -> None:
    rows = [
        ("SUG_MISSING_MATERIAL", None, "缺项补交",
         "缺少《{材料名}》{缺少份数} 份（应交 {应交份数} 份，已交 {实交份数} 份）。请按要求补交：{提交要求}。截止日期：{截止日期}。",
         "请补交思想汇报 1 份，写明近期学习与实践收获。"),
        ("SUG_TIME_INTERVAL", "R-T05", "培养周期不足",
         "《{材料名}》中{节点名}为 {实际值}，不符合“{规则名}”要求（{要求值}）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。",
         None),
        ("SUG_DATE_INVALID", "R-T21", "日期不完整",
         "《{材料名}》第 {页码} 页日期“{原文}”书写不完整或无效，请按“××××年××月××日”格式补全。", None),
        ("SUG_TERM", "R-C01", "术语不规范",
         "第 {页码} 页“{原文}”表述不规范，标准写法为“{标准写法}”，请修改。", None),
        ("SUG_SIGNATURE", "R-F03", "缺签名",
         "《{材料名}》{签名位} 未检测到签名，请本人（或相关负责人）补签。", None),
        ("SUG_SEAL", "R-F04", "缺印章",
         "《{材料名}》{盖章位} 未检测到党组织印章，请联系相应党组织补盖。", None),
        ("SUG_JUDGEMENT", "R-C03", "需研判表述",
         "第 {页码} 页“{原文}”需审核员研判：{风险说明}。如确有不妥，请结合党章和理论学习修改相关表述。", None),
        ("SUG_FORMAT", None, "形式规范",
         "《{材料名}》{问题描述}。请按学校材料格式要求修改后重新上传。", None),
        ("SUG_CONTENT", None, "内容要素",
         "《{材料名}》缺少要素“{要素名}”，请按模板补写相关内容。", None),
    ]
    for code, rule, title, text, example in rows:
        db.add(SuggestionTemplate(
            code=code, rule_code=rule, title=title, template_text=text,
            example_text=example, is_active=True, created_at=now(), updated_at=now(),
        ))
    db.flush()


MATERIAL_TYPES = [
    ("APPLICATION_LETTER", "入党申请书", [1], ["入党申请书"],
     {"signature_date": "T02", "field:出生日期": "T01"},
     {"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"],
      "signature_slots": [{"slot": "本人签名", "keywords": ["签名", "申请人"]}],
      "seal_slots": [], "required_fields": ["姓名"], "handwriting_required": False}),
    ("PARTY_TALK_RECORD", "党组织派人谈话记录", [1], ["谈话记录", "派人谈话"],
     {"signature_date": "T03"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "signature_slots": [{"slot": "谈话人签名", "keywords": ["谈话人", "签名"]}],
      "seal_slots": [{"slot": "党组织印章", "keywords": ["盖章", "党支部"]}],
      "required_fields": []}),
    ("RECOMMENDATION", "推荐/推优材料", [2], ["推荐", "推优", "团组织推优"], {},
     {"doc_elements": ["title", "body", "signature", "date"],
      "signature_slots": [{"slot": "推荐组织签名", "keywords": ["签名"]}],
      "seal_slots": [{"slot": "团组织印章", "keywords": ["盖章"]}]}),
    ("ACTIVIST_MEETING_RECORD", "支委会研究确定积极分子记录", [2], ["确定入党积极分子", "支委会"],
     {"signature_date": "T04"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "signature_slots": [{"slot": "书记签名", "keywords": ["书记", "签名"]}],
      "seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}]}),
    ("ACTIVIST_FILING", "积极分子备案材料", [2], ["积极分子", "备案"], {"signature_date": "T04"},
     {"doc_elements": ["title", "body", "date"], "seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}]}),
    ("RECORD_BOOK_ACTIVIST", "写实簿·积极分子培养考察部分", [2], ["培养教育考察写实簿", "积极分子"],
     {"field:确定积极分子": "T04"},
     {"doc_elements": ["title", "body", "signature"], "handwriting_required": True}),
    ("THOUGHT_REPORT", "思想汇报", [2, 3, 5], ["思想汇报"], {"signature_date": "T06"},
     {"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"],
      "signature_slots": [{"slot": "本人签名", "keywords": ["汇报人", "签名"]}]}),
    ("ACTIVIST_TRAINING_CERT", "积极分子培训结业证明", [2], ["积极分子培训", "结业"], {},
     {"doc_elements": ["title", "body"], "seal_slots": [{"slot": "培训单位印章", "keywords": ["盖章"]}]}),
    ("AUTOBIOGRAPHY", "自传", [3], ["自传"], {"field:出生日期": "T01"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "required_fields": ["姓名", "出生日期", "家庭主要成员"], "min_chars": 3000}),
    ("CANDIDATE_MEETING_RECORD", "支委会确定发展对象记录", [3], ["确定为发展对象"],
     {"signature_date": "T08"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}]}),
    ("POLITICAL_REVIEW", "政治审查材料", [3], ["政治审查", "政审", "函调"], {"signature_date": "T09"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "seal_slots": [{"slot": "审查单位印章", "keywords": ["盖章"]}]}),
    ("TRAINING_CERT", "集中培训结业证书", [3], ["集中培训", "结业证书"],
     {"field:培训起": "T10", "field:学时": "T10"},
     {"doc_elements": ["title", "body"], "seal_slots": [{"slot": "党校印章", "keywords": ["盖章"]}]}),
    ("RECORD_BOOK_CANDIDATE", "写实簿·发展对象考察部分", [3], ["写实簿", "发展对象"], {},
     {"doc_elements": ["title", "body"], "handwriting_required": True}),
    ("CANDIDATE_PUBLICITY", "发展对象公示材料", [4], ["公示", "发展对象"],
     {"field:公示起": "T11"},
     {"doc_elements": ["title", "body", "date"], "seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}]}),
    ("PRE_REVIEW_OPINION", "上级党委预审意见", [4], ["预审"], {"signature_date": "T12"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}]}),
    ("APPLICATION_FORM", "入党志愿书", [4], ["入党志愿书"],
     {"field:出生日期": "T01", "signature_date": "T13"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "signature_slots": [{"slot": "本人签名", "keywords": ["志愿人", "签名"]}],
      "seal_slots": [{"slot": "党组织印章", "keywords": ["盖章"]}]}),
    ("ADMISSION_MEETING_RECORD", "支部大会讨论接收记录", [4], ["支部大会", "接收预备党员"],
     {"signature_date": "T14"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}]}),
    ("COMMITTEE_TALK_RECORD", "上级党委派人谈话记录", [4], ["上级党委", "谈话"], {"signature_date": "T15"},
     {"doc_elements": ["title", "body", "signature", "date"]}),
    ("ADMISSION_APPROVAL", "上级党委审批意见", [4], ["审批", "接收为预备党员"], {"signature_date": "T16"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}]}),
    ("REGULARIZATION_LETTER", "转正申请书", [5], ["转正申请"], {"signature_date": "T18"},
     {"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"]}),
    ("RECORD_BOOK_PROBATIONARY", "写实簿·预备党员考察部分", [5], ["写实簿", "预备党员"], {},
     {"doc_elements": ["title", "body"], "handwriting_required": True}),
    ("REGULARIZATION_PUBLICITY", "转正公示材料", [5], ["转正", "公示"], {"field:公示起": "T19"},
     {"doc_elements": ["title", "body", "date"], "seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}]}),
    ("REGULARIZATION_MEETING_RECORD", "支部大会讨论转正记录", [5], ["支部大会", "转正"],
     {"signature_date": "T20"},
     {"doc_elements": ["title", "body", "signature", "date"]}),
    ("REGULARIZATION_APPROVAL", "上级党委审批转正意见", [5], ["审批", "转为正式党员"], {"signature_date": "T21"},
     {"doc_elements": ["title", "body", "signature", "date"],
      "seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}]}),
]


def _seed_material_types(db: Session) -> None:
    for i, (code, name, stages, kws, dmap, fmt) in enumerate(MATERIAL_TYPES, start=1):
        elements = []
        if code in ("APPLICATION_LETTER", "THOUGHT_REPORT", "REGULARIZATION_LETTER"):
            elements = [
                {"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": True},
                {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": True},
            ]
        if code == "AUTOBIOGRAPHY":
            elements = [
                {"key": "family", "name": "家庭主要成员", "keywords": ["家庭主要成员", "家庭成员"], "required": True},
                {"key": "growth", "name": "成长经历", "keywords": ["成长", "学习经历"], "required": True},
                {"key": "thought", "name": "思想演变", "keywords": ["思想", "认识"], "required": True},
            ]
        db.add(MaterialType(
            code=code, name=name, stage_codes=stages, title_keywords=kws, exclude_keywords=[],
            element_template=elements, format_requirements=fmt, date_node_map=dmap,
            description=None, is_active=True, sort_order=i, created_at=now(), updated_at=now(),
        ))
    db.flush()


def _mt(db: Session, code: str) -> int:
    return db.query(MaterialType).filter(MaterialType.code == code).one().id


def _seed_checklists(db: Session) -> None:
    items = [
        (1, "APPLICATION_LETTER", "FIXED", 1, None, None, None, True, "本人亲笔或打印后签字的入党申请书"),
        (1, "PARTY_TALK_RECORD", "FIXED", 1, None, None, None, True, "党组织派人谈话记录"),
        (2, "RECOMMENDATION", "FIXED", 1, None, None, None, True, "党员推荐或团组织推优材料"),
        (2, "ACTIVIST_MEETING_RECORD", "FIXED", 1, None, None, None, True, "支委会（支部大会）研究确定积极分子记录"),
        (2, "ACTIVIST_FILING", "FIXED", 1, None, None, None, True, "积极分子备案材料"),
        (2, "RECORD_BOOK_ACTIVIST", "FIXED", 1, None, None, None, True, "写实簿积极分子培养考察部分"),
        (2, "THOUGHT_REPORT", "PER_PERIOD", 0, 3, "T04", "T08", True, "每季度至少一份思想汇报"),
        (2, "ACTIVIST_TRAINING_CERT", "FIXED", 1, None, None, None, False, "积极分子培训结业证明（可选）"),
        (3, "AUTOBIOGRAPHY", "FIXED", 1, None, None, None, True, "自传"),
        (3, "CANDIDATE_MEETING_RECORD", "FIXED", 1, None, None, None, True, "支委会确定发展对象记录"),
        (3, "POLITICAL_REVIEW", "FIXED", 1, None, None, None, True, "政治审查材料"),
        (3, "TRAINING_CERT", "FIXED", 1, None, None, None, True, "集中培训结业证书"),
        (3, "RECORD_BOOK_CANDIDATE", "FIXED", 1, None, None, None, True, "写实簿发展对象考察部分"),
        (3, "THOUGHT_REPORT", "PER_PERIOD", 0, 3, "T08", "T14", True, "每季度至少一份思想汇报"),
        (4, "CANDIDATE_PUBLICITY", "FIXED", 1, None, None, None, True, "发展对象公示材料"),
        (4, "PRE_REVIEW_OPINION", "FIXED", 1, None, None, None, True, "上级党委预审意见"),
        (4, "APPLICATION_FORM", "FIXED", 1, None, None, None, True, "入党志愿书"),
        (4, "ADMISSION_MEETING_RECORD", "FIXED", 1, None, None, None, True, "支部大会讨论接收预备党员记录"),
        (4, "COMMITTEE_TALK_RECORD", "FIXED", 1, None, None, None, True, "上级党委派人谈话记录"),
        (4, "ADMISSION_APPROVAL", "FIXED", 1, None, None, None, True, "上级党委审批意见"),
        (5, "REGULARIZATION_LETTER", "FIXED", 1, None, None, None, True, "转正申请书"),
        (5, "RECORD_BOOK_PROBATIONARY", "FIXED", 1, None, None, None, True, "写实簿预备党员考察部分"),
        (5, "REGULARIZATION_PUBLICITY", "FIXED", 1, None, None, None, True, "转正公示材料"),
        (5, "REGULARIZATION_MEETING_RECORD", "FIXED", 1, None, None, None, True, "支部大会讨论转正记录"),
        (5, "REGULARIZATION_APPROVAL", "FIXED", 1, None, None, None, True, "上级党委审批转正意见"),
        (5, "THOUGHT_REPORT", "PER_PERIOD", 0, 3, "T14", "T20", True, "预备期每季度至少一份思想汇报"),
    ]
    for i, (stage, code, mode, n, months, start, end, req, text) in enumerate(items, start=1):
        db.add(ChecklistItem(
            stage_code=stage, material_type_id=_mt(db, code), quantity_mode=mode,
            fixed_count=n, period_months=months, period_start_node=start, period_end_node=end,
            is_required=req, requirement_text=text, sort_order=i, is_active=True,
            created_at=now(), updated_at=now(),
        ))
    db.flush()


def _seed_nodes(db: Session) -> None:
    nodes = [
        ("T01", "出生日期", "DATE", False, 1, 1, ["APPLICATION_LETTER", "AUTOBIOGRAPHY", "APPLICATION_FORM"], ["出生日期", "生于"]),
        ("T02", "递交入党申请书日期", "DATE", False, 1, 1, ["APPLICATION_LETTER"], ["入党申请", "申请入党"]),
        ("T03", "党组织派人谈话日期", "DATE", False, 1, 2, ["PARTY_TALK_RECORD"], ["谈话"]),
        ("T04", "确定为入党积极分子日期", "DATE", False, 2, 2, ["ACTIVIST_MEETING_RECORD", "ACTIVIST_FILING"], ["确定为入党积极分子", "列为入党积极分子"]),
        ("T05", "指定培养联系人日期", "DATE", False, 2, 2, ["RECORD_BOOK_ACTIVIST"], ["培养联系人"]),
        ("T06", "思想汇报日期", "DATE_SEQ", False, 2, 2, ["THOUGHT_REPORT"], ["思想汇报"]),
        ("T07", "培养考察记录日期", "DATE_SEQ", False, 2, 2, ["RECORD_BOOK_ACTIVIST", "RECORD_BOOK_CANDIDATE", "RECORD_BOOK_PROBATIONARY"], ["考察", "写实"]),
        ("T08", "确定为发展对象日期", "DATE", False, 3, 3, ["CANDIDATE_MEETING_RECORD"], ["确定为发展对象"]),
        ("T09", "政治审查完成日期", "DATE", False, 3, 4, ["POLITICAL_REVIEW"], ["政治审查", "政审"]),
        ("T10", "集中培训起止与学时", "DATE_RANGE", True, 3, 4, ["TRAINING_CERT"], ["培训", "学时", "结业"]),
        ("T11", "发展对象公示起止", "DATE_RANGE", False, 4, 4, ["CANDIDATE_PUBLICITY"], ["公示"]),
        ("T12", "上级党委预审日期", "DATE", False, 4, 4, ["PRE_REVIEW_OPINION"], ["预审"]),
        ("T13", "填写入党志愿书日期", "DATE", False, 4, 4, ["APPLICATION_FORM"], ["志愿书"]),
        ("T14", "支部大会接收预备党员日期", "DATE", False, 4, 4, ["ADMISSION_MEETING_RECORD", "APPLICATION_FORM"], ["支部大会", "接收为预备党员"]),
        ("T15", "上级党委派人谈话日期", "DATE", False, 4, 4, ["COMMITTEE_TALK_RECORD"], ["谈话"]),
        ("T16", "上级党委审批预备党员日期", "DATE", False, 4, 4, ["ADMISSION_APPROVAL"], ["审批", "预备党员"]),
        ("T17", "编入党支部日期", "DATE", False, 4, 5, ["RECORD_BOOK_PROBATIONARY"], ["编入"]),
        ("T18", "递交转正申请书日期", "DATE", False, 5, 5, ["REGULARIZATION_LETTER"], ["转正申请"]),
        ("T19", "转正公示起止", "DATE_RANGE", False, 5, 5, ["REGULARIZATION_PUBLICITY"], ["转正公示", "公示"]),
        ("T20", "支部大会讨论转正日期", "DATE", False, 5, 5, ["REGULARIZATION_MEETING_RECORD"], ["转正", "支部大会"]),
        ("T21", "上级党委审批转正日期", "DATE", False, 5, 5, ["REGULARIZATION_APPROVAL"], ["审批", "正式党员"]),
        ("D01", "预备期满日", "DERIVED", False, 4, 5, [], []),
    ]
    for i, (code, name, kind, hours, stage, req_from, sources, kws) in enumerate(nodes, start=1):
        expr = {"base": "T14", "offset": {"value": 1, "unit": "YEAR"}} if code == "D01" else None
        db.add(TimeNodeDef(
            code=code, name=name, value_kind=kind, has_hours=hours, stage_code=stage,
            required_from_stage=req_from, source_material_codes=sources, extract_keywords=kws,
            derive_expr=expr, sort_order=i, is_active=True, created_at=now(), updated_at=now(),
        ))
    db.flush()


def _tr(code, name, rtype, stages, sev, basis, msg, checks, sort):
    return dict(code=code, name=name, rule_type=rtype, applies_stages=stages, severity=sev,
                basis=basis, message_template=msg, params={"checks": checks}, sort_order=sort)


def _seed_time_rules(db: Session) -> None:
    basis_detail = "中国共产党发展党员工作细则"
    basis_const = "中国共产党章程"
    rules = [
        _tr("R-T01", "年满十八周岁", "AGE", [1, 2, 3, 4, 5], "BLOCK", basis_const,
            "递交入党申请书时未满 18 周岁（出生 {T01}，申请 {T02}）",
            [{"op": "age_at_least", "birth": "T01", "at": "T02", "years": 18}], 1),
        _tr("R-T02", "谈话不超过一个月", "INTERVAL", [1, 2], "WARN", basis_detail,
            "党组织派人谈话（{T03}）距递交申请（{T02}）超过一个月",
            [{"op": "within", "a": "T02", "b": "T03", "max": {"value": 1, "unit": "MONTH"}}], 2),
        _tr("R-T03", "谈话不早于申请", "ORDER", [1, 2], "BLOCK", basis_detail,
            "谈话日期（{T03}）早于递交申请日期（{T02}）",
            [{"op": "before", "a": "T02", "b": "T03", "strict": False}], 3),
        _tr("R-T04", "确定积极分子距申请不过久", "INTERVAL", [2], "WARN", basis_detail,
            "确定积极分子（{T04}）距递交申请（{T02}）间隔过长",
            [{"op": "within", "a": "T02", "b": "T04", "max": {"value": 30, "unit": "DAY"}}], 4),
        _tr("R-T05", "积极分子培养满一年", "INTERVAL", [3, 4, 5], "BLOCK", basis_detail,
            "确定积极分子（{T04}）至确定发展对象（{T08}）间隔不足 1 年",
            [{"op": "at_least", "a": "T04", "b": "T08", "min": {"value": 1, "unit": "YEAR"}}], 5),
        _tr("R-T06", "思想汇报相邻间隔", "SEQ_GAP", [2, 3, 5], "WARN", basis_detail,
            "思想汇报相邻间隔超过一个季度",
            [{"op": "seq_max_gap", "seq": "T06[*]", "from": "T04", "to": "T08", "max": {"value": 3, "unit": "MONTH"}}], 6),
        _tr("R-T07", "思想汇报按期提交", "SEQ_COUNT", [2, 3, 5], "BLOCK", basis_detail,
            "培养期内思想汇报未按每季度至少一份提交",
            [{"op": "seq_period_count", "seq": "T06[*]", "from": "T04", "to": "T08", "period_months": 3, "min_per_period": 1}], 7),
        _tr("R-T08", "政审完成于确定发展对象之后", "ORDER", [3, 4], "BLOCK", basis_detail,
            "政治审查完成日期（{T09}）早于确定发展对象（{T08}）",
            [{"op": "before", "a": "T08", "b": "T09", "strict": False}], 8),
        _tr("R-T09", "集中培训时长或学时", "DURATION", [3, 4], "BLOCK", basis_detail,
            "集中培训未满规定时长或学时",
            [{"op": "duration_min", "node": "T10", "min": {"value": 3, "unit": "DAY"}, "or_hours": 24}], 9),
        _tr("R-T10", "公示不少于五个工作日且在预审前", "COMPOSITE", [4], "WARN", basis_detail,
            "发展对象公示未满五个工作日或晚于预审",
            [{"op": "before", "a": "T11.end", "b": "T12", "strict": False},
             {"op": "duration_min", "node": "T11", "min": {"value": 5, "unit": "WORKDAY"}}], 10),
        _tr("R-T11", "预审在填写志愿书之前", "ORDER", [4], "BLOCK", basis_detail,
            "填写入党志愿书（{T13}）早于上级党委预审（{T12}）",
            [{"op": "before", "a": "T12", "b": "T13", "strict": False}], 11),
        _tr("R-T12", "支部大会在预审之后", "ORDER", [4], "BLOCK", basis_detail,
            "支部大会接收日期（{T14}）早于预审（{T12}）",
            [{"op": "before", "a": "T12", "b": "T14", "strict": True}], 12),
        _tr("R-T13", "党委派人谈话在支部大会之后", "ORDER", [4], "BLOCK", basis_detail,
            "上级党委派人谈话（{T15}）早于支部大会（{T14}）",
            [{"op": "before", "a": "T14", "b": "T15", "strict": False}], 13),
        _tr("R-T14", "审批在谈话之后", "ORDER", [4], "BLOCK", basis_detail,
            "上级党委审批（{T16}）早于派人谈话（{T15}）",
            [{"op": "before", "a": "T15", "b": "T16", "strict": False}], 14),
        _tr("R-T15", "党委审批不超过三个月", "INTERVAL", [4, 5], "WARN", basis_detail,
            "上级党委审批（{T16}）距支部大会（{T14}）超过三个月",
            [{"op": "within", "a": "T14", "b": "T16", "max": {"value": 3, "unit": "MONTH"}}], 15),
        _tr("R-T16", "派生预备期满日", "DERIVED", [4, 5], "CALC", basis_detail,
            "预备期满日 = 支部大会接收日 + 1 年",
            [{"op": "derive", "name": "D01", "base": "T14", "offset": {"value": 1, "unit": "YEAR"}}], 16),
        _tr("R-T17", "转正申请不晚于预备期满", "ORDER", [5], "WARN", basis_detail,
            "转正申请（{T18}）晚于预备期满日（D01）",
            [{"op": "before", "a": "T18", "b": "D01", "strict": False}], 17),
        _tr("R-T18", "转正公示不少于五个工作日", "DURATION", [5], "WARN", basis_detail,
            "转正公示不足五个工作日",
            [{"op": "duration_min", "node": "T19", "min": {"value": 5, "unit": "WORKDAY"}}], 18),
        _tr("R-T19", "转正大会在预备期满之后", "ORDER", [5], "BLOCK", basis_detail,
            "支部大会讨论转正（{T20}）早于预备期满日",
            [{"op": "before", "a": "D01", "b": "T20", "strict": False}], 19),
        _tr("R-T20", "同一节点多来源一致", "CONSISTENCY", [1, 2, 3, 4, 5], "BLOCK", basis_detail,
            "时间节点在多份材料中取值不一致",
            [{"op": "consistent", "nodes": "*"}], 20),
        _tr("R-T21", "日期合法且不晚于上传日", "VALID_DATE", [1, 2, 3, 4, 5], "BLOCK", basis_detail,
            "抽取日期不完整、不合法或晚于材料上传日",
            [{"op": "valid_date", "nodes": "*"}], 21),
        _tr("R-T22", "阶段必填节点与单调递增", "REQUIRED_NODES", [1, 2, 3, 4, 5], "BLOCK", basis_detail,
            "当前阶段关键时间节点缺失或顺序颠倒",
            [{"op": "required", "nodes_by_stage": {
                "1": ["T01", "T02"], "2": ["T02", "T03", "T04"], "3": ["T04", "T08"],
                "4": ["T08", "T09", "T10", "T11", "T12", "T13", "T14", "T15", "T16"],
                "5": ["T14", "T16", "T18", "T19", "T20"]}},
             {"op": "monotonic", "nodes": ["T02", "T04", "T08", "T14", "T20"]}], 22),
        _tr("R-T23", "序列日期落在培养区间", "IN_RANGE", [2, 3, 5], "WARN", basis_detail,
            "思想汇报日期未落在对应培养考察区间内",
            [{"op": "seq_in_range", "seq": "T06[*]", "from": "T04", "to": "T08"}], 23),
    ]
    for r in rules:
        db.add(TimeRule(
            **r, is_active=True, created_at=now(), updated_at=now(),
        ))
    db.flush()


def _seed_check_rules(db: Session) -> None:
    fmt = [
        ("R-F01", "文书结构完整", "RULE", [], "WARN", False, False,
         "材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素",
         {"elements": ["title", "salutation", "body", "closing", "signature", "date"]}),
        ("R-F02", "落款日期格式", "RULE", [], "WARN", False, False,
         "落款日期未按“××××年××月××日”书写", {}),
        ("R-F03", "签名齐全", "RULE", [], "BLOCK", False, False,
         "规定签名位未检测到签名", {}),
        ("R-F04", "印章齐全", "RULE", [], "BLOCK", False, False,
         "规定盖章位未检测到党组织印章", {}),
        ("R-F05", "手写材料可辨识", "RULE", ["RECORD_BOOK_ACTIVIST", "RECORD_BOOK_CANDIDATE", "RECORD_BOOK_PROBATIONARY"],
         "WARN", False, False, "写实簿等手写材料清晰度不足或文本过少", {}),
        ("R-F06", "篇幅下限", "RULE", ["AUTOBIOGRAPHY"], "WARN", False, False,
         "材料正文字数不足规定篇幅", {"min_chars": {"AUTOBIOGRAPHY": 3000}}),
        ("R-F07", "扫描件清晰度", "RULE", [], "WARN", False, False,
         "扫描件分辨率不足或页面模糊", {"min_dpi": 150, "blur_threshold": 60}),
        ("R-F08", "版式规范", "RULE", [], "INFO", False, True,
         "DOCX 字体、字号、行距或页边距与学校模板不一致",
         {"docx_layout": {"font": "宋体", "size_pt": 12, "line_spacing": 1.5, "margin_cm": 2.54}}),
        ("R-F09", "页面方向与装订", "RULE", [], "INFO", False, True,
         "页面方向或装订边距不符合归档要求", {}),
    ]
    for i, (code, name, engine, applies, sev, judge, optional, msg, params) in enumerate(fmt, start=1):
        db.add(CheckRule(
            code=code, category="FORMAT", name=name, engine=engine, applies_to=applies, params=params,
            severity=sev, needs_human_judgement=judge, basis="学校党员发展材料规范",
            message_template=msg, is_optional=optional, is_active=not optional, sort_order=i,
            created_at=now(), updated_at=now(),
        ))
    content = [
        ("R-C01", "政治术语规范", "RULE", [], "WARN", False, False,
         "出现不规范政治术语或并列顺序错误", {}),
        ("R-C02", "政治表述准确性", "LLM", [], "WARN", True, False,
         "政治理论表述疑似不准确，请审核员研判", {}),
        ("R-C03", "意识形态表述", "RULE_LLM", [], "BLOCK", True, False,
         "疑似存在需研判的意识形态表述", {}),
        ("R-C04", "入党动机表述", "RULE_LLM", ["APPLICATION_LETTER", "THOUGHT_REPORT", "REGULARIZATION_LETTER"],
         "WARN", True, False, "入党动机表述疑似功利化或要素不足", {}),
        ("R-C05", "内容要素完整", "RULE", [], "WARN", False, False,
         "材料缺少模板规定的内容要素", {}),
        ("R-C06", "基本信息一致", "RULE", [], "BLOCK", False, False,
         "姓名、学号、出生日期等基本信息与档案或其他材料不一致", {}),
        ("R-C07", "经历与时间线吻合", "LLM", ["AUTOBIOGRAPHY", "APPLICATION_LETTER"], "WARN", True, False,
         "自传或申请书经历与时间节点疑似矛盾", {}),
        ("R-C08", "思想认识深度", "LLM", ["THOUGHT_REPORT", "AUTOBIOGRAPHY"], "INFO", True, False,
         "思想认识表述较空泛，建议结合学习与实践写实", {}),
        ("R-C09", "引用原文核对", "RULE", [], "INFO", False, True,
         "疑似错误引用党章或重要文献原文", {}),
        ("R-C10", "同批次文本高度相似", "RULE", ["THOUGHT_REPORT", "AUTOBIOGRAPHY", "APPLICATION_LETTER"],
         "WARN", False, True, "与同批次其他学生材料文本高度相似", {"threshold": 0.8}),
    ]
    for i, (code, name, engine, applies, sev, judge, optional, msg, params) in enumerate(content, start=10):
        db.add(CheckRule(
            code=code, category="CONTENT", name=name, engine=engine, applies_to=applies, params=params,
            severity=sev, needs_human_judgement=judge, basis="党章及发展党员工作细则；学校审核标准",
            message_template=msg, is_optional=optional, is_active=not optional, sort_order=i,
            created_at=now(), updated_at=now(),
        ))
    db.flush()


def _seed_terms(db: Session) -> None:
    db.add(PoliticalTerm(
        term_type="SEQUENCE",
        standard_text="马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想",
        wrong_variants=[],
        sequence_items=["马克思列宁主义", "毛泽东思想", "邓小平理论", "“三个代表”重要思想", "科学发展观", "习近平新时代中国特色社会主义思想"],
        category="指导思想", severity="BLOCK",
        note="示例数据，请组织部按学校标准核定后启用", is_active=True,
        created_at=now(), updated_at=now(),
    ))
    db.add(PoliticalTerm(
        term_type="VARIANT", standard_text="中国共产党是中国工人阶级的先锋队",
        wrong_variants=["中国共产党是中国人民的先锋队"],
        sequence_items=[], category="党的性质", severity="WARN",
        note="示例数据，完整表述见党章", is_active=True, created_at=now(), updated_at=now(),
    ))
    db.add(PoliticalTerm(
        term_type="VARIANT", standard_text="全心全意为人民服务",
        wrong_variants=["全心全意为人名服务", "全心全意为人民做贡献"],
        sequence_items=[], category="宗旨", severity="WARN",
        note="示例数据", is_active=True, created_at=now(), updated_at=now(),
    ))
    db.add(SensitivePhrase(
        phrase="入党可以评优评奖", match_type="KEYWORD", category="MOTIVATION",
        risk_level="HIGH", risk_note="功利化入党动机表述",
        suggestion="请从理想信念、服务师生、发挥作用等角度重写入党动机。",
        is_active=True, created_at=now(), updated_at=now(),
    ))
    db.add(SensitivePhrase(
        phrase="为了好找工作", match_type="KEYWORD", category="MOTIVATION",
        risk_level="HIGH", risk_note="功利化入党动机表述",
        suggestion="请结合对党的认识和自身成长经历写明入党动机。",
        is_active=True, created_at=now(), updated_at=now(),
    ))
    db.add(SensitivePhrase(
        phrase="入党有面子", match_type="KEYWORD", category="MOTIVATION",
        risk_level="MEDIUM", risk_note="功利化入党动机表述",
        suggestion="请删除面子、待遇等表述，聚焦党员义务。",
        is_active=True, created_at=now(), updated_at=now(),
    ))
    db.flush()


def _seed_prompts(db: Session) -> None:
    prompts = [
        ("CLASSIFY", "材料分类",
         "你是高校党员发展材料审核助手。只根据给定文本判断材料类型。必须输出 JSON。",
         "候选类型：{types}\n文本：\n{text}\n请输出 {\"type_code\":\"...\",\"confidence\":0-1,\"reason\":\"...\"}",
         {"type_code": "string", "confidence": "number", "reason": "string"}),
        ("EXTRACT", "信息抽取",
         "你是材料信息抽取助手。从文本中抽取时间节点与基本信息，不得编造。输出 JSON。",
         "节点定义：{nodes}\n文本：\n{text}\n输出 {\"fields\":{},\"dates\":[{\"node_code\",\"date\",\"raw_text\"}]}",
         {"fields": "object", "dates": "array"}),
        ("CONTENT_CHECK", "内容核查",
         "你是党建材料内容审核助手。只标注疑似不规范表述，不下定性政治结论。涉及意识形态一律标 needs_human_judgement=true。",
         "规则：{rules}\n文本：\n{text}\n输出 {\"issues\":[{\"rule_code\",\"snippet\",\"reason\",\"confidence\"}]}",
         {"issues": "array"}),
        ("SUGGEST", "修改建议润色",
         "在给定模板约束下润色修改建议，必须保留模板中的修改要求句，不得改变事实。",
         "模板：{template}\n变量：{vars}\n问题：{issue}\n输出 {\"suggestion\":\"...\"}",
         {"suggestion": "string"}),
    ]
    for code, name, sys_p, user_p, schema in prompts:
        db.add(PromptTemplate(
            code=code, name=name, system_prompt=sys_p, user_prompt=user_p,
            output_schema=schema, is_active=True, created_at=now(), updated_at=now(),
        ))
    db.flush()

