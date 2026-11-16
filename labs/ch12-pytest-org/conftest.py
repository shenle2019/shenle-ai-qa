"""全局夹具：起一次服务、登录一次、每条用例拿到干净的客户端。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api_client import HttpClient  # noqa: E402
from mini_api import serve  # noqa: E402


@pytest.fixture(scope="session")
def sut():
    with serve() as base:
        yield base


@pytest.fixture(scope="session")
def session_client(sut):
    return HttpClient(sut)


@pytest.fixture(scope="session")
def token(session_client):
    resp = session_client.post("/api/login", json={"username": "alice", "password": "secret"})
    return resp.json()["token"]


@pytest.fixture
def client(session_client, token):
    """每条用例一份：带 token，用完摘掉，互不影响。"""
    session_client.headers["Authorization"] = f"Bearer {token}"
    yield session_client
    session_client.headers.pop("Authorization", None)


@pytest.fixture
def anon(session_client):
    """不带 token 的客户端，专门测鉴权。"""
    session_client.headers.pop("Authorization", None)
    return session_client
