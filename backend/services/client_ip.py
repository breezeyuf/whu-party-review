"""Resolve an IP without trusting client-supplied forwarding headers by default."""
from __future__ import annotations

from ipaddress import IPv4Address, IPv6Address, ip_address

from config import TRUSTED_PROXY_CIDRS


def _address(raw: str) -> IPv4Address | IPv6Address | None:
    if not isinstance(raw, str) or "%" in raw:
        return None
    try:
        return ip_address(raw.strip())
    except ValueError:
        return None


def _trusted(address: IPv4Address | IPv6Address) -> bool:
    return any(address in network for network in TRUSTED_PROXY_CIDRS)


def client_ip(request) -> str:
    """Strip trusted hops from the right; malformed chains fall back to the peer.

    The ASGI server must leave request.client intact (Uvicorn proxy_headers=False).
    A trusted proxy must append the actual source IP or replace the incoming header.
    """
    peer = _address(getattr(getattr(request, "client", None), "host", None))
    if peer is None:
        return ""
    if not _trusted(peer):
        return str(peer)
    headers = getattr(request, "headers", None)
    if headers is None:
        return str(peer)
    if hasattr(headers, "getlist"):
        forwarded = ",".join(headers.getlist("x-forwarded-for"))
    else:
        forwarded = headers.get("x-forwarded-for", "")
    if not forwarded:
        return str(peer)
    # Bound parsing work as well as rejecting empty, port-bearing or invalid IPs.
    if len(forwarded) > 8192:
        return str(peer)
    parts = forwarded.split(",")
    if len(parts) > 64:
        return str(peer)
    chain = [_address(part) for part in parts]
    if any(address is None for address in chain):
        return str(peer)
    chain.append(peer)
    while len(chain) > 1 and _trusted(chain[-1]):
        chain.pop()
    return str(chain[-1])
