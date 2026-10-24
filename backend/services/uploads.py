"""Bound application-level upload reads independently of declared sizes."""
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

from errors import too_large
from security import random_stored_name
from services import storage


CHUNK_SIZE = 1024 * 1024


async def _chunks(file: UploadFile, limit: int, message: str):
    total = 0
    while True:
        # Read at most one byte past the limit to detect overflow, including
        # uploads with missing or incorrect size metadata.
        chunk = await file.read(min(CHUNK_SIZE, max(1, limit - total + 1)))
        if not chunk:
            return
        total += len(chunk)
        if total > limit:
            raise too_large(message)
        yield chunk


async def read_upload(file: UploadFile, limit: int, message: str) -> bytes:
    with BytesIO() as data:
        async for chunk in _chunks(file, limit, message):
            data.write(chunk)
        return data.getvalue()


async def save_upload_tmp(file: UploadFile, limit: int, message: str) -> str:
    ext = Path(file.filename or "batch.zip").suffix.lstrip(".") or "zip"
    rel = f"tmp/{random_stored_name(ext)}"
    path = storage.abs_path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as target:
            created = True
            async for chunk in _chunks(file, limit, message):
                target.write(chunk)
        return rel
    except BaseException:
        # Cancellation/read failures must not leave partial ZIPs behind, and
        # exclusive creation must never delete another task's existing file.
        if created:
            path.unlink(missing_ok=True)
        raise
