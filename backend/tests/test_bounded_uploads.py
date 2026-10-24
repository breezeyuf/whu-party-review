import asyncio
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest

from errors import AppError
from routers import materials
from services import storage, uploads


class Stream:
    def __init__(self, data, *, failure=None):
        self.data = data
        self.filename = "upload.zip"
        self.size = 0  # Deliberately misleading metadata must not bypass limits.
        self.offset = 0
        self.read_sizes = []
        self.failure = failure

    async def read(self, size=-1):
        assert 0 < size <= uploads.CHUNK_SIZE, "unbounded upload read"
        self.read_sizes.append(size)
        if self.failure and self.offset:
            raise self.failure
        chunk = self.data[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr(storage, "ensure_storage", lambda: tmp_path)
    return tmp_path


@pytest.mark.parametrize("size", [0, 7, 8])
def test_read_upload_accepts_empty_under_limit_and_exact_limit(size):
    file = Stream(b"x" * size)
    assert asyncio.run(uploads.read_upload(file, 8, "too large")) == file.data


@pytest.mark.parametrize("save", [False, True])
def test_overflow_reads_only_limit_plus_one_byte(root, save):
    limit = uploads.CHUNK_SIZE + 5
    file = Stream(b"x" * (limit + 100))
    operation = uploads.save_upload_tmp if save else uploads.read_upload
    with pytest.raises(AppError) as error:
        asyncio.run(operation(file, limit, "too large"))
    assert error.value.status_code == 413
    assert file.offset == limit + 1
    assert not list(root.rglob("*.zip"))


def test_streamed_zip_matches_input_at_exact_limit(root):
    file = Stream(b"PK" + b"x" * (uploads.CHUNK_SIZE + 7))
    rel = asyncio.run(uploads.save_upload_tmp(file, len(file.data), "too large"))
    assert (root / rel).read_bytes() == file.data
    assert len(file.read_sizes) >= 3


@pytest.mark.parametrize("failure", [OSError("read failed"), asyncio.CancelledError()])
def test_failed_or_cancelled_read_removes_only_partial_upload(root, failure):
    existing = root / "keep.zip"
    existing.write_bytes(b"keep")
    file = Stream(b"x" * (uploads.CHUNK_SIZE + 10), failure=failure)
    with pytest.raises(type(failure)):
        asyncio.run(uploads.save_upload_tmp(file, len(file.data), "too large"))
    assert [p for p in root.rglob("*.zip")] == [existing]
    assert existing.read_bytes() == b"keep"


def test_filename_collision_never_deletes_existing_upload(root, monkeypatch):
    (root / "tmp").mkdir()
    existing = root / "tmp" / "existing.zip"
    existing.write_bytes(b"keep")
    monkeypatch.setattr(uploads, "random_stored_name", lambda _: "existing.zip")
    with pytest.raises(FileExistsError):
        asyncio.run(uploads.save_upload_tmp(Stream(b"new"), 10, "too large"))
    assert existing.read_bytes() == b"keep"


@pytest.fixture
def endpoints(monkeypatch, root):
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = NS(id=1, archive_id=1, status="DRAFT")
    actor = NS(id=5, role="BRANCH_REVIEWER", org_id=2)
    monkeypatch.setattr(materials, "ensure_archive_access", lambda *a: NS(id=1, current_stage=1))
    monkeypatch.setattr(materials, "_editable_submission", lambda *a: None)
    monkeypatch.setattr(materials, "get_setting", lambda *a: {"max_file_mb": 1, "max_zip_mb": 1})
    create = Mock(return_value=(NS(id=1), NS(id=2), NS(id=3)))
    version = Mock(return_value=(NS(id=2), NS(id=3), []))
    job = Mock(return_value=NS(id=3))
    monkeypatch.setattr(materials, "create_material_with_file", create)
    monkeypatch.setattr(materials, "add_version", version)
    monkeypatch.setattr(materials, "enqueue_job", job)
    monkeypatch.setattr(materials, "_material_dict", lambda *a: {})
    monkeypatch.setattr(materials, "_ver_brief", lambda *a: {})
    monkeypatch.setattr(materials, "log", lambda *a: None)

    def run(kind, file):
        if kind == "initial":
            return asyncio.run(materials.upload_material(1, file, None, None, None, None, db, actor))
        if kind == "revision":
            return asyncio.run(materials.post_version(1, file, None, None, None, db, actor))
        return asyncio.run(materials.batch_upload(file, None, None, db, actor))

    return run, create, version, job


@pytest.mark.parametrize("kind", ["initial", "revision", "zip"])
def test_all_material_routes_reject_oversize_before_creating_records(endpoints, root, kind):
    run, create, version, job = endpoints
    file = Stream(b"x" * (uploads.CHUNK_SIZE + 100))
    with pytest.raises(AppError) as error:
        run(kind, file)
    assert error.value.status_code == 413
    assert file.offset == uploads.CHUNK_SIZE + 1
    for operation in (create, version, job):
        operation.assert_not_called()
    assert not list(root.rglob("*.zip"))


@pytest.mark.parametrize("kind", ["initial", "revision", "zip"])
def test_all_material_routes_keep_exact_limit_uploads(endpoints, root, kind):
    run, create, version, job = endpoints
    data = b"x" * uploads.CHUNK_SIZE
    run(kind, Stream(data))
    if kind == "initial":
        assert create.call_args.args[5] == data
    elif kind == "revision":
        assert version.call_args.args[4] == data
    else:
        params = job.call_args.args[5]
        assert (root / params["zip_path"]).read_bytes() == data
        assert params["actor_role"] == "BRANCH_REVIEWER" and params["actor_org_id"] == 2


def test_zip_job_failure_cleans_up_completed_temporary_file(endpoints, root):
    run, _, _, job = endpoints
    job.side_effect = RuntimeError("database unavailable")
    with pytest.raises(RuntimeError):
        run("zip", Stream(b"PK-small"))
    assert not list(root.rglob("*.zip"))
