import asyncio
import json
import logging
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, File, Request, UploadFile
from starlette import formparsers
from starlette.exceptions import HTTPException

from diagnostics import log_exception, request_id
from middleware import RequestBodyLimitMiddleware, RequestDiagnosticsMiddleware


def app_with_limit(limit):
    app = FastAPI()
    app.state.invoked = False
    app.add_middleware(RequestBodyLimitMiddleware, max_bytes=limit)
    app.add_middleware(RequestDiagnosticsMiddleware)

    @app.post("/json")
    async def json_body(request: Request):
        data = await request.json()
        app.state.invoked = True
        return {"length": len(data["value"])}

    @app.post("/form")
    async def form_body(file: UploadFile = File(...)):
        app.state.invoked = True
        return {"length": len(await file.read())}

    @app.post("/stream")
    async def stream_body(request: Request):
        total = 0
        async for chunk in request.stream():
            total += len(chunk)
        app.state.invoked = True
        return {"length": total}

    @app.post("/raw")
    async def raw_body(request: Request):
        data = await request.body()
        app.state.invoked = True
        return {"length": len(data)}

    return app


def call_asgi(app, path, chunks, headers=(), query_string=b""):
    async def run():
        messages = [
            {"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1}
            for index, chunk in enumerate(chunks)
        ]
        consumed = []
        sent = []

        async def receive():
            if messages:
                message = messages.pop(0)
                consumed.append(message)
                return message
            return {"type": "http.disconnect"}

        async def send(message):
            sent.append(message)

        await app({
            "type": "http", "asgi": {"version": "3.0", "spec_version": "2.4"},
            "http_version": "1.1", "method": "POST", "scheme": "http",
            "path": path, "raw_path": path.encode(), "query_string": query_string,
            "root_path": "", "headers": list(headers),
            "client": ("127.0.0.1", 12345), "server": ("testserver", 80),
        }, receive, send)
        assert request_id.get() is None
        return sent, consumed

    sent, consumed = asyncio.run(run())
    starts = [message for message in sent if message["type"] == "http.response.start"]
    assert len(starts) == 1, "the middleware must send exactly one response"
    body = b"".join(message.get("body", b"") for message in sent if message["type"] == "http.response.body")
    return starts[0], json.loads(body), consumed


@pytest.mark.parametrize("declared", [None, b"1", b"-1", b"invalid"])
def test_actual_json_chunks_reject_oversize_even_with_missing_or_false_content_length(declared):
    app = app_with_limit(20)
    headers = [(b"content-type", b"application/json")]
    if declared is not None:
        headers.append((b"content-length", declared))
    response, body, consumed = call_asgi(app, "/json", [b'{"value":"', b"x" * 20, b'"}'], headers)
    assert response["status"] == 413 and body["code"] == 41300
    assert len(consumed) == 2
    assert not app.state.invoked
    assert dict(response["headers"])[b"x-request-id"]


@pytest.mark.parametrize("streamed", [False, True])
def test_raw_and_streamed_request_bodies_are_counted_before_the_endpoint_finishes(streamed):
    app = app_with_limit(10)
    response, body, consumed = call_asgi(app, "/stream" if streamed else "/raw", [b"123456", b"78901"])
    assert response["status"] == 413 and body["code"] == 41300
    assert len(consumed) == 2 and not app.state.invoked


def test_body_at_exact_limit_is_allowed_and_context_is_reset():
    app = app_with_limit(10)
    response, body, _ = call_asgi(app, "/stream", [b"12345", b"67890"])
    assert response["status"] == 200 and body == {"length": 10}
    assert request_id.get() is None


def test_an_endpoint_cannot_hide_an_oversize_body_by_catching_the_read_error():
    app = app_with_limit(10)

    @app.post("/catch")
    async def catch(request: Request):
        try:
            await request.body()
        except HTTPException:
            return {"accepted": True}

    response, body, _ = call_asgi(app, "/catch", [b"123456", b"78901"])
    assert response["status"] == 413 and body["code"] == 41300
    assert "accepted" not in body


def test_a_response_already_started_is_aborted_without_a_second_response_start():
    async def run():
        sent = []

        async def consume_after_start(scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await receive()

        async def receive():
            return {"type": "http.request", "body": b"12345678901", "more_body": False}

        async def send(message):
            sent.append(message)

        app = RequestBodyLimitMiddleware(consume_after_start, max_bytes=10)
        with pytest.raises(HTTPException) as error:
            await app({"type": "http", "headers": []}, receive, send)
        assert error.value.status_code == 413
        assert [message["status"] for message in sent if message["type"] == "http.response.start"] == [200]

    asyncio.run(run())


def test_large_content_length_is_rejected_without_reading_the_body_or_opening_files(monkeypatch):
    app = app_with_limit(10)
    create = []
    monkeypatch.setattr(formparsers, "SpooledTemporaryFile", lambda **kwargs: create.append(kwargs))
    response, body, consumed = call_asgi(app, "/form", [b"unused"], [
        (b"content-type", b"multipart/form-data; boundary=test"), (b"content-length", b"11"),
    ])
    assert response["status"] == 413 and body["code"] == 41300
    assert not consumed and not create and not app.state.invoked


@pytest.mark.parametrize("declared", [None, b"1"])
def test_streamed_multipart_limit_closes_already_opened_parser_files(monkeypatch, declared):
    head = (b"--test\r\nContent-Disposition: form-data; name=\"file\"; filename=\"report.pdf\"\r\n"
            b"Content-Type: application/pdf\r\n\r\n")
    app = app_with_limit(len(head) + 4)
    created = []
    original = formparsers.SpooledTemporaryFile

    def tracked_file(*args, **kwargs):
        file = original(*args, **kwargs)
        created.append(file)
        return file

    monkeypatch.setattr(formparsers, "SpooledTemporaryFile", tracked_file)
    headers = [(b"content-type", b"multipart/form-data; boundary=test")]
    if declared is not None:
        headers.append((b"content-length", declared))
    response, body, consumed = call_asgi(app, "/form", [head + b"1234", b"5678\r\n--test--\r\n"], headers)
    assert response["status"] == 413 and body["code"] == 41300
    assert len(consumed) == 2 and len(created) == 1
    assert all(file.closed for file in created)
    assert not app.state.invoked


@pytest.mark.parametrize("path", ["/raw", "/stream"])
def test_multipart_content_type_on_a_raw_body_route_still_returns_413(path):
    app = app_with_limit(10)
    response, body, _ = call_asgi(app, path, [b"123456", b"78901"], [
        (b"content-type", b"multipart/form-data; boundary=test"),
    ])
    assert response["status"] == 413 and body["code"] == 41300
    assert not app.state.invoked


def test_500_response_and_diagnostic_logs_exclude_body_query_credentials_and_exception_values(caplog):
    app = app_with_limit(1000)
    secret = "private-document-token-password"

    @app.post("/fail/{item_id}")
    async def fail(item_id: str, request: Request):
        body = await request.body()
        raise RuntimeError(secret + body.decode())

    with caplog.at_level(logging.INFO, logger="party_review"):
        response, body, _ = call_asgi(app, f"/fail/{secret}", [secret.encode()], [
            (b"authorization", ("Bearer " + secret).encode()),
            (b"x-request-id", secret.encode()),
        ], query_string=("token=" + secret).encode())
    assert response["status"] == 500 and body["code"] == 50000
    request_header = dict(response["headers"])[b"x-request-id"].decode()
    assert body["data"]["request_id"] == request_header
    assert secret not in json.dumps(body) and secret not in caplog.text
    records = [json.loads(record.message) for record in caplog.records if record.name == "party_review"]
    failure = next(record for record in records if record["event"] == "http.unhandled")
    request = next(record for record in records if record["event"] == "http.request")
    assert failure["exception_type"] == "RuntimeError" and failure["frames"]
    assert failure["request_id"] == request["request_id"] == request_header
    assert request["status"] == 500 and request["route"] == "/fail/{item_id}"
    assert request_id.get() is None


def test_exception_diagnostics_record_call_sites_without_exception_strings_or_locals(caplog):
    secret = "private-material-model-api-key"
    try:
        raise ValueError(secret)
    except ValueError as error:
        with caplog.at_level(logging.ERROR, logger="party_review"):
            log_exception("test.failed", error, version_id=7)
    assert secret not in caplog.text
    payload = json.loads(caplog.records[-1].message)
    assert payload["version_id"] == 7 and payload["exception_type"] == "ValueError"
    assert payload["frames"][-1]["file"] == "test_request_middleware.py"
    assert set(payload["frames"][-1]) == {"file", "line", "function"}


def test_worker_logs_failure_identity_without_the_exception_value(caplog, monkeypatch):
    import worker
    from ai import pipeline

    secret = "private-worker-document-api-key"
    monkeypatch.setattr(worker, "_heartbeat", Mock())
    monkeypatch.setattr(worker, "_fail", Mock())
    monkeypatch.setattr(pipeline, "parse_version", Mock(side_effect=RuntimeError(secret)))
    job = SimpleNamespace(id=7, job_type="PARSE", params={"version_id": 8}, target_id=8)
    with caplog.at_level(logging.ERROR, logger="party_review"):
        worker._run(Mock(), job)
    assert secret not in caplog.text
    payload = json.loads(caplog.records[-1].message)
    assert payload["event"] == "worker.job_failed"
    assert payload["job_id"] == 7 and payload["job_type"] == "PARSE"
    assert payload["exception_type"] == "RuntimeError"
    assert secret not in worker._fail.call_args.args[2]


def test_material_parse_failure_logs_the_version_without_document_text(caplog, monkeypatch):
    from ai import pipeline

    secret = "private-material-text-model-password"
    ver = SimpleNamespace(id=8, material_id=9, stored_path="materials/1/file.pdf", file_ext="pdf")
    material = SimpleNamespace(id=9, submission_id=10)
    db = Mock()
    db.query.return_value.filter.return_value.first.side_effect = [ver, material]
    monkeypatch.setattr(pipeline, "parse_version_file", Mock(side_effect=RuntimeError(secret)))
    with caplog.at_level(logging.ERROR, logger="party_review"):
        with pytest.raises(RuntimeError):
            pipeline.parse_version(db, 8)
    assert secret not in caplog.text
    payload = json.loads(caplog.records[-1].message)
    assert payload["event"] == "material.parse_failed" and payload["version_id"] == 8
    assert ver.parse_status == "FAILED"
    assert secret not in ver.parse_error


def test_unrelated_validation_error_remains_a_422_response():
    app = app_with_limit(1000)
    response, body, _ = call_asgi(app, "/form", [b""], [(b"content-type", b"multipart/form-data; boundary=test")])
    assert response["status"] == 422 and "detail" in body
