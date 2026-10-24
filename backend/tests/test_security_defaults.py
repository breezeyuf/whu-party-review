"""Public deployment defaults and demo restore credentials; no live DB required."""
from datetime import datetime, timezone
from pathlib import Path
import re
import runpy
from types import SimpleNamespace
from unittest.mock import Mock

import dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from models import Org, User
from security import verify_password
import seed_rules
from services.frontend import mount_frontend


@pytest.mark.parametrize("value,expected", [(None, False), ("0", False), ("false", False), ("1", True)])
def test_demo_hints_require_explicit_opt_in(monkeypatch, value, expected):
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **kw: None)
    monkeypatch.delenv("DEMO_LOGIN_HINT", raising=False)
    if value is not None:
        monkeypatch.setenv("DEMO_LOGIN_HINT", value)
    config = runpy.run_path(str(Path(__file__).parents[1] / "config.py"))
    assert config["DEMO_LOGIN_HINT"] is expected


@pytest.mark.parametrize("partial_dist", [False, True])
def test_unbuilt_frontend_exposes_no_source_files(tmp_path, partial_dist):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.jsx").write_text("private-source", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"private":true}', encoding="utf-8")
    (tmp_path / "index.html").write_text("development-index", encoding="utf-8")
    if partial_dist:
        (tmp_path / "dist").mkdir()
        (tmp_path / "dist" / "partial.js").write_text("incomplete-build", encoding="utf-8")
    app = FastAPI()

    @app.get("/api/health")
    def health():
        return {"ok": True}

    mount_frontend(app, tmp_path)
    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"ok": True}
        for path in ("/", "/index.html", "/src/app.jsx", "/package.json", "/partial.js"):
            assert client.get(path).status_code == 404


def test_built_frontend_preserves_spa_routing_without_source_fallback(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("production-index", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("production-js", encoding="utf-8")
    (tmp_path / "package.json").write_text("source-package", encoding="utf-8")
    app = FastAPI()
    mount_frontend(app, tmp_path)
    with TestClient(app) as client:
        for path in ("/", "/archives/123"):
            response = client.get(path)
            assert response.status_code == 200 and response.text == "production-index"
        assert client.get("/assets/app.js").text == "production-js"
        for path in ("/package.json", "/api/missing", "/assets/missing", "/storage/missing"):
            assert client.get(path).status_code == 404


def dump_admin():
    text = (Path(__file__).parents[2] / "database" / "party_review_20261017.sql").read_text(encoding="utf-8")
    block = re.search(r"COPY public\.users \(([^\n]+)\) FROM stdin;\n(.*?)\n\\\.", text, re.S)
    assert block is not None
    columns = block[1].split(", ")
    rows = [dict(zip(columns, line.split("\t"), strict=True)) for line in block[2].splitlines()]
    admins = [row for row in rows if row["username"] == "admin"]
    assert len(admins) == 1
    return admins[0]


def test_public_dump_admin_cannot_authenticate_before_reinitialization():
    row = dump_admin()
    assert row["password_hash"] == seed_rules.RESTORE_PASSWORD_MARKER
    assert row["is_active"] == "f" and row["must_change_password"] == "t"
    assert not verify_password("Demo@2026", row["password_hash"])
    assert not verify_password(seed_rules.RESTORE_PASSWORD_MARKER, row["password_hash"])


def admin_db(password_hash):
    user = SimpleNamespace(
        id=1, password_hash=password_hash, is_active=False, must_change_password=False,
        token_version=7, failed_login_count=5, locked_until=datetime.now(timezone.utc),
    )
    db = Mock()
    queries = {Org: Mock(), User: Mock()}
    queries[Org].filter.return_value.first.return_value = SimpleNamespace(id=1)
    queries[User].filter.return_value.first.return_value = user
    db.query.side_effect = lambda entity: queries[entity]
    return db, user


@pytest.mark.parametrize("configured_password", ["", "NewRestorePassword9!"])
def test_restored_admin_gets_new_password_and_old_tokens_are_revoked(monkeypatch, configured_password):
    db, user = admin_db(dump_admin()["password_hash"])
    monkeypatch.setattr(seed_rules, "ADMIN_PASSWORD", configured_password)
    printed = seed_rules.ensure_admin(db)
    password = configured_password or printed
    assert password and verify_password(password, user.password_hash)
    assert printed is None if configured_password else printed is not None
    assert user.is_active and user.must_change_password
    assert user.token_version == 8 and user.failed_login_count == 0 and user.locked_until is None
    assert user.id == 1
    db.add.assert_not_called()  # Keep existing identity and role/foreign-key links.
    saved = user.password_hash
    assert seed_rules.ensure_admin(db) is None
    assert user.password_hash == saved and user.token_version == 8


def test_existing_admin_is_not_reset_or_reactivated(monkeypatch):
    db, user = admin_db("existing-hash")
    monkeypatch.setattr(seed_rules, "ADMIN_PASSWORD", "ChangedEnvironmentPassword9!")
    assert seed_rules.ensure_admin(db) is None
    assert user.password_hash == "existing-hash"
    assert not user.is_active and user.token_version == 7
    db.flush.assert_not_called()


@pytest.mark.parametrize("active", [False, True])
def test_historically_public_admin_hash_is_rotated_without_reactivation(monkeypatch, active):
    db, user = admin_db("synthetic-historical-hash")
    user.is_active = active
    # Supply a synthetic digest result rather than putting the old bcrypt hash
    # back in a public regression fixture.
    monkeypatch.setattr(seed_rules, "sha256", lambda _: SimpleNamespace(
        hexdigest=lambda: "2baa999db1fb9db82bfc5798d798723b01686c7038ba9c8fc392e1ad16270346"))
    monkeypatch.setattr(seed_rules, "ADMIN_PASSWORD", "ReplacementPassword9!")
    assert seed_rules.ensure_admin(db) is None
    assert verify_password("ReplacementPassword9!", user.password_hash)
    assert user.is_active is active
    assert user.must_change_password and user.token_version == 8
