from __future__ import annotations

import hashlib
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import bcrypt
import jwt
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from config import APP_SECRET_KEY, STORAGE_DIR, ensure_storage

ALG = "HS256"
MAGIC = {
    "pdf": b"%PDF",
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def secret_key() -> str:
    if APP_SECRET_KEY:
        return APP_SECRET_KEY
    ensure_storage()
    path = STORAGE_DIR / ".secret"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    key = secrets.token_urlsafe(48)
    path.write_text(key, encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return key


def _fernet() -> Fernet:
    raw = secret_key().encode("utf-8")
    derived = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"party-review-v1", info=b"fernet").derive(raw)
    import base64

    return Fernet(base64.urlsafe_b64encode(derived))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def encrypt_field(plain: Optional[str]) -> Optional[str]:
    if not plain:
        return None
    return _fernet().encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_field(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        return None


def mask_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 7:
        return digits[:3] + "****" + digits[-4:]
    return "****"


def mask_id_card(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    s = re.sub(r"\s", "", value)
    if len(s) >= 8:
        return s[:3] + "*" * (len(s) - 7) + s[-4:]
    return "****"


def issue_token(user_id: int, token_version: int, typ: str, minutes: int | None = None, days: int | None = None) -> tuple[str, str, datetime]:
    jti = uuid.uuid4().hex
    exp = _now()
    if minutes is not None:
        exp = exp + timedelta(minutes=minutes)
    if days is not None:
        exp = exp + timedelta(days=days)
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "tv": token_version,
        "typ": typ,
        "exp": int(exp.timestamp()),
        "iat": int(_now().timestamp()),
    }
    token = jwt.encode(payload, secret_key(), algorithm=ALG)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token, jti, exp


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, secret_key(), algorithms=[ALG])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint(*parts: Any) -> str:
    text = "|".join("" if p is None else str(p) for p in parts)
    text = re.sub(r"\s+", "", text)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def detect_ext(filename: str, header: bytes) -> tuple[Optional[str], Optional[str]]:
    name = (filename or "").lower()
    ext = name.rsplit(".", 1)[-1] if "." in name else ""
    mime = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if ext in MAGIC:
        if not header.startswith(MAGIC[ext]):
            return None, None
        return ext, mime[ext]
    if ext == "docx":
        if header[:2] != b"PK":
            return None, None
        return "docx", mime["docx"]
    return None, None


def random_stored_name(ext: str) -> str:
    return f"{uuid.uuid4().hex}.{ext}"


def password_ok(new_password: str, old_password: Optional[str] = None) -> Optional[str]:
    if len(new_password) < 8:
        return "密码至少 8 位"
    if not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
        return "密码须同时包含字母和数字"
    if old_password and new_password == old_password:
        return "新密码不得与旧密码相同"
    return None


def random_password() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"
    return "A1" + "".join(secrets.choice(alphabet) for _ in range(8))
