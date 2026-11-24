"""Model egress is restricted to private LAN/loopback addresses, including DNS."""
import ipaddress
import socket
from urllib.parse import urlsplit

import httpx
from errors import unprocessable

NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '127.0.0.0/8', 'fc00::/7', '::1/128'))


def permitted(address):
    ip = ipaddress.ip_address(address)
    if getattr(ip, 'ipv4_mapped', None):
        ip = ip.ipv4_mapped
    return any(ip in network for network in NETWORKS)


def _resolve(host, port):
    return list(dict.fromkeys(item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)))


def destination(url):
    try:
        parsed = urlsplit(url)
        if (parsed.scheme not in ('http', 'https') or not parsed.hostname
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or any(c.isspace() for c in url) or '\\' in url or '%' in parsed.netloc):
            raise ValueError()
        port = parsed.port if parsed.port is not None else (443 if parsed.scheme == 'https' else 80)
        if not 1 <= port <= 65535:
            raise ValueError()
        try:
            addresses = [str(ipaddress.ip_address(parsed.hostname))]
        except ValueError:
            addresses = _resolve(parsed.hostname, port)
        if not addresses or not all(permitted(address) for address in addresses):
            raise ValueError()
        return parsed, addresses[0]
    except (ValueError, TypeError, OSError):
        raise unprocessable('模型接口仅允许校内私网或本机地址；请检查地址及 DNS，禁止公网、链路本地和混合解析地址') from None


class PrivateModelTransport(httpx.BaseTransport):
    def __init__(self):
        self.transport = httpx.HTTPTransport(trust_env=False)

    def handle_request(self, request):
        parsed, address = destination(str(request.url))
        # Connect to the verified literal IP, not a second DNS lookup. Preserve
        # Host and TLS SNI/certificate verification for the original hostname.
        request.extensions['sni_hostname'] = parsed.hostname
        request.url = request.url.copy_with(host=address)
        return self.transport.handle_request(request)

    def close(self):
        self.transport.close()
