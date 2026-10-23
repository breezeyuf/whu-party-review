from pathlib import Path
import socket
import zipfile

import pytest

from desktop.build import extract_postgres
from desktop.runtime import AlreadyRunning, Runtime, bind_local, postgres_runtime, read_config


def test_private_credentials_persist_and_differ_between_workspaces(tmp_path):
    first = read_config(tmp_path / "first.json")
    assert read_config(tmp_path / "first.json") == first
    second = read_config(tmp_path / "second.json")
    assert first["db_password"] != second["db_password"]
    assert first["app_secret"] != second["app_secret"]
    assert len(first["admin_password"]) >= 12


def test_broken_config_never_silently_reinitializes_keys(tmp_path):
    config = tmp_path / "config.json"
    original = '{"app_secret":"existing"}'
    config.write_text(original)
    with pytest.raises(RuntimeError, match="配置不完整"):
        read_config(config)
    assert config.read_text() == original


def test_occupied_port_uses_another_loopback_port():
    with bind_local() as first:
        with bind_local(first.getsockname()[1]) as second:
            assert first.getsockname()[1] != second.getsockname()[1]
            assert second.getsockname()[0] == "127.0.0.1"


def test_second_instance_cannot_lock_or_remove_active_status(tmp_path):
    first, second = Runtime(tmp_path), Runtime(tmp_path)
    first._lock()
    first.ready_file.write_text("active")
    try:
        with pytest.raises(AlreadyRunning): second._lock()
        second.stop()
        assert first.ready_file.read_text() == "active"
    finally: first.stop()
    assert not first.ready_file.exists()
    second._lock(); second.stop()


def test_english_distribution_path_required_without_cache_side_effects():
    assert postgres_runtime(Path("C:/PartyReview/runtime")) == Path("C:/PartyReview/runtime")
    with pytest.raises(RuntimeError, match="全英文路径"):
        postgres_runtime(Path("C:/中文/PartyReview/runtime"))


def test_postgres_extract_excludes_admin_tools_and_preserves_licenses(tmp_path):
    archive = tmp_path / "pg.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("pgsql/bin/postgres.exe", b"test binary")
        z.writestr("pgsql/server_license.txt", "license")
        z.writestr("pgsql/pgAdmin 4/admin.exe", b"not used")
    extract_postgres(archive, tmp_path / "runtime")
    assert (tmp_path / "runtime/bin/postgres.exe").exists()
    assert (tmp_path / "runtime/server_license.txt").read_text() == "license"
    assert not (tmp_path / "runtime/pgAdmin 4").exists()


def test_postgres_extract_rejects_parent_traversal(tmp_path):
    archive = tmp_path / "pg.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("pgsql/bin/../../../escape.exe", b"bad")
    with pytest.raises(ValueError, match="Unsafe archive path"):
        extract_postgres(archive, tmp_path / "runtime")
    assert not (tmp_path / "escape.exe").exists()
