from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import CORS_ORIGINS, HOST, PORT, ensure_storage
from database import SessionLocal, init_db
from errors import AppError
from seed_rules import ensure_admin, seed_rules
from worker import start_workers, stop_workers
from services.frontend import mount_frontend
from diagnostics import configure_logging, log_exception
from middleware import RequestBodyLimitMiddleware, RequestDiagnosticsMiddleware

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage()
    init_db()
    db = SessionLocal()
    printed = None
    try:
        seed_rules(db)
        printed = ensure_admin(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    if printed:
        print(f"[init] 管理员账号 admin 初始密码：{printed}（请立即修改）")
    start_workers()
    yield
    stop_workers()


app = FastAPI(title="党员发展材料智能审核工作台", version="1.0.0", lifespan=lifespan)

app.add_middleware(RequestBodyLimitMiddleware)
app.add_middleware(RequestDiagnosticsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=bool(CORS_ORIGINS),
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


@app.exception_handler(AppError)
async def app_error_handler(_, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.biz_code, "message": exc.biz_message, "data": exc.biz_data},
    )


@app.exception_handler(RequestValidationError)
async def valid_handler(_, exc: RequestValidationError):
    errors = [{"loc": e.get("loc"), "msg": e.get("msg")} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"code": 42200, "message": "参数校验失败", "data": {"errors": errors}})


@app.exception_handler(StarletteHTTPException)
async def http_handler(_, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content={"code": exc.detail.get("code"), "message": exc.detail.get("message"), "data": exc.detail.get("data")})
    code = {401: 40100, 403: 40300, 404: 40400, 409: 40900}.get(exc.status_code, exc.status_code * 100)
    return JSONResponse(status_code=exc.status_code, content={"code": code, "message": str(exc.detail), "data": None})


@app.exception_handler(Exception)
async def unhandled(_, exc: Exception):
    log_exception("http.unhandled", exc)
    return JSONResponse(status_code=500, content={"code": 50000, "message": "服务器内部错误", "data": None})


from routers import (  # noqa: E402
    admin,
    ai_check,
    archives,
    audit,
    auth,
    batches,
    health,
    issues,
    jobs,
    materials,
    messages,
    meta,
    notices,
    orgs,
    rules,
    settings,
    stats,
    submissions,
    users,
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(meta.router, prefix="/api")
app.include_router(orgs.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(batches.router, prefix="/api")
app.include_router(archives.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
app.include_router(issues.router, prefix="/api")
app.include_router(ai_check.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(notices.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

_here = os.path.dirname(os.path.abspath(__file__))
_fe = os.environ.get("PARTY_REVIEW_FRONTEND_DIR") or os.path.normpath(os.path.join(_here, "..", "frontend"))
mount_frontend(app, _fe)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=os.getenv("HOST", HOST), port=int(os.getenv("PORT", str(PORT))), proxy_headers=False)
