from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import Actor, get_current_user
from models import MaterialType, Stage, TimeNodeDef
from schemas.common import ok
from utils import CATEGORY_NAMES, ROLE_NAMES, SEVERITY_NAMES, STATUS_NAMES

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta(db: Session = Depends(get_db), actor: Actor = Depends(get_current_user)):
    stages = [{"code": s.code, "key": s.stage_key, "name": s.name} for s in db.query(Stage).order_by(Stage.sort_order).all()]
    mts = db.query(MaterialType).filter(MaterialType.is_active.is_(True)).order_by(MaterialType.sort_order).all()
    return ok({
        "stages": stages,
        "roles": [{"code": k, "name": v} for k, v in ROLE_NAMES.items()],
        "submission_statuses": [{"code": k, "name": v} for k, v in STATUS_NAMES.items()],
        "issue_categories": [{"code": k, "name": v} for k, v in CATEGORY_NAMES.items()],
        "severities": [{"code": k, "name": v} for k, v in SEVERITY_NAMES.items()],
        "review_statuses": [
            {"code": "PENDING", "name": "待确认"}, {"code": "CONFIRMED", "name": "已确认"},
            {"code": "REJECTED", "name": "已驳回"}, {"code": "MODIFIED", "name": "已修改"},
        ],
        "recommendations": [
            {"code": "SUGGEST_PASS", "name": "建议通过"}, {"code": "SUGGEST_RETURN", "name": "建议退回"},
            {"code": "NEEDS_REVIEW", "name": "需人工研判"},
        ],
        "handover_statuses": [
            {"code": "REQUIRED", "name": "待人工审核"}, {"code": "DONE", "name": "已接管"},
            {"code": "NOT_REQUIRED", "name": "无需接管"},
        ],
        "material_types": [{"id": t.id, "code": t.code, "name": t.name, "stage_codes": t.stage_codes} for t in mts],
        "time_nodes": [{"code": n.code, "name": n.name, "value_kind": n.value_kind,
                        "has_hours": n.has_hours, "is_active": n.is_active}
                       for n in db.query(TimeNodeDef).order_by(TimeNodeDef.sort_order).all()],
        "levels": [
            {"code": "SELF", "name": "自查"}, {"code": "BRANCH", "name": "支部初审"},
            {"code": "CROSS", "name": "交叉互查"}, {"code": "COLLEGE", "name": "学院复审"},
            {"code": "ORG", "name": "组织部备案"},
        ],
    })
