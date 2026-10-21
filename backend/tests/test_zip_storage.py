import stat
import zipfile

import pytest

from services import storage as store


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr(store, "ensure_storage", lambda: tmp_path)
    return tmp_path


def make_zip(storage, entries):
    path = storage / "batch.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries:
            archive.writestr(name, content)
    return path


def test_same_filename_for_different_students_keeps_both_contents(storage):
    entries = [("D2026001/思想汇报.pdf", b"student-one"), ("D2026002/思想汇报.pdf", b"student-two")]
    make_zip(storage, entries)

    items = store.extract_zip_safe("batch.zip", "tmp/batch_1")

    assert len({item["temp_path"] for item in items}) == 2
    for item, (name, content) in zip(items, entries):
        assert item["entry_path"] == name
        assert store.read_bytes(item["temp_path"]) == content
        assert item["file_size"] == len(content)


def test_retry_never_overwrites_files_from_previous_extraction(storage):
    make_zip(storage, [("report.pdf", b"first-version")])
    first = store.extract_zip_safe("batch.zip", "tmp/task")[0]
    make_zip(storage, [("report.pdf", b"second-version")])
    second = store.extract_zip_safe("batch.zip", "tmp/task")[0]

    assert first["temp_path"] != second["temp_path"]
    assert store.read_bytes(first["temp_path"]) == b"first-version"
    assert store.read_bytes(second["temp_path"]) == b"second-version"


def test_storage_rejects_sibling_directory_with_same_name_prefix(storage):
    with pytest.raises(ValueError, match="invalid storage path"):
        store.abs_path(f"../{storage.name}-outside/file.pdf")


def test_zip_skips_absolute_traversal_and_windows_drive_entries(storage):
    make_zip(storage, [("../outside.pdf", b"bad"), ("C:/outside.pdf", b"bad"),
                       ("/outside.pdf", b"bad"), ("dir\\..\\outside.pdf", b"bad"),
                       ("student/report.pdf", b"good")])

    items = store.extract_zip_safe("batch.zip", "tmp/task")

    assert len(items) == 1 and items[0]["entry_path"] == "student/report.pdf"
    assert store.read_bytes(items[0]["temp_path"]) == b"good"


def test_zip_does_not_extract_symlinks(storage):
    info = zipfile.ZipInfo("link.pdf")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    make_zip(storage, [(info, b"../../outside")])
    assert store.extract_zip_safe("batch.zip", "tmp/task") == []


def test_zip_directory_entries_do_not_consume_file_limit(storage):
    make_zip(storage, [("one/", b""), ("two/", b""), ("one/report.pdf", b"good")])
    assert len(store.extract_zip_safe("batch.zip", "tmp/task", max_files=1)) == 1


@pytest.mark.parametrize("limits", [{"max_files": 1}, {"max_total": 5}])
def test_archive_limits_reject_before_writing_materials(storage, limits):
    make_zip(storage, [("one.pdf", b"1234"), ("two.pdf", b"5678")])
    with pytest.raises(ValueError):
        store.extract_zip_safe("batch.zip", "tmp/task", **limits)
    assert not list((storage / "tmp/task").iterdir())


def test_corrupt_zip_cleans_only_files_created_by_this_attempt(storage):
    path = make_zip(storage, [("one.pdf", b"first"), ("two.pdf", b"CORRUPTME")])
    path.write_bytes(path.read_bytes().replace(b"CORRUPTME", b"DIFFERENT"))
    dest = storage / "tmp/task"
    dest.mkdir(parents=True)
    existing = dest / "existing.pdf"
    existing.write_bytes(b"keep")

    with pytest.raises(zipfile.BadZipFile):
        store.extract_zip_safe("batch.zip", "tmp/task")

    assert list(dest.iterdir()) == [existing]
    assert existing.read_bytes() == b"keep"
