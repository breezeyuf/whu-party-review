from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock
import zipfile

from docx import Document
import pytest

from errors import AppError
from services import materials


@pytest.fixture(params=["initial", "revision"])
def upload(request, monkeypatch):
    sub = SimpleNamespace(id=10, status="DRAFT", stage_code=1)
    material = SimpleNamespace(id=20, submission_id=10, archive_id=1, version_count=1, current_version_id=30)
    actor = SimpleNamespace(id=1)
    db = Mock()
    query = db.query.return_value
    query.filter.return_value = query
    query.with_for_update.return_value = query
    query.populate_existing.return_value = query
    query.one.return_value = sub
    query.first.side_effect = [sub, material]
    next_id = iter(range(100, 200))
    db.add.side_effect = lambda obj: setattr(obj, "id", next(next_id))
    cfg = {"max_file_mb": 1, "allowed_ext": ["pdf", "docx"]}
    monkeypatch.setattr(materials, "get_setting", lambda *_args, **_kwargs: cfg)
    save = Mock(side_effect=lambda data, *_args: ("materials/1/file.bin", "test-sha", len(data)))
    monkeypatch.setattr(materials.store, "save_bytes", save)

    def run(filename, data):
        if request.param == "initial":
            return materials.create_material_with_file(db, SimpleNamespace(id=1), sub, actor, filename, data)
        return materials.add_version(db, material, actor, filename, data)

    return run, cfg, save, db, material


@pytest.mark.parametrize("filename,data,status", [
    ("photo.png", b"\x89PNG\r\n\x1a\nexample", 415),
    ("bad.pdf", b"not a pdf", 415),
    ("large.pdf", b"%PDF" + b"x" * (1024 * 1024), 413),
    ("empty.pdf", b"", 415),
], ids=["disallowed-format", "wrong-header", "over-size-limit", "empty-file"])
def test_invalid_or_disallowed_upload_never_writes_a_file_or_version(upload, filename, data, status):
    run, _, save, db, material = upload

    with pytest.raises(AppError) as error:
        run(filename, data)

    assert error.value.status_code == status
    save.assert_not_called()
    db.add.assert_not_called()
    assert material.version_count == 1 and material.current_version_id == 30


@pytest.mark.parametrize("valid_zip", [False, True])
def test_ordinary_zip_or_corrupt_package_cannot_be_uploaded_as_docx(upload, valid_zip):
    run, _, save, _, _ = upload
    buf = BytesIO()
    if valid_zip:
        with zipfile.ZipFile(buf, "w") as archive:
            archive.writestr("readme.txt", "this is not a DOCX")
        data = buf.getvalue()
    else:
        data = b"PKbroken-package"

    with pytest.raises(AppError) as error:
        run("pretend.docx", data)

    assert error.value.status_code == 415
    save.assert_not_called()


@pytest.mark.parametrize("kind", ["pdf", "docx"])
def test_allowed_pdf_and_real_docx_still_create_a_material_version(upload, kind):
    run, cfg, save, _, _ = upload
    cfg["allowed_ext"] = ["PDF", "DOCX"]
    if kind == "docx":
        doc = Document()
        doc.add_paragraph("虚构材料正文")
        buf = BytesIO()
        doc.save(buf)
        data = buf.getvalue()
    else:
        data = b"%PDF-1.7\nexample"

    run(f"material.{kind}", data)

    save.assert_called_once()
    assert save.call_args.args[0] == data
    assert save.call_args.args[2] == kind


def test_missing_settings_use_the_default_supported_formats(monkeypatch):
    monkeypatch.setattr(materials, "get_setting", lambda *_args: {})
    assert materials._validate_upload(None, "report.pdf", b"%PDF-1.7") == ("pdf", "application/pdf")
