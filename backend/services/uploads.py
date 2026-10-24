from __future__ import annotations

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from errors import too_large
from security import random_stored_name
from services import storage as store
from utils import get_setting

_MB = 1024 * 1024
_CHUNK_SIZE = _MB


async def read_material_upload(db, upload: UploadFile) -> bytes:
    """Only material files small enough for the configured limit enter memory."""
    cfg = get_setting(db, "upload", {})
    max_mb = max(0, int(cfg.get("max_file_mb") or 20))
    data = await upload.read(max_mb * _MB + 1)
    if len(data) > max_mb * _MB:
        raise too_large(f"文件超过 {max_mb} MB")
    return data


async def save_zip_upload(db, upload: UploadFile) -> str:
    """Stream a ZIP into storage; the caller owns the file after this succeeds."""
    cfg = get_setting(db, "upload", {})
    max_bytes = max(0, int(cfg.get("max_zip_mb") or 500)) * _MB
    # The supplied filename never forms any part of the temporary storage path.
    rel = f"tmp/{random_stored_name('zip')}"
    path = store.abs_path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    total = 0
    try:
        with path.open("xb") as output:
            created = True
            while chunk := await upload.read(min(_CHUNK_SIZE, max_bytes - total + 1)):
                total += len(chunk)
                if total > max_bytes:
                    raise too_large("ZIP 超过上限")
                await run_in_threadpool(output.write, chunk)
    except BaseException:
        # Includes request cancellation and only removes the file created here.
        if created:
            path.unlink(missing_ok=True)
        raise
    return rel
