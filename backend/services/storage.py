from __future__ import annotations

import stat
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

from config import STORAGE_DIR, ensure_storage
from security import random_stored_name, sha256_bytes


def abs_path(rel: str) -> Path:
    ensure_storage()
    p = (STORAGE_DIR / rel).resolve()
    if not p.is_relative_to(STORAGE_DIR.resolve()):
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
    created = []
    try:
        with zipfile.ZipFile(zpath) as zf:
            infos = [info for info in zf.infolist() if not info.is_dir()]
            if len(infos) > max_files:
                raise ValueError("ZIP 内文件过多")
            if sum(info.file_size for info in infos) > max_total:
                raise ValueError("ZIP 解压体积超限")
            for info in infos:
                name = info.filename.replace("\\", "/")
                parts = PurePosixPath(name)
                if (parts.is_absolute() or PureWindowsPath(name).drive or ".." in parts.parts
                        or not parts.name or stat.S_ISLNK(info.external_attr >> 16)):
                    continue
                ext = parts.suffix.lstrip(".")
                ext = ext if ext.isalnum() and len(ext) <= 12 else "bin"
                # 归属使用原 entry_path；实际文件名独立生成，避免不同学生的同名材料覆盖。
                target = dest / random_stored_name(ext)
                size = 0
                with zf.open(info) as src, open(target, "xb") as out:
                    created.append(target)
                    while chunk := src.read(min(1024 * 1024, max_total - total + 1)):
                        total += len(chunk)
                        size += len(chunk)
                        if total > max_total:
                            raise ValueError("ZIP 解压体积超限")
                        out.write(chunk)
                items.append({
                    "entry_path": name,
                    "temp_path": str(target.relative_to(STORAGE_DIR)).replace("\\", "/"),
                    "file_size": size,
                })
    except Exception:
        # 出错仅清理本次新建的临时文件，保留同目录已有任务和文件。
        for target in created:
            try:
                target.unlink(missing_ok=True)
            except OSError:
                pass
        raise
    return items


def read_bytes(rel: str) -> bytes:
    return abs_path(rel).read_bytes()


def exists(rel: str | None) -> bool:
    return bool(rel) and abs_path(rel).is_file()
