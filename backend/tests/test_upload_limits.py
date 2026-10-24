import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from errors import AppError, forbidden
from routers import materials as router
from services import storage as store
from services import uploads

MB = 1024 * 1024


class TrackingUpload:
    """A large upload without allocating its whole contents for the test."""

    def __init__(self, size, filename="material.pdf", failure=None):
        self.remaining = size
        self.filename = filename
        self.read_sizes = []
        self.consumed = 0
        self.failure = failure
        # Client-provided metadata must never substitute for actual byte counting.
        self.size = 0

    async def read(self, size=-1):
        assert size > 0, "uploads must never use an unbounded read"
        self.read_sizes.append(size)
        if self.failure is not None and self.consumed:
            raise self.failure
        count = min(size, self.remaining)
        self.remaining -= count
        self.consumed += count
        return b"x" * count


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr(store, "ensure_storage", lambda: tmp_path)
    monkeypatch.setattr(uploads, "get_setting", lambda *_args: {"max_file_mb": 1, "max_zip_mb": 1})
    return tmp_path


@pytest.mark.parametrize("size", [MB - 1, MB])
def test_material_accepts_files_up_to_the_configured_limit(storage, size):
    file = TrackingUpload(size)
    assert len(asyncio.run(uploads.read_material_upload(None, file))) == size
    assert file.read_sizes == [MB + 1]
    assert not list(storage.iterdir())


def test_material_limit_rejects_after_only_limit_plus_one_bytes(storage):
    file = TrackingUpload(100 * MB)
    with pytest.raises(AppError) as error:
        asyncio.run(uploads.read_material_upload(None, file))
    assert error.value.status_code == 413
    assert file.consumed == MB + 1
    assert file.remaining > 0
    assert not list(storage.iterdir())


@pytest.mark.parametrize("initial", [True, False], ids=["initial-upload", "revision-upload"])
def test_both_material_routes_enforce_limits_before_creating_versions(storage, monkeypatch, initial):
    arch = SimpleNamespace(id=1, current_stage=1)
    sub = SimpleNamespace(id=2, status="DRAFT")
    material = SimpleNamespace(id=3, archive_id=1)
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = sub if initial else material
    monkeypatch.setattr(router, "ensure_archive_access", lambda *_args: arch)
    monkeypatch.setattr(router, "_editable_submission", lambda *_args: sub)
    create = Mock()
    revise = Mock()
    monkeypatch.setattr(router, "create_material_with_file", create)
    monkeypatch.setattr(router, "add_version", revise)
    actor = SimpleNamespace(id=1, role="STUDENT")
    file = TrackingUpload(100 * MB)
    with pytest.raises(AppError) as error:
        if initial:
            asyncio.run(router.upload_material(1, file, None, None, None, None, db, actor))
        else:
            asyncio.run(router.post_version(3, file, None, None, None, db, actor))
    assert error.value.status_code == 413
    assert file.consumed == MB + 1
    create.assert_not_called()
    revise.assert_not_called()


@pytest.mark.parametrize("size", [MB - 1, MB])
def test_zip_streams_to_random_path_without_using_the_supplied_filename(storage, size):
    file = TrackingUpload(size, "../../outside.zip/evil")
    rel = asyncio.run(uploads.save_zip_upload(None, file))
    path = storage / rel
    assert path.parent == storage / "tmp"
    assert path.suffix == ".zip" and "outside" not in path.name and "evil" not in path.name
    assert path.stat().st_size == size
    assert path.read_bytes() == b"x" * size
    assert max(file.read_sizes) <= MB


def test_zip_over_limit_stops_at_limit_plus_one_and_removes_partial_file(storage):
    file = TrackingUpload(100 * MB)
    with pytest.raises(AppError) as error:
        asyncio.run(uploads.save_zip_upload(None, file))
    assert error.value.status_code == 413
    assert file.consumed == MB + 1 and file.remaining > 0
    assert file.read_sizes == [MB, 1]
    assert not list((storage / "tmp").iterdir())


def test_zip_larger_than_one_chunk_still_uses_bounded_reads(storage, monkeypatch):
    monkeypatch.setattr(uploads, "get_setting", lambda *_args: {"max_zip_mb": 3})
    file = TrackingUpload(2 * MB + 17)
    rel = asyncio.run(uploads.save_zip_upload(None, file))
    assert (storage / rel).stat().st_size == 2 * MB + 17
    assert len(file.read_sizes) >= 3 and max(file.read_sizes) <= MB


@pytest.mark.parametrize("failure", [OSError("interrupted upload"), asyncio.CancelledError()])
def test_zip_read_error_or_cancellation_removes_partial_file(storage, failure):
    file = TrackingUpload(MB, failure=failure)
    with pytest.raises(type(failure)):
        asyncio.run(uploads.save_zip_upload(None, file))
    assert not list((storage / "tmp").iterdir())


def test_zip_write_error_removes_partial_file(storage, monkeypatch):
    async def fail_write(*_args):
        raise OSError("disk full")

    monkeypatch.setattr(uploads, "run_in_threadpool", fail_write)
    with pytest.raises(OSError, match="disk full"):
        asyncio.run(uploads.save_zip_upload(None, TrackingUpload(100)))
    assert not list((storage / "tmp").iterdir())


def test_zip_name_collision_never_removes_or_overwrites_an_existing_file(storage, monkeypatch):
    monkeypatch.setattr(uploads, "random_stored_name", lambda _ext: "existing.zip")
    path = storage / "tmp" / "existing.zip"
    path.parent.mkdir()
    path.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        asyncio.run(uploads.save_zip_upload(None, TrackingUpload(100)))
    assert path.read_bytes() == b"keep"


def test_zip_enqueue_failure_removes_successfully_uploaded_file(storage, monkeypatch):
    monkeypatch.setattr(router, "enqueue_job", Mock(side_effect=RuntimeError("database failure")))
    actor = SimpleNamespace(id=1, role="BRANCH_REVIEWER", org_id=1)
    with pytest.raises(RuntimeError, match="database failure"):
        asyncio.run(router.batch_upload(TrackingUpload(100), None, None, Mock(), actor))
    assert not list((storage / "tmp").iterdir())


def test_zip_success_keeps_worker_path_and_uploader_identity(storage, monkeypatch):
    enqueue = Mock(return_value=SimpleNamespace(id=42))
    monkeypatch.setattr(router, "enqueue_job", enqueue)
    actor = SimpleNamespace(id=5, role="BRANCH_REVIEWER", org_id=7)
    response = asyncio.run(router.batch_upload(TrackingUpload(100), "3", "2", Mock(), actor))
    assert response["data"]["job_id"] == 42
    params = enqueue.call_args.args[-1]
    assert params["batch_id"] == 3 and params["stage_code"] == 2
    assert params["actor_role"] == actor.role and params["actor_org_id"] == actor.org_id
    assert (storage / params["zip_path"]).stat().st_size == 100


@pytest.mark.parametrize("batch,stage", [("invalid", None), (None, "6")])
def test_invalid_zip_form_parameters_are_rejected_before_reading_or_creating_a_file(storage, batch, stage):
    file = TrackingUpload(100)
    actor = SimpleNamespace(id=1, role="BRANCH_REVIEWER", org_id=1)
    with pytest.raises(AppError) as error:
        asyncio.run(router.batch_upload(file, batch, stage, Mock(), actor))
    assert error.value.status_code == 422
    assert not file.read_sizes and not list(storage.iterdir())


@pytest.mark.parametrize("entry", ["initial", "revision", "zip"])
def test_permission_denied_never_reads_upload_or_writes_storage(storage, monkeypatch, entry):
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id=1, archive_id=1)
    monkeypatch.setattr(router, "ensure_archive_access", lambda *_args: SimpleNamespace(id=1))
    monkeypatch.setattr(router, "_editable_submission", Mock(side_effect=forbidden()))
    actor = SimpleNamespace(id=1, role="SYS_ADMIN")
    file = TrackingUpload(100)
    with pytest.raises(AppError) as error:
        if entry == "initial":
            asyncio.run(router.upload_material(1, file, None, None, None, None, db, actor))
        elif entry == "revision":
            asyncio.run(router.post_version(1, file, None, None, None, db, actor))
        else:
            asyncio.run(router.batch_upload(file, None, None, db, actor))
    assert error.value.status_code == 403
    assert not file.read_sizes
    assert not list(storage.iterdir())


@pytest.mark.parametrize("key,read", [
    ("max_file_mb", uploads.read_material_upload),
    ("max_zip_mb", uploads.save_zip_upload),
])
def test_negative_configuration_cannot_turn_a_bounded_read_into_an_unbounded_one(storage, monkeypatch, key, read):
    monkeypatch.setattr(uploads, "get_setting", lambda *_args: {key: -1})
    file = TrackingUpload(100)
    with pytest.raises(AppError) as error:
        asyncio.run(read(None, file))
    assert error.value.status_code == 413
    assert file.consumed == 1
    assert not list(storage.rglob("*.zip"))
