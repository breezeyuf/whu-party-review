"""Opt-in real CPU model + PostgreSQL upload/worker/API acceptance."""
import os
from io import BytesIO

import fitz
import pytest

from ai import ocr, parser
from models import Job, MaterialVersion, ParseResult
from tests.pg_fixtures import pg_schema, case, as_client, storage_tmp  # noqa: F401
from worker import _run

pytestmark = pytest.mark.skipif(os.environ.get("RUN_OCR_INTEGRATION") != "1", reason="Set RUN_OCR_INTEGRATION=1 for real OCR models")


@pytest.fixture(scope="module", autouse=True)
def stop_ocr():
    yield
    ocr.shutdown()


def sample(ext):
    with fitz.open() as doc:
        page = doc.new_page(width=595, height=300)
        page.insert_text((40, 65), "入党申请书 测试材料", fontname="china-s", fontsize=24)
        page.insert_text((40, 110), "OCR 20260001", fontsize=26)
        image = page.get_pixmap(dpi=150, alpha=False).tobytes("png")
    if ext == "pdf":
        with fitz.open() as scan:
            scan.new_page(width=595, height=300).insert_image(fitz.Rect(0, 0, 595, 300), stream=image)
            return scan.tobytes()
    if ext == "jpg":
        return fitz.Pixmap(image).tobytes("jpg", jpg_quality=90)
    return image


@pytest.mark.parametrize("ext", ["png", "jpg", "pdf"])
def test_upload_worker_persists_real_ocr_and_api_returns_text(case, as_client, storage_tmp, monkeypatch, ext):
    monkeypatch.setattr(parser, "STORAGE_DIR", storage_tmp)
    client = as_client(case.student)
    response = client.post(f"/api/archives/{case.arch_a.id}/materials", files={"file": (f"scan.{ext}", sample(ext))}, data={"stage_code": "2"})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    job = case.db.get(Job, data["parse_job_id"])
    job.attempts = 1
    _run(case.db, job)
    assert job.status == "SUCCEEDED", job.error
    version = case.db.get(MaterialVersion, data["version"]["id"])
    assert version.parse_status == "DONE"
    stored = case.db.query(ParseResult).filter(ParseResult.version_id == version.id).one()
    assert "20260001" in stored.full_text and "申请书" in stored.full_text
    assert stored.ocr_engine == "paddleocr" and stored.parser == "OCR"
    parsed = client.get(f'/api/materials/{data["material"]["id"]}/parsed').json()["data"]
    assert parsed["full_text"] == stored.full_text
    assert parsed["pages"] and parsed["pages"][0]["blocks"]
    for page in parsed["pages"]:
        for block in page["blocks"]:
            x0, y0, x1, y1 = block["bbox"]
            assert 0 <= x0 < x1 <= page["width"] + 1
            assert 0 <= y0 < y1 <= page["height"] + 1


def test_failed_ocr_is_saved_as_failure_and_can_be_retried(case, as_client, storage_tmp, monkeypatch):
    monkeypatch.setattr(parser, "STORAGE_DIR", storage_tmp)
    client = as_client(case.student)
    response = client.post(f"/api/archives/{case.arch_a.id}/materials", files={"file": ("scan.png", sample("png"))}, data={"stage_code": "2"})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    job = case.db.get(Job, data["parse_job_id"])
    job.attempts = job.max_attempts or 3
    with monkeypatch.context() as failure:
        failure.setattr(ocr, "ocr_pixmap", lambda _: ("", [], None, "OCR 测试故障"))
        _run(case.db, job)
    assert job.status == "FAILED"
    version = case.db.get(MaterialVersion, data["version"]["id"])
    assert version.parse_status == "FAILED"
    assert case.db.query(ParseResult).filter(ParseResult.version_id == version.id).one().warnings
    mid = data["material"]["id"]
    response = client.post(f"/api/materials/{mid}/retry-parse")
    assert response.status_code == 200, response.text
    jid = response.json()["data"]["parse_job_id"]
    assert client.post(f"/api/materials/{mid}/retry-parse").json()["data"]["parse_job_id"] == jid
    retry = case.db.get(Job, jid)
    retry.attempts = 1
    _run(case.db, retry)
    assert retry.status == "SUCCEEDED" and version.parse_status == "DONE"
    assert "20260001" in client.get(f"/api/materials/{mid}/parsed").json()["data"]["full_text"]
    assert case.db.query(ParseResult).filter(ParseResult.version_id == version.id).count() == 1


def test_retry_rejects_other_student_frozen_and_reviewing_material(case, as_client, storage_tmp, monkeypatch):
    monkeypatch.setattr(parser, "STORAGE_DIR", storage_tmp)
    client = as_client(case.student)
    response = client.post(f"/api/archives/{case.arch_a.id}/materials", files={"file": ("scan.png", sample("png"))}, data={"stage_code": "2"})
    data = response.json()["data"]
    job = case.db.get(Job, data["parse_job_id"])
    job.status = "FAILED"
    version = case.db.get(MaterialVersion, data["version"]["id"])
    version.parse_status = "FAILED"
    case.db.flush()
    url = f'/api/materials/{data["material"]["id"]}/retry-parse'
    assert as_client(case.student_b).post(url).status_code in (403, 404)
    client = as_client(case.student)
    version.is_frozen = True
    case.db.flush()
    assert client.post(url).status_code == 409
    version.is_frozen = False
    case.sub_draft.status = "BRANCH_REVIEW"
    case.db.flush()
    assert client.post(url).status_code == 403
