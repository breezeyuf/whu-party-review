from __future__ import annotations

import os
from ipaddress import ip_network
from pathlib import Path

from dotenv import load_dotenv

_HERE = Path(__file__).resolve().parent
BACKEND_DIR = Path(os.environ.get("PARTY_REVIEW_BACKEND_DIR") or _HERE)
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent.parent / ".env")

APP_VERSION = "1.0.0"


def _env(name: str, default: str = "") -> str:
    v = os.environ.get(name)
    return default if v is None else v


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
CORS_ORIGINS = [s.strip() for s in _env("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if s.strip()]
# Only these direct peers may supply X-Forwarded-For. Invalid CIDRs fail startup.
TRUSTED_PROXY_CIDRS = tuple(ip_network(value.strip()) for value in _env("TRUSTED_PROXY_CIDRS").split(",") if value.strip())


def ensure_storage() -> Path:
    for sub in ("materials", "previews", "cache", "exports", "tmp"):
        (STORAGE_DIR / sub).mkdir(parents=True, exist_ok=True)
    return STORAGE_DIR
