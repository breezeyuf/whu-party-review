from __future__ import annotations

import os
import time
from uuid import uuid4

from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from diagnostics import event, log_exception, request_id


def _body_error():
    return JSONResponse(status_code=413, content={"code": 41300, "message": "请求体超过上传上限", "data": None})


class RequestBodyLimitMiddleware:
    """Count received bytes before multipart parsing, including chunked bodies."""

    def __init__(self, app, max_bytes: int | None = None):
        self.app = app
        self.max_bytes = max_bytes if max_bytes is not None else int(os.getenv("MAX_REQUEST_BODY_MB", "512")) * 1024 * 1024
        if self.max_bytes <= 0:
            raise ValueError("MAX_REQUEST_BODY_MB must be positive")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        try:
            declared = int(headers.get(b"content-length", b"0"))
        except ValueError:
            declared = 0
        if declared > self.max_bytes:
            return await _body_error()(scope, receive, send)
        total = 0
        oversized = False
        replaced = False
        started = False

        async def limited_receive():
            nonlocal total, oversized
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > self.max_bytes:
                    oversized = True
                    # The pinned Starlette parser closes partial temporary files
                    # on any exception while consuming the request stream.
                    raise HTTPException(status_code=413, detail="请求体超过上传上限")
            return message

        async def limited_send(message):
            nonlocal replaced, started
            if oversized:
                if not replaced:
                    if started:
                        raise HTTPException(status_code=413, detail="请求体超过上传上限")
                    replaced = True
                    await _body_error()(scope, receive, send)
                return
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, limited_send)
        except HTTPException:
            if not oversized or started:
                raise
            if not replaced:
                await _body_error()(scope, receive, send)


class RequestDiagnosticsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        trace = uuid4().hex
        token = request_id.set(trace)
        started = False
        status = 500
        before = time.monotonic()

        async def traced_send(message):
            nonlocal started, status
            if message["type"] == "http.response.start":
                started = True
                status = message["status"]
                message = {**message, "headers": [
                    (key, value) for key, value in message.get("headers", [])
                    if key.lower() != b"x-request-id"
                ] + [(b"x-request-id", trace.encode("ascii"))]}
            await send(message)

        try:
            await self.app(scope, receive, traced_send)
        except Exception as exc:
            log_exception("http.unhandled", exc, method=scope.get("method"),
                          route=getattr(scope.get("route"), "path", None))
            if started:
                raise
            await JSONResponse(status_code=500, content={
                "code": 50000, "message": "服务器内部错误", "data": {"request_id": trace},
            })(scope, receive, traced_send)
        finally:
            event("http.request", method=scope.get("method"),
                  route=getattr(scope.get("route"), "path", None), status=status,
                  duration_ms=round((time.monotonic() - before) * 1000, 1))
            request_id.reset(token)
