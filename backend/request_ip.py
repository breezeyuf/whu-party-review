"""Resolve audit IPs only across explicitly trusted proxy hops."""
from ipaddress import ip_address

from config import TRUSTED_PROXY_CIDRS


def _address(value):
    # Scoped IPv6 and host:port strings are not valid proxy-chain entries.
    if "%" in value:
        raise ValueError("scoped address")
    return ip_address(value)


def _trusted(address):
    return any(address in network for network in TRUSTED_PROXY_CIDRS)


def client_ip(request) -> str:
    peer = request.client.host if request.client else ""
    try:
        current = _address(peer)
    except ValueError:
        return peer
    if not _trusted(current):
        return peer
    headers = request.headers
    values = headers.getlist("x-forwarded-for") if hasattr(headers, "getlist") else [headers.get("x-forwarded-for", "")]
    forwarded = ",".join(values)
    if not forwarded or len(forwarded) > 8192:
        return peer
    parts = forwarded.split(",")
    if len(parts) > 32:
        return peer
    try:
        chain = [_address(part.strip()) for part in parts]
    except ValueError:
        return peer
    # Walk from the socket peer toward the client. Stop at the first untrusted
    # hop; anything further left may have been supplied by that caller.
    for address in reversed(chain):
        if not _trusted(current):
            break
        current = address
    return str(current)
