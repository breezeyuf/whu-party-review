"""《工作台再次核查 2026-10-27》7 项缺陷的回归用例。"""
import json
from io import BytesIO
from types import SimpleNamespace

import pytest
from openpyxl import Workbook

from models import AuditLog, Issue, Material, Notice, Submission, TimeNodeDef
from tests.test_review_regressions import case, test_engine, as_client, material, parsed_material, pair
from utils import now


def sysadmin(c):
    actor = SimpleNamespace(**{**vars(c.student), "role": "SYS_ADMIN"})
    actor.id, actor.username = c.student.id, c.student.username
    return actor


def test_sys_admin_cannot_read_material_content(case, as_client):
    c = case
    m, _ = parsed_material(c)
    client = as_client(sysadmin(c))
    for path in (f"/api/materials/{m.id}", f"/api/materials/{m.id}/parsed",
                 f"/api/materials/{m.id}/versions", f"/api/archives/{c.arch.id}"):
        assert client.get(path).status_code == 404, path
    # 系统管理职责不受影响：用户与设置接口仍可用
    assert client.get("/api/users").status_code == 200
    assert client.get("/api/settings").status_code == 200
    # 聚合口径保留：管理台与统计仍可看数字，但不含材料正文
    assert client.get("/api/dashboard").status_code == 200
    assert client.get("/api/stats/overview").status_code == 200


def test_cross_reviewer_material_access_follows_submission_batch(case, as_client):
    c = case
    pair(c, batch=0)
    own, _ = material(c)  # 位于已分配批次 0 的提交包
    other_sub = c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.batches[1].id,
                      college_id=c.college.id, branch_id=c.branches[0].id, status="DRAFT",
                      ai_status="NONE", created_at=now(), updated_at=now())
    other = c.add(Material, archive_id=c.arch.id, submission_id=other_sub.id, stage_code=2,
                  title="批次外材料", status="ACTIVE", created_at=now(), updated_at=now())
    c.db.flush()
    client = as_client(c.cross)
    assert client.get(f"/api/materials/{own.id}").status_code == 200
    assert client.get(f"/api/submissions/{other_sub.id}").status_code == 404
    for path in (f"/api/materials/{other.id}", f"/api/materials/{other.id}/parsed",
                 f"/api/materials/{other.id}/versions", f"/api/materials/{other.id}/diff"):
        assert client.get(path).status_code == 404, path


def test_node_correction_rejects_invalid_input_without_touching_previous_value(case, as_client):
    c = case
    client = as_client(c.reviewer)
    endpoint = f"/api/archives/{c.arch.id}/timeline/T02"
    assert client.put(endpoint, json={"date": "2026-01-05", "reason": "核对原件"}).status_code == 200
    node = c.db.query(__import__("models").ArchiveTimeNode).filter_by(archive_id=c.arch.id, node_code="T02").first()
    assert node.corrected_date.isoformat() == "2026-01-05"

    for body in ({"date": "2026-02-30", "reason": "核对原件"},
                 {"date": "2026-01-05", "end_date": "2026-01-01", "reason": "核对原件"},
                 {"date": "", "reason": "核对原件"},
                 {"date": "2026-01-05", "hours": 3, "reason": "核对原件"}):
        response = client.put(endpoint, json=body)
        assert response.status_code == 422, (body, response.text)
    c.db.refresh(node)
    assert node.corrected_date.isoformat() == "2026-01-05"

    assert client.put(endpoint, json={"clear": True, "reason": "撤销校正"}).status_code == 200
    c.db.refresh(node)
    assert node.corrected_date is None


def test_rule_create_and_import_share_required_field_checks(case, as_client):
    c = case
    client = as_client(c.org)
    empty = client.post("/api/rules/time-rules", json={})
    assert empty.status_code == 422
    assert {item["field"] for item in empty.json()["data"]["errors"]} >= {"code", "name", "rule_type", "severity", "message_template"}

    def workbook(rows):
        wb = Workbook()
        ws = wb.active
        ws.append(["code", "name", "rule_type", "params", "severity", "message_template"])
        for row in rows:
            ws.append(row)
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    params = json.dumps({"checks": [{"op": "before", "a": "T01", "b": "T02"}]})
    missing = client.post("/api/rules/time-rules/import",
                          files={"file": ("a.xlsx", workbook([["R-T98", None, "ORDER", params, "WARN", "提示"]]))},
                          data={"mode": "upsert", "dry_run": "true"})
    assert missing.status_code == 200
    assert missing.json()["data"]["created"] == 0
    assert "缺少必填字段" in missing.json()["data"]["errors"][0]["message"]

    duplicated = client.post("/api/rules/time-rules/import",
                             files={"file": ("b.xlsx", workbook([
                                 ["R-T97", "测试", "ORDER", params, "WARN", "提示"],
                                 ["R-T97", "测试", "ORDER", params, "WARN", "提示"]]))},
                             data={"mode": "upsert", "dry_run": "true"})
    assert duplicated.status_code == 200
    assert duplicated.json()["data"]["errors"][0]["message"].startswith("同一文件重复 code")

    blocked = client.post("/api/rules/time-rules/import",
                          files={"file": ("c.xlsx", workbook([["R-T96", None, "ORDER", params, "WARN", "提示"]]))},
                          data={"mode": "upsert", "dry_run": "false"})
    assert blocked.status_code == 422
    assert c.db.query(__import__("models").TimeRule).filter_by(code="R-T96").count() == 0


def test_upload_new_version_records_each_issue_response(case, as_client):
    c = case
    sub = c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.batches[0].id,
                college_id=c.college.id, branch_id=c.branches[0].id, status="DRAFT",
                ai_status="DONE", created_at=now(), updated_at=now())
    m = c.add(Material, archive_id=c.arch.id, submission_id=sub.id, stage_code=2,
              title="整改材料", status="ACTIVE", version_count=0, created_at=now(), updated_at=now())
    iss = c.add(Issue, submission_id=sub.id, material_id=m.id, report_id=c.report.id, source="AI_RULE",
                category="FORMAT", severity="WARN", title="需补材料", description="补签字页",
                review_status="CONFIRMED", resolution="OPEN", is_active=True,
                created_at=now(), updated_at=now())
    c.db.flush()
    before = c.db.query(AuditLog).filter(AuditLog.action == "ISSUE_RESPONSE", AuditLog.object_id == str(iss.id)).count()
    response = as_client(c.student).post(
        f"/api/materials/{m.id}/versions",
        files={"file": ("b.pdf", b"%PDF-1.4\nprobe\n%%EOF", "application/pdf")},
        data={"issue_ids": str(iss.id), "change_note": "按整改补签字页"})
    assert response.status_code == 200, response.text
    version_id = response.json()["data"]["version"]["id"]
    assert iss.response_type == "MODIFIED" and iss.response_version_id == version_id
    events = c.db.query(AuditLog).filter(AuditLog.action == "ISSUE_RESPONSE", AuditLog.object_id == str(iss.id)).all()
    assert len(events) == before + 1
    assert events[-1].detail["version_id"] == version_id

    history = as_client(c.student).get(f"/api/archives/{c.arch.id}/history").json()["data"]
    replies = [item for item in history if item["kind"] == "ISSUE_RESPONSE" and item["issue_id"] == iss.id]
    assert replies and replies[0]["detail"] == "按整改补签字页"


def test_notice_export_filename_uses_anon_code_only(case, as_client):
    c = case
    fresh = c.add(Notice, notice_type="RECTIFICATION", submission_id=c.sub.id, archive_id=c.arch.id,
                  student_user_id=c.student.id, round_no=1, title="整改通知",
                  content={"student": {"name": "学生", "student_no": "2026001", "anon_code": "anon-77"},
                           "items": [], "intro": "请整改"},
                  status="SENT", created_by=c.reviewer.id, created_at=now(), updated_at=now())
    legacy = c.add(Notice, notice_type="RECTIFICATION", submission_id=c.sub.id, archive_id=c.arch.id,
                   student_user_id=c.student.id, round_no=2, title="整改通知",
                   content={"student": {"name": "学生", "student_no": "2026001"}, "items": [], "intro": "请整改"},
                   status="SENT", created_by=c.reviewer.id, created_at=now(), updated_at=now())
    c.db.flush()
    client = as_client(c.reviewer)
    for fmt in ("pdf", "docx"):
        disposition = client.get(f"/api/notices/{fresh.id}/export?format={fmt}").headers["content-disposition"]
        assert "anon-77" in disposition and "2026001" not in disposition
        legacy_disposition = client.get(f"/api/notices/{legacy.id}/export?format={fmt}").headers["content-disposition"]
        assert f"_{legacy.id}_" in legacy_disposition and "2026001" not in legacy_disposition
