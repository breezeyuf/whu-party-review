"""Migration regressions run only in disposable schemas on TEST_DATABASE_URL."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import os
from pathlib import Path
import re
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

import migrations
from migrations import Migration, MigrationError, apply_migrations, load_migrations


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def schema_factory():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required; migration tests never use the application database")
    admin = create_engine(url, connect_args={"connect_timeout": 5})
    created = []

    def create(*, autocommit=False):
        name = "migration_test_" + uuid4().hex
        with admin.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{name}"'))
        engine = create_engine(
            url, connect_args={"connect_timeout": 5, "options": f"-csearch_path={name},public"},
            **({"isolation_level": "AUTOCOMMIT"} if autocommit else {}),
        )
        result = SimpleNamespace(name=name, engine=engine)
        created.append(result)
        return result

    try:
        yield create
    finally:
        for item in reversed(created):
            item.engine.dispose()
            with admin.begin() as conn:
                conn.execute(text(f'DROP SCHEMA "{item.name}" CASCADE'))
        admin.dispose()


@pytest.fixture
def empty_schema(schema_factory):
    return schema_factory()


def execute(engine, sql):
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cursor:
            cursor.execute(sql)
        raw.commit()
    finally:
        raw.close()


def ledger(engine):
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT version, name, checksum, adopted, applied_at FROM schema_migrations ORDER BY version"
        )).all()


def tables(schema):
    with schema.engine.connect() as conn:
        return set(conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = :schema"
        ), {"schema": schema.name}).scalars())


def table_rows(engine, names):
    with engine.connect() as conn:
        return {name: conn.execute(text(
            f'SELECT to_jsonb(t) FROM "{name}" t ORDER BY to_jsonb(t)::text'
        )).scalars().all() for name in names}


def trigger_ids(schema):
    with schema.engine.connect() as conn:
        return conn.execute(text(
            "SELECT t.tgname, t.oid FROM pg_trigger t "
            "JOIN pg_class c ON c.oid = t.tgrelid "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = :schema ORDER BY t.tgname, t.oid"
        ), {"schema": schema.name}).all()


def test_migration_files_are_contiguous_and_have_stable_checksums():
    records = load_migrations()
    assert [record.version for record in records] == [1, 2, 3, 4, 5, 6]
    assert all(len(record.checksum) == 64 for record in records)
    assert replace(records[0], sql=records[0].sql.replace("\n", "\r\n")).checksum == records[0].checksum
    assert replace(records[0], sql=records[0].sql + "\n-- edited history\n").checksum != records[0].checksum


def test_empty_database_bootstraps_once_and_restarts_without_replaying_ddl(empty_schema):
    assert apply_migrations(empty_schema.engine) == [1, 2, 3, 4, 5, 6]
    before = ledger(empty_schema.engine)
    triggers = trigger_ids(empty_schema)
    assert all(not row.adopted for row in before)
    assert {"users", "handover_records", "import_password_files", "schema_migrations"} <= tables(empty_schema)
    assert apply_migrations(empty_schema.engine) == []
    assert ledger(empty_schema.engine) == before
    assert trigger_ids(empty_schema) == triggers
    with empty_schema.engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM stages")).scalar_one() == 5
        assert conn.execute(text("SELECT count(*) FROM system_settings")).scalar_one() == 8


@pytest.mark.parametrize("with_handover", [False, True])
def test_adopts_existing_legacy_without_rewriting_business_rows_or_triggers(empty_schema, with_handover):
    from database import _HANDOVER_PATCH

    execute(empty_schema.engine, load_migrations()[0].sql)
    if with_handover:
        execute(empty_schema.engine, _HANDOVER_PATCH)
    execute(empty_schema.engine, """
        INSERT INTO orgs (org_type, name) VALUES ('SCHOOL', '已有学校');
        INSERT INTO users (username, password_hash, real_name)
            VALUES ('existing-user', 'unchanged-existing-hash', '已有用户');
        UPDATE system_settings SET value = '{"custom": true}'::jsonb WHERE key = 'ai';
        INSERT INTO audit_logs (action, detail) VALUES ('MIGRATION_TEST', '{"keep": true}');
        CREATE TABLE custom_data (note TEXT);
        INSERT INTO custom_data VALUES ('保留自定义表');
    """)
    names = tables(empty_schema)
    before = table_rows(empty_schema.engine, names)
    triggers = trigger_ids(empty_schema)

    assert apply_migrations(empty_schema.engine) == [1, 2, 3, 4, 5, 6]

    assert ledger(empty_schema.engine)[0].adopted is True
    assert all(not row.adopted for row in ledger(empty_schema.engine)[1:])
    assert table_rows(empty_schema.engine, names) == before
    assert set(triggers) <= set(trigger_ids(empty_schema))
    assert "import_password_files" in tables(empty_schema)


def _restore_demo_dump_in_schema(schema):
    # The checked-in pg_dump is trusted fixture data. Never execute it in public:
    # rewrite SQL identifiers only, while streaming COPY data verbatim.
    dump = (ROOT.parent / "database" / "party_review_20261017.sql").read_text(encoding="utf-8")
    dump = re.sub(r"(?m)^\\(?:un)?restrict[^\n]*\n?", "", dump)

    def scoped(sql):
        return sql.replace("public.", f'"{schema.name}".').replace(
            "set_config('search_path', '', false)",
            f"set_config('search_path', '{schema.name}', false)",
        )

    raw = schema.engine.raw_connection()
    try:
        with raw.cursor() as cursor:
            offset = 0
            for match in re.finditer(r"(?m)^(COPY public\.\w+ [^\n]+ FROM stdin;)\n(.*?)^\\\.\n", dump, re.S):
                cursor.execute(scoped(dump[offset:match.start()]))
                with cursor.copy(scoped(match.group(1))) as copy:
                    copy.write(match.group(2))
                offset = match.end()
            cursor.execute(scoped(dump[offset:]))
        raw.commit()
    finally:
        raw.close()


def test_adopts_actual_public_demo_dump_without_changing_restored_data(empty_schema):
    _restore_demo_dump_in_schema(empty_schema)
    names = tables(empty_schema)
    before = table_rows(empty_schema.engine, names)
    assert before["archives"] and before["users"] and before["ai_reports"]
    triggers = trigger_ids(empty_schema)

    apply_migrations(empty_schema.engine)

    assert ledger(empty_schema.engine)[0].adopted is True
    assert table_rows(empty_schema.engine, names) == before
    assert set(triggers) <= set(trigger_ids(empty_schema))
    assert "import_password_files" in tables(empty_schema)


@pytest.mark.parametrize("bad_kind", ["unrelated", "missing_column", "unknown_version"])
def test_unknown_or_incomplete_legacy_is_rejected_without_leaving_a_ledger(empty_schema, bad_kind):
    if bad_kind == "unrelated":
        execute(empty_schema.engine, "CREATE TABLE unrelated (id INTEGER)")
    else:
        execute(empty_schema.engine, load_migrations()[0].sql)
        if bad_kind == "missing_column":
            execute(empty_schema.engine, "ALTER TABLE users DROP COLUMN phone_masked")
        else:
            execute(empty_schema.engine, "UPDATE schema_meta SET value = '999' WHERE key = 'schema_version'")
    before = tables(empty_schema)

    with pytest.raises(MigrationError):
        apply_migrations(empty_schema.engine)

    assert tables(empty_schema) == before
    assert "schema_migrations" not in tables(empty_schema)


def test_checksum_drift_is_rejected_before_any_pending_migration(empty_schema, monkeypatch):
    records = load_migrations()
    apply_migrations(empty_schema.engine)
    before = ledger(empty_schema.engine)
    edited = [replace(records[0], sql=records[0].sql + "\n-- changed\n")] + records[1:]
    edited.append(Migration(7, "0007_must_not_run.sql", "CREATE TABLE must_not_run (id INTEGER)"))
    monkeypatch.setattr(migrations, "load_migrations", lambda _: edited)

    with pytest.raises(MigrationError, match="checksum"):
        apply_migrations(empty_schema.engine)

    assert ledger(empty_schema.engine) == before
    assert "must_not_run" not in tables(empty_schema)


@pytest.mark.parametrize("corruption", ["gap", "future"])
def test_record_gaps_and_newer_database_versions_are_rejected(empty_schema, corruption):
    apply_migrations(empty_schema.engine)
    if corruption == "gap":
        execute(empty_schema.engine, "DELETE FROM schema_migrations WHERE version = 2")
    else:
        execute(empty_schema.engine, """
            INSERT INTO schema_migrations (version, name, checksum)
                VALUES (7, '0007_future.sql', repeat('a', 64))
        """)
    before = ledger(empty_schema.engine)

    with pytest.raises(MigrationError, match="断档或版本高于"):
        apply_migrations(empty_schema.engine)

    assert ledger(empty_schema.engine) == before


@pytest.mark.parametrize("initial", [True, False])
def test_failed_batch_rolls_back_every_ddl_and_ledger_entry(empty_schema, monkeypatch, initial):
    records = load_migrations()
    if not initial:
        apply_migrations(empty_schema.engine)
    before = ledger(empty_schema.engine) if not initial else []
    before_tables = tables(empty_schema)
    records += [
        Migration(7, "0007_pending.sql", "CREATE TABLE pending_table (id INTEGER)"),
        Migration(8, "0008_failure.sql", "CREATE TABLE partial_table (id INTEGER); SELECT 1 / 0"),
    ]
    monkeypatch.setattr(migrations, "load_migrations", lambda _: records)

    with pytest.raises(MigrationError, match="0008.*回滚"):
        apply_migrations(empty_schema.engine)

    assert tables(empty_schema) == before_tables
    if not initial:
        assert ledger(empty_schema.engine) == before


def test_autocommit_engine_still_uses_one_atomic_migration_transaction(schema_factory, monkeypatch):
    schema = schema_factory(autocommit=True)
    records = load_migrations() + [
        Migration(7, "0007_failure.sql", "CREATE TABLE partial_table (id INTEGER); SELECT 1 / 0"),
    ]
    monkeypatch.setattr(migrations, "load_migrations", lambda _: records)

    with pytest.raises(MigrationError, match="0007.*回滚"):
        apply_migrations(schema.engine)

    assert tables(schema) == set()
    raw = schema.engine.raw_connection()
    try:
        assert raw.driver_connection.autocommit is True
    finally:
        raw.close()


@pytest.mark.parametrize("initial", [True, False])
def test_parallel_startups_are_serialized_and_apply_each_version_once(empty_schema, monkeypatch, initial):
    records = load_migrations()
    if not initial:
        apply_migrations(empty_schema.engine)
    records.append(Migration(
        7, "0007_parallel.sql", "SELECT pg_sleep(0.2); CREATE TABLE parallel_marker (id INTEGER)",
    ))
    monkeypatch.setattr(migrations, "load_migrations", lambda _: records)
    start = Barrier(2)

    def run():
        start.wait(timeout=10)
        return apply_migrations(empty_schema.engine)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run) for _ in range(2)]
        results = [future.result(timeout=30) for future in futures]

    assert sorted(results, key=len) == [[], [1, 2, 3, 4, 5, 6, 7] if initial else [7]]
    assert [row.version for row in ledger(empty_schema.engine)] == [1, 2, 3, 4, 5, 6, 7]


def test_legacy_foreign_key_repair_ignores_same_named_constraints_in_other_schemas(schema_factory):
    other = schema_factory()
    target = schema_factory()
    apply_migrations(other.engine)
    execute(target.engine, load_migrations()[0].sql)
    execute(target.engine, """
        ALTER TABLE submissions DROP CONSTRAINT fk_submissions_latest_report;
        ALTER TABLE submissions DROP CONSTRAINT fk_submissions_ai_job;
        ALTER TABLE materials DROP CONSTRAINT fk_materials_current_version;
    """)

    apply_migrations(target.engine)

    with target.engine.connect() as conn:
        names = conn.execute(text(
            "SELECT conname FROM pg_constraint WHERE connamespace = CAST(:schema AS regnamespace) "
            "AND conname IN ('fk_submissions_latest_report', 'fk_submissions_ai_job', 'fk_materials_current_version')"
        ), {"schema": target.name}).scalars().all()
    assert len(names) == 3
