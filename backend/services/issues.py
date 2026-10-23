from __future__ import annotations

import math
from sqlalchemy.orm import Session

from errors import conflict, forbidden, unprocessable
from models import Issue, MaterialVersion, ParseResult
from utils import now


def manual_location(db, material, location):
    if not isinstance(location, dict):
        raise unprocessable("问题位置格式无效")
    if not material:
        if any(location.get(key) is not None for key in ("material_id", "version_id", "page_no", "bbox")):
            raise unprocessable("指定问题位置前须选择材料")
        return location, None
    if location.get("material_id", material.id) != material.id:
        raise unprocessable("位置与关联材料不一致")
    vid = location.get("version_id") or material.current_version_id
    if type(vid) is not int or vid != material.current_version_id:
        raise conflict("材料版本已更新，请在当前版本重新定位问题")
    ver = db.query(MaterialVersion).filter(MaterialVersion.id == vid, MaterialVersion.material_id == material.id).first()
    if not ver:
        raise unprocessable("材料版本不存在")
    result = {**location, "material_id": material.id, "version_id": ver.id}
    page = location.get("page_no")
    if page is not None and (type(page) is not int or page < 1 or (ver.page_count and page > ver.page_count)):
        raise unprocessable("页码须为材料范围内的正整数")
    box = location.get("bbox")
    if box is not None:
        if page is None or not isinstance(box, list) or len(box) != 4 or any(
            isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in box
        ) or not (0 <= box[0] < box[2] and 0 <= box[1] < box[3]):
            raise unprocessable("框选坐标无效，须包含页码和有效矩形")
        parsed = db.query(ParseResult).filter(ParseResult.version_id == ver.id).first()
        dims = next((p for p in (parsed.pages or []) if p.get("page_no") == page), {}) if parsed else {}
        if (dims.get("width") and box[2] > dims["width"] + 0.01) or (dims.get("height") and box[3] > dims["height"] + 0.01):
            raise unprocessable("框选区域超出页面范围")
        result["bbox"] = box
    return result, ver.id


def act_issue(db: Session, issue: Issue, actor, action: str, note=None, patch=None) -> Issue:
    if action == "confirm":
        issue.review_status = "CONFIRMED"
    elif action == "reject":
        if not (note or "").strip():
            raise unprocessable("驳回必须填写理由")
        issue.review_status = "REJECTED"
    elif action == "modify":
        issue.original_snapshot = {
            "title": issue.title, "description": issue.description, "severity": issue.severity,
            "suggestion": issue.suggestion, "location": issue.location,
        }
        patch = patch or {}
        for k in ("severity", "title", "description", "suggestion", "location"):
            if k in patch and patch[k] is not None:
                setattr(issue, k, patch[k])
        issue.review_status = "MODIFIED"
    elif action == "reset":
        issue.review_status = "PENDING"
        issue.reviewed_by = None
        issue.reviewed_at = None
        issue.review_note = None
        issue.updated_at = now()
        db.flush()
        return issue
    else:
        raise unprocessable("未知操作")
    issue.reviewed_by = actor.id
    issue.reviewed_at = now()
    issue.review_note = note
    issue.review_level = {
        "BRANCH_REVIEWER": "BRANCH", "CROSS_REVIEWER": "CROSS",
        "COLLEGE_REVIEWER": "COLLEGE", "ORG_ADMIN": "ORG",
    }.get(actor.role)
    issue.updated_at = now()
    db.flush()
    return issue


def respond_issue(db: Session, issue: Issue, actor, response_type: str, response_text: str, version_id=None) -> Issue:
    from models import Archive, MaterialVersion, Submission

    sub = db.query(Submission).filter(Submission.id == issue.submission_id).first()
    arch = db.query(Archive).filter(Archive.id == sub.archive_id).first() if sub else None
    if not arch or arch.student_user_id != actor.id or actor.role != "STUDENT":
        raise forbidden()
    if sub.status not in ("DRAFT", "RETURNED") or not issue.is_active:
        raise forbidden("当前状态不可回复问题")
    if response_type not in ("MODIFIED", "EXPLAINED"):
        raise unprocessable("无效的整改回复类型")
    if version_id is not None:
        from models import Material
        q = db.query(MaterialVersion.id).join(Material, Material.id == MaterialVersion.material_id).filter(
            MaterialVersion.id == version_id, Material.submission_id == sub.id, Material.status == "ACTIVE",
        )
        if issue.material_id:
            q = q.filter(Material.id == issue.material_id)
        if not q.first():
            raise unprocessable("整改版本不属于对应材料或当前提交包")
    if response_type == "EXPLAINED" and len((response_text or "").strip()) < 10:
        raise unprocessable("情况说明不少于 10 字")
    issue.response_type = response_type
    issue.response_text = response_text
    issue.response_version_id = version_id
    issue.responded_at = now()
    issue.updated_at = now()
    db.flush()
    return issue


def serialize_issue(iss: Issue) -> dict:
    return {
        "id": iss.id, "submission_id": iss.submission_id, "report_id": iss.report_id,
        "material_id": iss.material_id, "material_version_id": iss.material_version_id,
        "source": iss.source, "category": iss.category, "severity": iss.severity,
        "rule_code": iss.rule_code, "rule_basis": iss.rule_basis, "title": iss.title,
        "description": iss.description, "location": iss.location, "actual_value": iss.actual_value,
        "expected_value": iss.expected_value, "suggestion": iss.suggestion,
        "suggestion_example": iss.suggestion_example, "needs_human_judgement": iss.needs_human_judgement,
        "confidence": iss.confidence, "fingerprint": iss.fingerprint, "is_active": iss.is_active,
        "review_status": iss.review_status, "review_level": iss.review_level, "review_note": iss.review_note,
        "response_type": iss.response_type, "response_text": iss.response_text,
        "resolution": iss.resolution, "is_new_in_recheck": iss.is_new_in_recheck,
        "created_at": iss.created_at.isoformat() if iss.created_at else None,
    }
