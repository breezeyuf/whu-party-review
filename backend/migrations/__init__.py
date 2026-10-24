"""Transactional PostgreSQL migrations; never replay the mutable schema.sql at startup."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from ._legacy import LEGACY_COLUMNS


class MigrationError(RuntimeError):
    """The database or the shipped migration history needs operator attention."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sql: str

    @property
    def checksum(self) -> str:
        # read_text normalizes CRLF; Windows and Unix checkouts have the same hash.
        return sha256(self.sql.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _sql_directory() -> Path:
    from config import BACKEND_DIR

    candidates = [BACKEND_DIR / "migrations" / "sql", Path(__file__).resolve().parent / "sql"]
    for path in candidates:
        if path.is_dir():
            return path
    raise MigrationError("数据库迁移 SQL 资源缺失，请检查安装包中的 migrations/sql 目录")


def load_migrations(sql_dir: Path | None = None) -> list[Migration]:
    directory = Path(sql_dir) if sql_dir is not None else _sql_directory()
    migrations = []
    for path in sorted(directory.glob("*.sql")):
        match = re.fullmatch(r"([0-9]{4})_([a-z0-9_]+)\.sql", path.name)
        if not match:
            raise MigrationError(f"数据库迁移文件名无效：{path.name}")
        sql = path.read_text(encoding="utf-8")
        if not sql.strip():
            raise MigrationError(f"数据库迁移文件为空：{path.name}")
        migrations.append(Migration(int(match.group(1)), path.name, sql))
    if not migrations or [m.version for m in migrations] != list(range(1, len(migrations) + 1)):
        raise MigrationError("数据库迁移文件必须从 0001 开始连续编号，且不能重复或缺失")
    return migrations


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _relations(cursor, schema: str) -> dict[str, str]:
    cursor.execute(
        "SELECT c.relname, c.relkind FROM pg_catalog.pg_class c "
        "JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = %s AND c.relkind IN ('r', 'p', 'v', 'm', 'f')",
        (schema,),
    )
    return dict(cursor.fetchall())


def _validate_legacy(cursor, schema: str, relations: dict[str, str]) -> None:
    """Adopt only the known legacy structure, without replaying its DDL or defaults."""
    missing_tables = sorted(name for name in LEGACY_COLUMNS if relations.get(name) not in ("r", "p"))
    if missing_tables:
        raise MigrationError("现有数据库不是完整的旧版结构，缺少表：" + ", ".join(missing_tables))
    cursor.execute("SELECT value FROM schema_meta WHERE key = 'schema_version'")
    row = cursor.fetchone()
    if not row or row[0] != "1":
        raise MigrationError("只支持接管 schema_meta.schema_version=1 的旧数据库，请先核对备份和数据库版本")
    cursor.execute(
        "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = %s",
        (schema,),
    )
    actual: dict[str, set[str]] = {}
    for table, column in cursor.fetchall():
        actual.setdefault(table, set()).add(column)
    missing_columns = [
        f"{table}.{column}"
        for table, columns in LEGACY_COLUMNS.items()
        for column in sorted(columns - actual.get(table, set()))
    ]
    if missing_columns:
        raise MigrationError("旧数据库缺少基线字段，拒绝自动接管：" + ", ".join(missing_columns))


def _validate_history(rows, migrations: list[Migration]) -> None:
    if [row[0] for row in rows] != list(range(1, len(rows) + 1)) or len(rows) > len(migrations):
        raise MigrationError("数据库迁移记录存在断档或版本高于当前程序，拒绝启动")
    for (version, name, checksum), migration in zip(rows, migrations):
        if name != migration.name or checksum != migration.checksum:
            raise MigrationError(f"数据库迁移 {version:04d} 的文件名或 checksum 与已应用记录不一致，拒绝启动")


def apply_migrations(db_engine, *, sql_dir: Path | None = None) -> list[int]:
    """Apply a complete pending batch atomically, under a database/schema-specific lock.

    The caller supplies the engine. Tests pass only TEST_DATABASE_URL engines with
    a disposable search_path; this function does not create a second connection
    to the configured application database.
    """
    migrations = load_migrations(sql_dir)
    raw = db_engine.raw_connection()
    driver = raw.driver_connection
    previous_autocommit = driver.autocommit
    if previous_autocommit:
        driver.autocommit = False
    pending_version = None
    try:
        with raw.cursor() as cursor:
            # Waiting processes must see the first process's commit after the lock.
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cursor.execute("SELECT current_database(), current_schema()")
            database, schema = cursor.fetchone()
            if not schema:
                raise MigrationError("数据库 search_path 中没有可用的目标 schema")
            lock_key = int.from_bytes(
                sha256(f"whu-party-review:migrations:{database}:{schema}".encode("utf-8")).digest()[:8],
                "big", signed=True,
            )
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", (lock_key,))
            # Do not resolve absent tables from a later schema in the search_path.
            cursor.execute(f"SET LOCAL search_path TO {_quote_identifier(schema)}")
            relations = _relations(cursor, schema)
            if "schema_migrations" not in relations:
                cursor.execute("""
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY CHECK (version > 0),
                        name TEXT NOT NULL UNIQUE,
                        checksum TEXT NOT NULL CHECK (checksum ~ '^[0-9a-f]{64}$'),
                        adopted BOOLEAN NOT NULL DEFAULT FALSE,
                        applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                """)
            elif relations["schema_migrations"] != "r":
                raise MigrationError("schema_migrations 必须是迁移记录表")
            cursor.execute("SELECT version, name, checksum FROM schema_migrations ORDER BY version")
            rows = cursor.fetchall()
            _validate_history(rows, migrations)
            legacy = False
            if not rows and set(relations) - {"schema_migrations"}:
                _validate_legacy(cursor, schema, relations)
                legacy = True
            applied = []
            for migration in migrations[len(rows):]:
                pending_version = migration.version
                adopted = legacy and migration.version == 1
                if not adopted:
                    cursor.execute(migration.sql)
                cursor.execute(
                    "INSERT INTO schema_migrations (version, name, checksum, adopted) VALUES (%s, %s, %s, %s)",
                    (migration.version, migration.name, migration.checksum, adopted),
                )
                applied.append(migration.version)
        raw.commit()
        return applied
    except MigrationError:
        raw.rollback()
        raise
    except Exception as exc:
        raw.rollback()
        version = f" {pending_version:04d}" if pending_version is not None else ""
        raise MigrationError(f"数据库迁移{version}失败；本次迁移及版本记录已全部回滚") from exc
    finally:
        # PostgreSQL releases the transaction advisory lock on commit/rollback.
        try:
            if previous_autocommit:
                driver.autocommit = True
        finally:
            raw.close()
