"""Build a portable Windows directory. Run using the isolated desktop venv."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PG_URL = "https://get.enterprisedb.com/postgresql/postgresql-16.15-5-windows-x64-binaries.zip"


def collect_licenses(app: Path):
    licenses = app / "licenses"
    licenses.mkdir(parents=True, exist_ok=True)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists(): shutil.copy2(python_license, licenses / "PYTHON.txt")
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name", "unknown").replace("/", "_").replace("\\", "_")
        for entry in dist.files or []:
            if entry.name.lower().startswith(("license", "copying", "notice")):
                source = Path(dist.locate_file(entry))
                if source.is_file():
                    target = licenses / name / Path(str(entry)).name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)


def extract_postgres(archive: Path, destination: Path):
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            parts = Path(info.filename).parts
            if len(parts) < 2 or info.is_dir(): continue
            if parts[1] not in {"bin", "lib", "share"} and "license" not in parts[-1].lower(): continue
            if parts[1] in {"pgAdmin 4", "StackBuilder"}: continue
            target = destination.joinpath(*parts[1:]).resolve()
            if not target.is_relative_to(destination.resolve()): raise ValueError("Unsafe archive path")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(info))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pg-archive", type=Path)
    p.add_argument("--output", type=Path, default=ROOT / "desktop/build/dist")
    args = p.parse_args()
    app = args.output / "PartyReview"
    if (app / "data").exists() or (app / "demo-data").exists():
        raise RuntimeError("构建目标含用户数据，请先备份并改用一个新的输出目录；不会覆盖现有工作台。")
    build = ROOT / "desktop/build"
    build.mkdir(parents=True, exist_ok=True)
    pg = ROOT / "desktop/runtime/postgres"
    archive = args.pg_archive or build / "postgresql-16.15-5.zip"
    if args.pg_archive or not (pg / "bin/postgres.exe").exists():
        if not archive.exists():
            print("Downloading official PostgreSQL Windows runtime…", flush=True)
            urllib.request.urlretrieve(PG_URL, archive)
        extract_postgres(archive, pg)
    if not (ROOT / "frontend/node_modules").is_dir():
        subprocess.run(["npm.cmd", "ci"], cwd=ROOT / "frontend", check=True)
    subprocess.run(["npm.cmd", "run", "build"], cwd=ROOT / "frontend", check=True)
    with (build / "pyinstaller.log").open("w", encoding="utf-8") as log:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--distpath", str(args.output),
                                 "--workpath", str(build / "pyinstaller"), str(ROOT / "desktop/party-review.spec")],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        print((build / "pyinstaller.log").read_text(encoding="utf-8", errors="replace")[-10000:])
        raise SystemExit(result.returncode)
    # Keep PostgreSQL DLLs out of PyInstaller's global DLL dependency search:
    # its bundled Tcl must not shadow the Python/Tk startup window's Tcl.
    shutil.copytree(pg, app / "runtime/postgres", dirs_exist_ok=True)
    collect_licenses(app)
    shutil.copy2(ROOT / "docs/Windows本地程序使用说明.md", app / "README_CN.md")
    shutil.copy2(ROOT / "docs/Windows本地程序验收.md", app / "VALIDATION_CN.md")
    shutil.copy2(ROOT / "docs/production-auth-and-model-policy.md", app / "AUTH_POLICY_CN.md")
    (app / "StartDemo.cmd").write_text('@echo off\r\ncd /d "%~dp0"\r\nstart "" "%~dp0PartyReview.exe" --demo\r\n', encoding="ascii")
    (app / "FirstLogin.cmd").write_text('@echo off\r\ncd /d "%~dp0"\r\nif exist "data\\FirstLogin.txt" start "" notepad.exe "data\\FirstLogin.txt"\r\nif exist "demo-data\\FirstLogin.txt" start "" notepad.exe "demo-data\\FirstLogin.txt"\r\n', encoding="ascii")
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
    manifest = {"app": "党员发展材料审核", "python": sys.version.split()[0], "postgres_url": PG_URL,
                "source_commit": revision, "source_has_uncommitted_changes": dirty,
                "postgres_archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest() if archive.exists() else None,
                "files": {str(file.relative_to(app)).replace("\\", "/"): hashlib.sha256(file.read_bytes()).hexdigest()
                          for file in app.rglob("*") if file.is_file()}}
    (app / "构建清单.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Built: " + str(app))


if __name__ == "__main__": main()
