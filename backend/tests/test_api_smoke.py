"""接口冒烟：无数据库时跳过；有库时走登录探活。"""
from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("WORKER_ENABLED", "0")
    try:
        from fastapi.testclient import TestClient
        from sqlalchemy import text

        from database import engine
        from main import app
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"无法启动应用（通常是未配置 PostgreSQL）：{e}")
    with TestClient(app) as client:
        yield client


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 0
    assert body["data"]["status"] == "ok"


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"username": "not-exist", "password": "x"})
    assert r.status_code in (401, 423)
    assert r.json()["code"] in (40100, 42300)
