from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from models import Stage, SystemSetting

TZ8 = timezone(timedelta(hours=8))

STAGE_NAMES = {
    1: "申请入党",
    2: "确定入党积极分子",
    3: "确定发展对象",
    4: "接收预备党员",
    5: "预备党员转正",
}

ROLE_NAMES = {
    "STUDENT": "学生",
    "BRANCH_REVIEWER": "党支部审核员",
    "CROSS_REVIEWER": "交叉互查员",
    "COLLEGE_REVIEWER": "学院党委审核员",
    "ORG_ADMIN": "组织部管理员",
    "SYS_ADMIN": "系统管理员",
}

STATUS_NAMES = {
    "DRAFT": "草稿",
    "BRANCH_REVIEW": "支部初审",
    "CROSS_REVIEW": "交叉互查",
    "COLLEGE_REVIEW": "学院复审",
    "ORG_FILING": "组织部备案",
    "FILED": "已备案",
    "RETURNED": "已退回",
}

LEVEL_BY_STATUS = {
    "DRAFT": "SELF",
    "BRANCH_REVIEW": "BRANCH",
    "CROSS_REVIEW": "CROSS",
    "COLLEGE_REVIEW": "COLLEGE",
    "ORG_FILING": "ORG",
    "FILED": "ORG",
    "RETURNED": None,
}

STATUS_BY_RETURN_LEVEL = {
    "BRANCH": "BRANCH_REVIEW",
    "CROSS": "CROSS_REVIEW",
    "COLLEGE": "COLLEGE_REVIEW",
    "ORG": "ORG_FILING",
}

CATEGORY_NAMES = {
    "COMPLETENESS": "完整性",
    "TIME": "时间逻辑",
    "FORMAT": "形式规范",
    "CONTENT": "内容规范",
}

SEVERITY_NAMES = {
    "BLOCK": "阻断",
    "WARN": "警告",
    "INFO": "提示",
    "CALC": "计算",
}


def now() -> datetime:
    return datetime.now(TZ8)


def as_date(value: Any) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value)[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def get_setting(db: Session, key: str, default: Optional[dict] = None) -> dict:
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not row:
        return default or {}
    val = row.value
    return val if isinstance(val, dict) else (default or {})


def stage_name(db: Session, code: int) -> str:
    row = db.query(Stage).filter(Stage.code == code).first()
    return row.name if row else STAGE_NAMES.get(code, str(code))


def serialize_user_brief(user) -> dict:
    org = user.org
    roles = [{"role": r.role, "org_id": r.org_id, "org_name": r.org.name if r.org else None} for r in (user.roles or [])]
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "org_id": user.org_id,
        "org_name": org.name if org else None,
        "roles": roles,
        "is_active": user.is_active,
        "is_demo": user.is_demo,
        "must_change_password": user.must_change_password,
        "gender": user.gender,
        "email": user.email,
        "phone_masked": user.phone_masked,
        "locked_until": user.locked_until.isoformat() if user.locked_until else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }
