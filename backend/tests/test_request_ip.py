import asyncio
from ipaddress import ip_network
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import Mock

import dotenv
from fastapi import FastAPI, Request
import httpx
import pytest
from starlette.requests import Request as StarletteRequest
import uvicorn

import deps
import request_ip
from services import audit


def request(peer, forwarded=None, extra_headers=()):
    headers = [] if forwarded is None else [(b"x-forwarded-for", forwarded.encode())]
    headers.extend(extra_headers)
    return StarletteRequest({
        "type": "http", "headers": headers,
        "client": (peer, 12345) if peer is not None else None,
    })


@pytest.fixture
def trust(monkeypatch):
    def configure(*cidrs):
        monkeypatch.setattr(request_ip, "TRUSTED_PROXY_CIDRS", tuple(ip_network(c) for c in cidrs))
    configure()
    return configure


@pytest.mark.parametrize("peer", ["198.51.100.7", "127.0.0.1", "::1", "testclient", None])
def test_no_trust_ignores_spoofed_header(trust, peer):
    assert request_ip.client_ip(request(peer, "203.0.113.99")) == (peer or "")


@pytest.mark.parametrize("peer,forwarded,expected", [
    ("10.0.0.2", "198.51.100.7", "198.51.100.7"),
    ("10.0.0.2", "203.0.113.99, 198.51.100.7", "198.51.100.7"),
    ("10.0.0.2", "203.0.113.99, 198.51.100.7, 10.0.0.3", "198.51.100.7"),
    ("198.51.100.7", "203.0.113.99, 10.0.0.3", "198.51.100.7"),
    ("::1", "2001:db8::123, 10.0.0.3", "2001:db8::123"),
    ("10.0.0.2", None, "10.0.0.2"),
])
def test_chain_stops_at_first_untrusted_hop(trust, peer, forwarded, expected):
    trust("10.0.0.0/24", "::1/128")
    assert request_ip.client_ip(request(peer, forwarded)) == expected


@pytest.mark.parametrize("value", [
    "unknown", "", "198.51.100.7,", "198.51.100.7:8080", "[::1]",
    "fe80::1%eth0", "invalid, 198.51.100.7", ",".join(["10.0.0.3"] * 33), "x" * 8193,
])
def test_malformed_or_excessive_header_falls_back_to_peer(trust, value):
    trust("10.0.0.0/24")
    assert request_ip.client_ip(request("10.0.0.2", value)) == "10.0.0.2"


def test_duplicate_headers_are_one_ordered_chain(trust):
    trust("10.0.0.0/24")
    req = request("10.0.0.2", "203.0.113.99", [(b"x-forwarded-for", b"198.51.100.7, 10.0.0.3")])
    assert request_ip.client_ip(req) == "198.51.100.7"


@pytest.mark.parametrize("trusted,expected", [(False, "10.0.0.2"), (True, "198.51.100.7")])
def test_actor_and_audit_paths_use_same_ip_policy(trust, trusted, expected):
    if trusted:
        trust("10.0.0.0/24")
    req = request("10.0.0.2", "203.0.113.99, 198.51.100.7")
    assert deps.client_ip(req) == expected
    db = Mock()
    audit.log(db, None, "LOGIN_FAILED", request=req)
    assert db.add.call_args.args[0].ip == expected
    actor = SimpleNamespace(ip=expected, id=1)
    audit.log(db, actor, "UPDATE")
    assert db.add.call_args.args[0].ip == expected


@pytest.mark.parametrize("value", ["*", "not-a-network", "10.0.0.0/999"])
def test_invalid_proxy_configuration_fails_closed(monkeypatch, value):
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **kw: None)
    monkeypatch.setenv("TRUSTED_PROXY_CIDRS", value)
    with pytest.raises(ValueError):
        runpy.run_path(str(Path(__file__).parents[1] / "config.py"))


def test_actual_server_entry_preserves_socket_peer_before_app_parsing(monkeypatch, trust):
    run = Mock()
    monkeypatch.setattr(uvicorn, "run", run)
    runpy.run_path(str(Path(__file__).parents[1] / "main.py"), run_name="__main__")
    assert run.call_args.kwargs["proxy_headers"] is False
    app = FastAPI()

    @app.get("/")
    def source(req: Request):
        return {"ip": request_ip.client_ip(req)}

    config = uvicorn.Config(app, proxy_headers=run.call_args.kwargs["proxy_headers"], log_config=None)
    config.load()

    async def check():
        transport = httpx.ASGITransport(app=config.loaded_app, client=("127.0.0.1", 12345))
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/", headers={"X-Forwarded-For": "203.0.113.99"})
            assert response.json() == {"ip": "127.0.0.1"}

    asyncio.run(check())
