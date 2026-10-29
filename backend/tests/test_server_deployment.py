"""Server mode is fail-closed; the application also works over verified local TLS."""
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import time

import httpx
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy.engine import make_url

import config
from tests.pg_fixtures import make_schema_engine


def test_server_mode_rejects_incomplete_security_settings(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DEPLOYMENT_MODE", "server")
    monkeypatch.setattr(config, "PUBLIC_BASE_URL", "http://example.invalid")
    monkeypatch.setattr(config, "APP_SECRET_KEY", "x" * 48)
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "test-admin-password")
    monkeypatch.setattr(config, "STORAGE_DIR", tmp_path)
    monkeypatch.setattr(config, "TRUSTED_PROXY_CIDRS", ("127.0.0.1/32",))
    monkeypatch.setattr(config, "CORS_ORIGINS", [])
    with pytest.raises(ValueError, match="HTTPS"):
        config.validate_deployment()
    monkeypatch.setattr(config, "PUBLIC_BASE_URL", "https://example.invalid")
    monkeypatch.setattr(config, "APP_SECRET_KEY", "")
    with pytest.raises(ValueError, match="APP_SECRET_KEY"):
        config.validate_deployment()


def _certificate(tmp_path: Path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "localhost")])
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(key, hashes.SHA256()))
    cert_path, key_path = tmp_path / "localhost.crt", tmp_path / "localhost.key"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                           serialization.PrivateFormat.TraditionalOpenSSL,
                                           serialization.NoEncryption()))
    return cert_path, key_path


def test_verified_https_health_login_and_same_origin_policy(tmp_path):
    schema = make_schema_engine("httpsqa")
    cert_path, key_path = _certificate(tmp_path)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ)
    env.update({
        "DATABASE_URL": make_url(os.environ["TEST_DATABASE_URL"]).set(
            query={"options": f"-csearch_path={schema.name}"}).render_as_string(hide_password=False),
        "DEPLOYMENT_MODE": "server", "PUBLIC_BASE_URL": f"https://localhost:{port}",
        "APP_SECRET_KEY": "local-https-test-key-with-at-least-forty-characters",
        "ADMIN_PASSWORD": "local-test-admin-password", "STORAGE_DIR": str(tmp_path / "storage"),
        "TRUSTED_PROXY_CIDRS": "127.0.0.1/32", "CORS_ORIGINS": "",
        "DEMO_LOGIN_HINT": "0", "WORKER_ENABLED": "0",
    })
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
        "--port", str(port), "--no-proxy-headers", "--ssl-certfile", str(cert_path),
        "--ssl-keyfile", str(key_path),
    ], cwd=Path(__file__).parents[1], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with httpx.Client(verify=ssl.create_default_context(cafile=str(cert_path)), trust_env=False, timeout=4) as client:
            deadline = time.monotonic() + 30
            while True:
                if process.poll() is not None:
                    pytest.fail("HTTPS 测试服务启动失败")
                try:
                    response = client.get(f"https://localhost:{port}/api/health")
                    if response.status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                if time.monotonic() >= deadline:
                    pytest.fail("HTTPS 测试服务启动超时")
                time.sleep(0.2)
            assert response.json()["data"]["db"] == "ok"
            bad = client.post(f"https://localhost:{port}/api/auth/login",
                              json={"username": "nonexistent", "password": "wrong"},
                              headers={"Origin": "https://untrusted.invalid"})
            assert bad.status_code == 401
            assert "access-control-allow-origin" not in bad.headers
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        schema.drop()
