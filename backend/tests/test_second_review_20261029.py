"""《GitHub 最新版本核查 2026-10-28》剩余缺陷的回归用例。

覆盖：时间轴越权旁路、档案批次迁移一致性、规则导入的枚举/结构校验、
敏感短语按 (phrase, category) 去重、手工建档匿名编号、上传自动回复说明。
"""
import json
from datetime import date
from io import BytesIO

from openpyxl import Workbook

from models import AuditLog, Issue, Material, MaterialVersion, SensitivePhrase, Submission, TimeNodeExtraction
from tests.test_review_regressions import case, test_engine, as_client, material, parsed_material, pair
from utils import now


def _extraction(c, m, version_id, raw_text, value_date=date(2026, 1, 5), node_code="T02"):
    row = c.add(TimeNodeExtraction, archive_id=c.arch.id, node_code=node_code, material_id=m.id,
                material_version_id=version_id, value_date=value_date, raw_text=raw_text,
                page_no=1, method="RULE", is_current=True, seq_index=0, created_at=now())
    c.db.flush()
    return row


def test_timeline_hides_material_sources_outside_submission_scope(case, as_client):
    """P1：档案时间轴不能绕过提交包权限吐出未分配批次材料的原文。"""
    c = case
    in_scope, in_scope_version = material(c)  # 属于 stage 1 / 批次 0，互查员有权限
    _extraction(c, in_scope, in_scope_version.id, "本批次材料原文")

    other_sub = c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.batches[1].id,
                      college_id=c.college.id, branch_id=c.branches[0].id, status="DRAFT",
                      ai_status="NONE", created_at=now(), updated_at=now())
    out_of_scope = c.add(Material, archive_id=c.arch.id, submission_id=other_sub.id, stage_code=2,
                         title="批次外材料", status="ACTIVE", created_at=now(), updated_at=now())
    out_version = c.add(MaterialVersion, material_id=out_of_scope.id, version_no=1,
                        original_filename="b.pdf", stored_path="x" * 8 + ".pdf", file_ext="pdf",
                        mime_type="application/pdf", file_size=10, sha256="1" * 64,
                        parse_status="DONE", uploaded_at=now())
    out_of_scope.current_version_id = out_version.id
    c.db.flush()
    _extraction(c, out_of_scope, out_version.id, "未分配批次的原文片段", value_date=date(2026, 2, 2))
    pair(c, batch=0)

    client = as_client(c.cross)
    assert client.get(f"/api/submissions/{other_sub.id}").status_code == 404
    timeline = client.get(f"/api/archives/{c.arch.id}/timeline")
    assert timeline.status_code == 200
    payload = timeline.json()["data"]
    assert "未分配批次的原文片段" not in json.dumps(payload, ensure_ascii=False)
    assert "批次外材料" not in json.dumps(payload, ensure_ascii=False)
    # 有权限的批次仍然照常展示，避免修复变成"一律看不见"
    assert "本批次材料原文" in json.dumps(payload, ensure_ascii=False)

    # 内部调用（不传 actor）保留全量：规则计算不因展示口径丢数据
    from services.timeline import timeline_view
    internal = timeline_view(c.db, c.arch)
    assert "未分配批次的原文片段" in json.dumps(internal, ensure_ascii=False)


def test_archive_batch_change_moves_active_submissions_only(case, as_client):
    """P2：档案改批次后活动提交包必须同步，已归档提交包保留历史归属。"""
    c = case
    filed = c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.batches[0].id,
                  college_id=c.college.id, branch_id=c.branches[0].id, status="FILED",
                  ai_status="DONE", created_at=now(), updated_at=now())
    c.db.flush()
    response = as_client(c.org).put(f"/api/archives/{c.arch.id}", json={"batch_id": c.batches[1].id})
    assert response.status_code == 200, response.text
    c.db.refresh(c.sub)
    c.db.refresh(filed)
    assert c.arch.batch_id == c.batches[1].id
    assert c.sub.batch_id == c.batches[1].id
    assert filed.batch_id == c.batches[0].id

    invalid = as_client(c.org).put(f"/api/archives/{c.arch.id}", json={"batch_id": 99999999})
    assert invalid.status_code == 422


def _terms_workbook(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["term_type", "standard_text", "wrong_variants", "severity"])
    for row in rows:
        ws.append(row)
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def test_rule_import_validates_enum_and_json_shape(case, as_client):
    """P2：预检与正式导入必须同一套字段口径，不能"预检通过、正式导入 500"。"""
    c = case
    client = as_client(c.org)
    bad_enum = client.post("/api/rules/terms/import",
                           files={"file": ("a.xlsx", _terms_workbook([["WRONG_TYPE", "测试术语甲", "[]", "WARN"]]))},
                           data={"mode": "upsert", "dry_run": "true"})
    assert bad_enum.status_code == 200
    assert bad_enum.json()["data"]["created"] == 0
    assert "term_type 取值无效" in bad_enum.json()["data"]["errors"][0]["message"]

    bad_shape = client.post("/api/rules/terms/import",
                            files={"file": ("b.xlsx", _terms_workbook([["VARIANT", "测试术语乙", "不是数组", "WARN"]]))},
                            data={"mode": "upsert", "dry_run": "true"})
    assert bad_shape.status_code == 200
    assert "wrong_variants 须为数组" in bad_shape.json()["data"]["errors"][0]["message"]

    blocked = client.post("/api/rules/terms/import",
                          files={"file": ("c.xlsx", _terms_workbook([["WRONG_TYPE", "测试术语丙", "[]", "WARN"]]))},
                          data={"mode": "upsert", "dry_run": "false"})
    assert blocked.status_code == 422
    assert c.db.query(__import__("models").PoliticalTerm).filter_by(standard_text="测试术语丙").count() == 0

    # 单条新增/更新与导入同口径
    created = client.post("/api/rules/terms", json={"standard_text": "测试术语丁", "term_type": "WRONG_TYPE"})
    assert created.status_code == 422
    ok_row = client.post("/api/rules/terms", json={"standard_text": "测试术语戊", "term_type": "SEQUENCE",
                                                   "wrong_variants": ["甲", "乙"]})
    assert ok_row.status_code == 200, ok_row.text
    assert client.put(f"/api/rules/terms/{ok_row.json()['data']['id']}",
                      json={"wrong_variants": "字符串"}).status_code == 422


def test_sensitive_phrase_export_can_be_imported_back(case, as_client):
    """P2：唯一键是 (phrase, category)，导出后应能原样导回。"""
    c = case
    for category in ("IDEOLOGY", "MOTIVATION"):
        c.add(SensitivePhrase, phrase="同一短语", match_type="KEYWORD", category=category,
              risk_level="MEDIUM", is_active=True, created_at=now(), updated_at=now())
    c.db.flush()
    client = as_client(c.org)
    exported = client.get("/api/rules/sensitive-phrases/export")
    assert exported.status_code == 200
    check = client.post("/api/rules/sensitive-phrases/import",
                        files={"file": ("p.xlsx", exported.content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                        data={"mode": "upsert", "dry_run": "true"})
    assert check.status_code == 200, check.text
    data = check.json()["data"]
    assert data["errors"] == []
    assert data["updated"] >= 2 and data["created"] == 0

    real = client.post("/api/rules/sensitive-phrases/import",
                       files={"file": ("p2.xlsx", exported.content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                       data={"mode": "upsert", "dry_run": "false"})
    assert real.status_code == 200, real.text
    assert c.db.query(SensitivePhrase).filter_by(phrase="同一短语").count() == 2


def test_manual_archive_generates_random_anon_code(case, as_client):
    """P2：手工建档的匿名编号不能包含学号。"""
    c = case
    response = as_client(c.org).post("/api/archives", json={
        "student": {"student_no": "2099999123456", "real_name": "匿名测试"},
        "branch_id": c.branches[0].id, "batch_id": c.batches[0].id,
    })
    assert response.status_code == 200, response.text
    anon = response.json()["data"]["archive"]["anon_code"]
    assert "2099999123456" not in anon
    assert anon.startswith("A") and len(anon) > 10


def test_upload_with_note_updates_current_response_text(case, as_client):
    """P2：上传自动回复要把新说明写进当前说明，不能只写审计。"""
    c = case
    sub = c.add(Submission, archive_id=c.arch.id, stage_code=2, batch_id=c.batches[0].id,
                college_id=c.college.id, branch_id=c.branches[0].id, status="DRAFT",
                ai_status="DONE", created_at=now(), updated_at=now())
    m = c.add(Material, archive_id=c.arch.id, submission_id=sub.id, stage_code=2,
              title="整改材料", status="ACTIVE", version_count=0, created_at=now(), updated_at=now())
    iss = c.add(Issue, submission_id=sub.id, material_id=m.id, report_id=c.report.id, source="AI_RULE",
                category="FORMAT", severity="WARN", title="需补材料", description="补签字页",
                review_status="CONFIRMED", resolution="OPEN", is_active=True,
                response_type="EXPLAINED", response_text="旧的情况说明", responded_at=now(),
                created_at=now(), updated_at=now())
    c.db.flush()

    response = as_client(c.student).post(
        f"/api/materials/{m.id}/versions",
        files={"file": ("c.pdf", b"%PDF-1.4\nprobe\n%%EOF", "application/pdf")},
        data={"issue_ids": str(iss.id), "change_note": "已按要求补签字页并重新扫描"})
    assert response.status_code == 200, response.text
    c.db.refresh(iss)
    assert iss.response_text == "已按要求补签字页并重新扫描"
    events = c.db.query(AuditLog).filter(AuditLog.action == "ISSUE_RESPONSE",
                                         AuditLog.object_id == str(iss.id)).all()
    assert events[-1].detail["response_text"] == iss.response_text
