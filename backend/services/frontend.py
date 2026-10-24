"""Serve built frontend assets only; never expose the source directory."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException


class SPAStatic(StaticFiles):
    async def get_response(self, path, scope):
        path = path.replace("\\", "/").lstrip("/")
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404 or path.split("/", 1)[0] in ("api", "assets", "storage") or Path(path).suffix:
                raise
            return await super().get_response("index.html", scope)


def mount_frontend(app: FastAPI, frontend_dir: str | Path) -> None:
    dist = Path(frontend_dir) / "dist"
    if (dist / "index.html").is_file():
        app.mount("/", SPAStatic(directory=dist, html=True), name="frontend")
