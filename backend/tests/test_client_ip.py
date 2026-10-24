"""Forwarding headers cannot change audit identity outside configured proxy hops."""
from ipaddress import ip_network
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import Mock

import dotenv
import pytest
from starlette.requests import Request

import services.client_ip as ip_service
from services.audit import log


def request_from(peer="198.51.100.9", forwarded=None):
    values = forwarded if isinstance(forwarded, list) else ([] if forwarded is None else [forwarded])
    scope = {
        "type": "http", "method": "GET", "path": "/", "headers": [
            (b"x-forwarded-for", value.encode("ascii")) for value in values
        ],
    }
    if peer is not None:
        scope["client"] = (peer, 12345)
    return Request(scope)


@pytest.fixture(autouse=True)
def no_trusted_proxies(monkeypatch):
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", ())


@pytest.mark.parametrize("peer", ["198.51.100.9", "127.0.0.1", "::1"])
def test_default_ignores_forwarded_headers_including_local_peers(peer):
    assert ip_service.client_ip(request_from(peer, "203.0.113.88")) == peer


def test_trusted_proxy_strips_only_the_rightmost_trusted_hops(monkeypatch):
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("10.0.0.0/8"),))
    request = request_from("10.0.0.2", "192.0.2.99, 198.51.100.9, 10.0.0.1")
    # A client-prepended spoofed IP must not win over the untrusted rightmost hop.
    assert ip_service.client_ip(request) == "198.51.100.9"


def test_forwarded_header_cannot_bypass_an_untrusted_direct_peer(monkeypatch):
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("10.0.0.0/8"),))
    assert ip_service.client_ip(request_from("198.51.100.9", "203.0.113.7, 10.0.0.1")) == "198.51.100.9"


def test_ipv6_proxy_and_ipv6_client_are_supported(monkeypatch):
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("2001:db8:1::/48"),))
    assert ip_service.client_ip(request_from("2001:db8:1::2", "2001:db8:2::9, 2001:db8:1::1")) == "2001:db8:2::9"


def test_repeated_header_fields_are_one_ordered_chain(monkeypatch):
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("10.0.0.0/8"),))
    assert ip_service.client_ip(request_from("10.0.0.2", ["192.0.2.99", "198.51.100.9, 10.0.0.1"])) == "198.51.100.9"


@pytest.mark.parametrize("forwarded", [
    "unknown", "198.51.100.9, bad", "bad, 198.51.100.9", "198.51.100.9,",
    "198.51.100.9:80", "[2001:db8::1]", "fe80::1%eth0", "999.1.1.1",
    ",".join(["198.51.100.9"] * 65), "1" * 8193,
])
def test_malformed_or_excessive_chains_fall_back_to_real_peer(monkeypatch, forwarded):
    monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("10.0.0.0/8"),))
    assert ip_service.client_ip(request_from("10.0.0.2", forwarded)) == "10.0.0.2"


@pytest.mark.parametrize("peer", [None, "testclient", "999.1.1.1", "fe80::1%eth0"])
def test_invalid_or_missing_peer_does_not_use_forwarded_identity(peer):
    assert ip_service.client_ip(request_from(peer, "198.51.100.9")) == ""


@pytest.mark.parametrize("trusted,expected", [(False, "10.0.0.2"), (True, "198.51.100.9")])
def test_audit_uses_the_same_proxy_policy(monkeypatch, trusted, expected):
    if trusted:
        monkeypatch.setattr(ip_service, "TRUSTED_PROXY_CIDRS", (ip_network("10.0.0.0/8"),))
    db = Mock()
    actor = SimpleNamespace(id=1, username="reviewer", role="SYS_ADMIN", ip="192.0.2.99")
    log(db, actor, "TEST", request=request_from("10.0.0.2", "198.51.100.9"))
    assert db.add.call_args.args[0].ip == expected


@pytest.mark.parametrize("value", [None, "10.0.0.0/8, 2001:db8:1::/48", "127.0.0.1", ""])
def test_proxy_configuration_accepts_explicit_networks(monkeypatch, value):
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **kw: None)
    if value is None:
        monkeypatch.delenv("TRUSTED_PROXY_CIDRS", raising=False)
    else:
        monkeypatch.setenv("TRUSTED_PROXY_CIDRS", value)
    config = runpy.run_path(str(Path(__file__).parents[1] / "config.py"))
    expected = tuple(ip_network(part.strip()) for part in (value or "").split(",") if part.strip())
    assert config["TRUSTED_PROXY_CIDRS"] == expected


@pytest.mark.parametrize("value", ["not-a-network", "10.0.0.1/8"])
def test_bad_proxy_configuration_fails_instead_of_broadening_trust(monkeypatch, value):
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **kw: None)
    monkeypatch.setenv("TRUSTED_PROXY_CIDRS", value)
    with pytest.raises(ValueError):
        runpy.run_path(str(Path(__file__).parents[1] / "config.py"))
