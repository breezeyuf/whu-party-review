"""在临时 PostgreSQL（pgserver 自带 16.x 二进制）上运行后端 pytest，结束后停库。

用法：
    python tools/run_db_tests.py [backend_dir] [pgdata_dir] [-- pytest 其他参数]

- backend_dir 默认 `backend`，pgdata_dir 默认 `_tmp/pgdata_tests`。
- 需要当前 Python 环境安装 pgserver（后端依赖仍需在该环境中可用）。
- 也可以用环境变量 TEST_DATABASE_URL 指向一个已在运行的实例：此时只负责跑 pytest，
  不动数据目录（用于 pgserver 没有对应 Python 轮子的环境，例如 Python 3.13）。
- 测试中各模块自建随机 schema，结束后 DROP；pgserver 实例只在本脚本运行期间存活。
- 结束后停库并删除 pgdata 目录；异常退出同样清理。
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKEND = ROOT / "backend"
DEFAULT_PGDATA = ROOT / "_tmp" / "pgdata_tests"


def split_args(argv: list[str]) -> tuple[list[str], list[str]]:
    if "--" in argv:
        cut = argv.index("--")
        return argv[:cut], argv[cut + 1 :]
    return argv, []


def run_pytest(backend: Path, env: dict, extra: list[str]) -> int:
    cmd = [pytest_python(), "-m", "pytest", "-q", *extra]
    print(f"[pytest] {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, cwd=backend, env=env)
    return proc.returncode


def pytest_python() -> str:
    """跑 pytest 的解释器：显式指定 > 项目 .venv > 当前解释器。

    这样可以在只装了 pgserver 的 Python（例如 3.12 的 _pgtools）里启动临时库，
    让真正装了后端依赖的 .venv 去跑用例。
    """
    explicit = os.environ.get("PARTY_REVIEW_PYTHON")
    if explicit:
        return explicit
    for candidate in (ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"):
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def prepare_app_database(server_uri: str) -> str | None:
    """在同一个临时实例里建一个空库给 API 冒烟用（其 lifespan 会执行 init_db）。

    冒烟用例读 DATABASE_URL、会建表建管理员，所以只放在一次性实例里；psycopg 不可用时跳过。
    """
    try:
        import psycopg
    except ImportError:
        print("[pg] 没有 psycopg，API 冒烟用例会跳过（其需要 DATABASE_URL）", flush=True)
        return None
    base, _, _ = server_uri.rpartition("/")
    try:
        with psycopg.connect(server_uri, autocommit=True, connect_timeout=5) as conn:
            exists = conn.execute("select 1 from pg_database where datname = 'party_review_test'").fetchone()
            if not exists:
                conn.execute("CREATE DATABASE party_review_test")
    except Exception as exc:  # 建库失败不影响数据库回归本身
        print(f"[pg] 应用库准备失败，API 冒烟会跳过：{exc}", flush=True)
        return None
    return f"{base}/party_review_test"


def main() -> int:
    argv, pytest_args = split_args(sys.argv[1:])
    backend = Path(argv[0]).resolve() if len(argv) > 0 else DEFAULT_BACKEND
    pgdata = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_PGDATA
    if not (backend / "pytest.ini").is_file():
        print(f"找不到后端目录（缺少 pytest.ini）：{backend}")
        return 2

    existing_url = os.environ.get("TEST_DATABASE_URL")
    if existing_url:
        print(f"[pg] 使用已运行的实例 TEST_DATABASE_URL={existing_url}")
        print("[pg] 由外部实例负责启停，本脚本不动数据目录")
        env = os.environ.copy()
        app_db = prepare_app_database(existing_url.replace("postgresql+psycopg://", "postgresql://"))
        if app_db and not env.get("DATABASE_URL"):
            env["DATABASE_URL"] = app_db.replace("postgresql://", "postgresql+psycopg://")
            print(f"[pg] API 冒烟使用 DATABASE_URL={env['DATABASE_URL']}")
        env.setdefault("APP_SECRET_KEY", "test-key-0123456789abcdef")
        env.setdefault("WORKER_ENABLED", "0")
        return run_pytest(backend, env, pytest_args)

    try:
        import pgserver
    except ImportError:
        print("当前 Python 环境没有 pgserver（它没有 Python 3.13+ 的轮子）。两种做法：")
        print("  1) pip install pgserver（Python ≤3.12）后直接运行本脚本；")
        print("  2) 先用 pgserver 另起一个实例，再用 TEST_DATABASE_URL=... 调本脚本，例如：")
        print("       uv python install 3.12")
        print("       uv venv --python 3.12 _pgtools/.venv")
        print("       uv pip install --python _pgtools/.venv/Scripts/python.exe pgserver")
        print("       _pgtools/.venv/Scripts/python.exe tools/pg_run.py _tmp/pgdata")
        print("       TEST_DATABASE_URL=postgresql+psycopg://postgres:@127.0.0.1:<port>/postgres \\")
        print(f"           {sys.executable} tools/run_db_tests.py {backend}")
        return 2

    pgdata.mkdir(parents=True, exist_ok=True)
    server = pgserver.get_server(pgdata, cleanup_mode="stop")
    print(f"[pg] ready: {server.get_uri()}", flush=True)
    code = 1
    try:
        env = os.environ.copy()
        env["TEST_DATABASE_URL"] = server.get_uri().replace("postgresql://", "postgresql+psycopg://")
        app_db = prepare_app_database(server.get_uri())
        if app_db and not env.get("DATABASE_URL"):
            env["DATABASE_URL"] = app_db.replace("postgresql://", "postgresql+psycopg://")
        env.setdefault("APP_SECRET_KEY", "test-key-0123456789abcdef")
        env.setdefault("WORKER_ENABLED", "0")
        code = run_pytest(backend, env, pytest_args)
    finally:
        server.cleanup()
        print("[pg] server stopped", flush=True)
        try:
            shutil.rmtree(pgdata)
            print(f"[pg] removed {pgdata}", flush=True)
        except OSError as exc:
            print(f"[pg] 数据目录删除失败（可手动删除）：{exc}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
