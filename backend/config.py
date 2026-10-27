from __future__ import annotations

import os
from ipaddress import ip_network
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv

_HERE = Path(__file__).resolve().parent
BACKEND_DIR = Path(os.environ.get("PARTY_REVIEW_BACKEND_DIR") or _HERE)
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent.parent / ".env")

APP_VERSION = "1.0.0"


def _env(name: str, default: str = "") -> str:
    v = os.environ.get(name)
    return default if v is None else v


DEPLOYMENT_MODE = _env("DEPLOYMENT_MODE", "desktop")
PUBLIC_BASE_URL = _env("PUBLIC_BASE_URL")
DATABASE_URL = _env(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/party_review",
)
HOST = _env("HOST", "127.0.0.1")
PORT = int(_env("PORT", "8000"))
APP_SECRET_KEY = _env("APP_SECRET_KEY", "")
STORAGE_DIR = Path(_env("STORAGE_DIR") or str(_HERE / "storage")).resolve()
ADMIN_USERNAME = _env("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = _env("ADMIN_PASSWORD", "")
WORKER_ENABLED = _env("WORKER_ENABLED", "1") not in ("0", "false", "False", "no")
DEMO_LOGIN_HINT = _env("DEMO_LOGIN_HINT", "0") not in ("0", "false", "False", "no")
DEMO_PASSWORD = _env("DEMO_PASSWORD", "Demo@2026")
CORS_ORIGINS = [s.strip() for s in _env("CORS_ORIGINS", "" if DEPLOYMENT_MODE == "server" else "http://127.0.0.1:5173,http://localhost:5173").split(",") if s.strip()]
# Only these direct peers may supply X-Forwarded-For. Invalid CIDRs fail startup.
TRUSTED_PROXY_CIDRS = tuple(ip_network(value.strip()) for value in _env("TRUSTED_PROXY_CIDRS").split(",") if value.strip())


def validate_deployment() -> None:
    if DEPLOYMENT_MODE not in ("desktop", "server"):
        raise ValueError("DEPLOYMENT_MODE 必须为 desktop 或 server")
    if DEPLOYMENT_MODE != "server":
        return
    parsed = urlsplit(PUBLIC_BASE_URL)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("服务器模式需要 HTTPS PUBLIC_BASE_URL")
    if len(APP_SECRET_KEY) < 32 or len(ADMIN_PASSWORD) < 12:
        raise ValueError("服务器模式需要独立的 APP_SECRET_KEY（至少 32 字符）和 ADMIN_PASSWORD（至少 12 字符）")
    if APP_SECRET_KEY.startswith("replace-") or ADMIN_PASSWORD.startswith("replace-") or "replace-with" in DATABASE_URL:
        raise ValueError("服务器模式不能使用示例凭据")
    if DEMO_LOGIN_HINT or not TRUSTED_PROXY_CIDRS:
        raise ValueError("服务器模式必须关闭演示登录提示并配置可信代理地址")
    if STORAGE_DIR == (_HERE / "storage").resolve():
        raise ValueError("服务器模式必须使用持久化 STORAGE_DIR")
    if DATABASE_URL.endswith("postgres:postgres@127.0.0.1:5432/party_review"):
        raise ValueError("服务器模式不能使用默认数据库凭据")
    if CORS_ORIGINS and CORS_ORIGINS != [PUBLIC_BASE_URL.rstrip("/")]:
        raise ValueError("服务器模式仅允许同源访问；请清空 CORS_ORIGINS")


def ensure_storage() -> Path:
    for sub in ("materials", "previews", "cache", "exports", "tmp"):
        (STORAGE_DIR / sub).mkdir(parents=True, exist_ok=True)
    return STORAGE_DIR
