from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
from types import SimpleNamespace

APP_TITLE = "党员发展材料审核"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def resource_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def app_directory() -> Path:
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else resource_root()


def postgres_runtime(bundled: Path) -> Path:
    # Keep the portable distribution in an English path, as requested.
    if not str(bundled).isascii():
        raise RuntimeError("请将完整 PartyReview 文件夹放到全英文路径（如 D:\\PartyReview）后运行。")
    return bundled


def bind_local(preferred: int = 0) -> socket.socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind(("127.0.0.1", preferred))
    except OSError:
        listener.bind(("127.0.0.1", 0))
    return listener


def read_config(path: Path) -> dict:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("db_password", "app_secret", "admin_password"):
            if not isinstance(data.get(key), str) or not data[key]:
                raise RuntimeError("本地配置不完整，请保留 data 文件夹并联系维护者，勿重新初始化覆盖数据。")
        return data
    data = {"db_password": secrets.token_urlsafe(32), "app_secret": secrets.token_urlsafe(48),
            "admin_password": secrets.token_urlsafe(12) + "A1", "http_port": 18761, "db_port": 18762}
    save_config(path, data)
    return data


def save_config(path: Path, data: dict) -> None:
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


class AlreadyRunning(RuntimeError):
    pass


class Runtime:
    def __init__(self, data_dir: Path, *, demo: bool = False, progress=None):
        self.data_dir = data_dir.resolve()
        self.demo = demo
        self.progress = progress or (lambda message: None)
        self.root = resource_root()
        bundled_pg = app_directory() / "runtime/postgres" if getattr(sys, "frozen", False) else self.root / "desktop/runtime/postgres"
        self.pg_root = Path(os.environ.get("PARTY_REVIEW_PG_RUNTIME") or bundled_pg)
        self.server = None
        self.thread = None
        self.listener = None
        self.lock_file = None
        self.owns_pg = False
        self.url = ""
        self.ready_file = self.data_dir / "running.json"

    def _lock(self):
        import msvcrt
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = (self.data_dir / "instance.lock").open("a+b")
        if self.lock_file.tell() == 0:
            self.lock_file.write(b"0"); self.lock_file.flush()
        self.lock_file.seek(0)
        try:
            msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            self.lock_file.close(); self.lock_file = None
            raise AlreadyRunning("这个工作台已经运行，请切换到已有窗口。") from exc

    def _pg(self, tool: str, *args, check=True, timeout=90):
        env = {**os.environ, "PATH": str(self.pg_root / "bin") + os.pathsep + os.environ.get("PATH", "")}
        log_path = self.data_dir / "database-bootstrap.log"
        # pg_ctl's long-lived server can inherit PIPE handles on Windows;
        # logging to a file avoids waiting forever for those pipes to close.
        with log_path.open("ab") as output:
            result = subprocess.run([str(self.pg_root / "bin" / (tool + ".exe")), *map(str, args)],
                                    cwd=self.pg_root / "bin", env=env, stdout=output, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, creationflags=NO_WINDOW, timeout=timeout)
        if check and result.returncode:
            message = log_path.read_bytes()[-1800:].decode("utf-8", errors="replace")
            raise RuntimeError(f"本地数据库操作失败（{tool}），请查看日志。\n{message[-1800:]}")
        return result

    def start(self):
        self._lock()
        if not (self.pg_root / "bin" / "postgres.exe").is_file():
            raise RuntimeError("程序文件不完整：缺少内置数据库。请完整解压压缩包，不要单独移动 exe。")
        if not (self.root / "frontend" / "dist" / "index.html").is_file():
            raise RuntimeError("缺少前端构建文件，请重新打包程序。")
        self.progress("准备本地运行文件…")
        self.pg_root = postgres_runtime(self.pg_root)
        self.config_path = self.data_dir / "config.json"
        cfg = read_config(self.config_path)
        cluster = self.data_dir / "postgres"
        self.progress("准备本地数据库，首次运行需要稍等…")
        if not (cluster / "PG_VERSION").is_file():
            password_file = self.data_dir / ".db-password.tmp"
            password_file.write_text(cfg["db_password"] + "\n", encoding="utf-8")
            try:
                self._pg("initdb", "-D", cluster, "-U", "party_local", "--pwfile", password_file,
                         "--auth-host=scram-sha-256", "--auth-local=scram-sha-256", "--encoding=UTF8", "--locale=C")
            finally:
                password_file.unlink(missing_ok=True)
        status = self._pg("pg_ctl", "status", "-D", cluster, check=False)
        if status.returncode == 0:
            # Recover our own database after an interrupted desktop session.
            cfg["db_port"] = int((cluster / "postmaster.pid").read_text().splitlines()[3])
            self.owns_pg = True
        else:
            with bind_local(int(cfg["db_port"])) as reservation:
                cfg["db_port"] = reservation.getsockname()[1]
            options = f"-h 127.0.0.1 -p {cfg['db_port']} -c max_connections=50 -c shared_buffers=32MB -c timezone=Asia/Shanghai"
            self._pg("pg_ctl", "start", "-D", cluster, "-l", self.data_dir / "postgres.log", "-o", options, "-w", "-t", "60")
            self.owns_pg = True
        save_config(self.config_path, cfg)
        import psycopg
        with psycopg.connect(host="127.0.0.1", port=cfg["db_port"], user="party_local", password=cfg["db_password"],
                             dbname="postgres", autocommit=True, connect_timeout=10) as conn:
            if not conn.execute("SELECT 1 FROM pg_database WHERE datname='party_review'").fetchone():
                conn.execute("CREATE DATABASE party_review ENCODING 'UTF8' TEMPLATE template0")
        self.listener = bind_local(int(cfg["http_port"]))
        cfg["http_port"] = self.listener.getsockname()[1]
        save_config(self.config_path, cfg)
        self.url = f"http://127.0.0.1:{cfg['http_port']}"
        os.environ.update({
            "DATABASE_URL": f"postgresql+psycopg://party_local:{cfg['db_password']}@127.0.0.1:{cfg['db_port']}/party_review",
            "STORAGE_DIR": str(self.data_dir / "storage"), "APP_SECRET_KEY": cfg["app_secret"],
            "ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": cfg["admin_password"], "WORKER_ENABLED": "1",
            "DEMO_LOGIN_HINT": "1" if self.demo else "0", "DEMO_PASSWORD": "Demo@2026",
            "HOST": "127.0.0.1", "PORT": str(cfg["http_port"]), "CORS_ORIGINS": self.url,
            "PARTY_REVIEW_BACKEND_DIR": str(self.root / "backend"), "PARTY_REVIEW_FRONTEND_DIR": str(self.root / "frontend"),
        })
        sys.path.insert(0, str(self.root / "backend"))
        self.progress("初始化材料清单与账号…")
        from database import init_db, SessionLocal
        from seed_rules import seed_rules, ensure_admin
        from models import User
        init_db()
        with SessionLocal() as db:
            new_admin = db.query(User).filter(User.username == "admin").first() is None
            seed_rules(db)
            ensure_admin(db)
            admin = db.query(User).filter(User.username == "admin").one()
            if new_admin:
                admin.must_change_password = True
            if self.demo:
                self.progress("正在创建虚构演示材料，首次启动约需一分钟…")
                from services.demo import seed_demo
                seed_demo(db, SimpleNamespace(id=admin.id), reset=False, run_checks=False)
            db.commit()
        if new_admin:
            (self.data_dir / "FirstLogin.txt").write_text(
                f"{APP_TITLE} · {'演示工作台' if self.demo else '本地工作台'}\n\n账号：admin\n初始密码：{cfg['admin_password']}\n"
                "\n首次登录必须修改密码。账号具有系统管理与组织管理两个已授权身份，改密并重新登录后选择本次身份。\n"
                "密码修改后，这份文件中的初始密码即失效；请妥善保存你设置的新密码。\n", encoding="utf-8-sig")
        self.progress("启动工作台…")
        import uvicorn
        main = importlib.import_module("main")
        config = uvicorn.Config(main.app, host="127.0.0.1", port=cfg["http_port"], log_config=None,
                                access_log=False, loop="asyncio", http="h11", lifespan="on", proxy_headers=False)
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, kwargs={"sockets": [self.listener]}, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + 90
        while not self.server.started:
            if not self.thread.is_alive() or time.monotonic() > deadline:
                raise RuntimeError("本地服务未能启动，请查看 data 文件夹中的 desktop.log。")
            time.sleep(0.1)
        self.ready_file.write_text(json.dumps({"url": self.url, "pid": os.getpid(), "demo": self.demo}), encoding="utf-8")
        return self.url

    def stop(self):
        if self.server:
            self.server.should_exit = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=15)
        if self.listener:
            self.listener.close()
        if self.owns_pg:
            self.progress("正在保存数据并关闭本地服务…")
            try:
                self._pg("pg_ctl", "stop", "-D", self.data_dir / "postgres", "-m", "fast", "-w", "-t", "30", timeout=40)
            except Exception as exc:
                print(f"Database stop: {exc}")
            self.owns_pg = False
        if self.lock_file:
            self.ready_file.unlink(missing_ok=True)
            self.lock_file.close(); self.lock_file = None
