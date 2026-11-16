"""链路用例的夹具：起服务、发 token、自动收尸。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api_client import ApiError, HttpClient  # noqa: E402
from mini_api import serve  # noqa: E402


@pytest.fixture(scope="session")
def sut():
    with serve() as base:
        yield base


@pytest.fixture(scope="session")
def http(sut):
    return HttpClient(sut)


@pytest.fixture(scope="session")
def token(http):
    return http.post("/api/login", json={"username": "alice", "password": "secret"}).json()["token"]


@pytest.fixture
def client(http, token):
    http.headers["Authorization"] = f"Bearer {token}"
    yield http
    http.headers.pop("Authorization", None)


@pytest.fixture
def created_orders(client):
    """记录本条用例造过的订单，结束后逐个删（删不掉也放过）。"""
    ids: list[int] = []
    yield ids
    for oid in ids:
        try:
            client.delete(f"/api/orders/{oid}")
        except ApiError:
            pass
