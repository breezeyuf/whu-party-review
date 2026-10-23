"""One-time, owner-only download of a password-protected Excel workbook."""
import base64
from datetime import timedelta
from io import BytesIO
import secrets

from fastapi.responses import Response
from openpyxl import Workbook
from urllib.parse import quote

from errors import gone, not_found
from models import ImportPasswordFile
from security import decrypt_field, encrypt_field
from services.exporter import _safe_cell
from utils import now


def create_password_file(db, actor, passwords):
    from msoffcrypto.format.ooxml import OOXMLFile
    wb = Workbook()
    ws = wb.active
    ws.title = "新账号初始密码"
    ws.append(["账号", "初始密码"])
    for username, password in passwords:
        ws.append([_safe_cell(username), _safe_cell(password)])
    plain, protected = BytesIO(), BytesIO()
    wb.save(plain)
    plain.seek(0)
    passphrase = secrets.token_urlsafe(18)
    OOXMLFile(plain).encrypt(passphrase, protected)
    record = ImportPasswordFile(created_by=actor.id,
        encrypted_payload=encrypt_field(base64.b64encode(protected.getvalue()).decode("ascii")),
        file_name="新账号初始密码.xlsx", created_at=now(), expires_at=now() + timedelta(hours=24))
    db.add(record)
    db.flush()
    return {"id": record.id, "file_name": record.file_name, "password": passphrase,
            "expires_at": record.expires_at.isoformat(),
            "download_url": f"/api/users/import-passwords/{record.id}/download"}


def consume_password_file(db, actor, file_id):
    # Filter by owner before locking; even administrators cannot consume a
    # different importer's file. The lock is held until the request commits.
    record = db.query(ImportPasswordFile).filter_by(id=file_id, created_by=actor.id).with_for_update().first()
    if not record:
        raise not_found()
    if record.consumed_at or record.expires_at <= now() or not record.encrypted_payload:
        raise gone("密码文件已下载或已过期")
    encrypted = decrypt_field(record.encrypted_payload)
    if not encrypted:
        raise gone("密码文件无法解密")
    data = base64.b64decode(encrypted, validate=True)
    response = Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(record.file_name)}",
                 "Cache-Control": "no-store, private", "Pragma": "no-cache"})
    record.encrypted_payload = None
    record.consumed_at = now()
    db.flush()
    return response
