from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

root = Path(SPECPATH).parent
sys.path.insert(0, str(root / "backend"))
hidden = ["main", "uvicorn.logging", "uvicorn.loops.asyncio", "uvicorn.protocols.http.h11_impl", "uvicorn.lifespan.on",
          "sqlalchemy.dialects.postgresql.psycopg", "psycopg_binary", "webview.platforms.winforms", "webview.platforms.edgechromium"]
for package in ["routers", "services", "ai", "schemas", "msoffcrypto", "migrations"]:
    hidden += collect_submodules(package)
datas = [(str(root / "backend" / "schema.sql"), "backend"),
         (str(root / "backend" / "migrations" / "sql"), "backend/migrations/sql"),
         (str(root / "frontend" / "dist"), "frontend/dist")]
datas += collect_data_files("webview")
datas += copy_metadata("pywebview")
for package in ['rapidocr', 'onnxruntime']:
    datas += collect_data_files(package)
    datas += copy_metadata(package)
    hidden += collect_submodules(package)
for name in ["seed_data"]:
    if (root / "backend" / name).is_dir(): datas.append((str(root / "backend" / name), "backend/" + name))
a = Analysis([str(root / "desktop" / "app.py")], pathex=[str(root), str(root / "backend")],
             binaries=[], datas=datas, hiddenimports=hidden, hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=["pytest", "IPython", "notebook", "matplotlib", "PyQt5", "PyQt6", "PySide2", "PySide6", "paddle", "paddleocr"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="PartyReview", debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="PartyReview")
