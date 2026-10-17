from __future__ import annotations

import hashlib
import os
import shutil
import zipfile
from pathlib import Path

from config import STORAGE_DIR, ensure_storage
from security import random_stored_name, sha256_bytes


def abs_path(rel: str) -> Path:
    ensure_storage()
    p = (STORAGE_DIR / rel).resolve()
    if not str(p).startswith(str(STORAGE_DIR.resolve())):
        raise ValueError("invalid storage path")
    return p


def save_bytes(data: bytes, archive_id: int, ext: str) -> tuple[str, str, int]:
    ensure_storage()
    name = random_stored_name(ext)
    rel = f"materials/{archive_id}/{name}"
    path = abs_path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return rel, sha256_bytes(data), len(data)


def save_tmp(data: bytes, name: str) -> str:
    ensure_storage()
    rel = f"tmp/{random_stored_name(Path(name).suffix.lstrip('.') or 'bin')}"
    path = abs_path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return rel


def extract_zip_safe(zip_rel: str, dest_rel: str, max_files: int = 500, max_total: int = 800 * 1024 * 1024) -> list[dict]:
    zpath = abs_path(zip_rel)
    dest = abs_path(dest_rel)
    dest.mkdir(parents=True, exist_ok=True)
    items = []
    total = 0
    with zipfile.ZipFile(zpath) as zf:
        infos = zf.infolist()
        if len(infos) > max_files:
            raise ValueError("ZIP 内文件过多")
        for info in infos:
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if name.startswith("/") or ".." in Path(name).parts:
                continue
            total += info.file_size
            if total > max_total:
                raise ValueError("ZIP 解压体积超限")
            target = dest / Path(name).name
            with zf.open(info) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
            items.append({
                "entry_path": name,
                "temp_path": str(target.relative_to(STORAGE_DIR)).replace("\\", "/"),
                "file_size": info.file_size,
            })
    return items


def read_bytes(rel: str) -> bytes:
    return abs_path(rel).read_bytes()


def exists(rel: str | None) -> bool:
    return bool(rel) and abs_path(rel).is_file()
