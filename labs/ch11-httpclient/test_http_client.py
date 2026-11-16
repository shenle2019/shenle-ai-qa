"""第 11 章的测试：封装的「可注入」设计让重试/异常都能被单测。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api import OrderApi, UserApi  # noqa: E402
from http_client import ApiError, HttpClient, Response  # noqa: E402
from mini_api import serve  # noqa: E402


def make_client(base="http://stub", **kw) -> HttpClient:
    return HttpClient(base, **kw)


# ---------- 用假 transport 测封装本身 ----------


def test_retries_on_5xx_for_get():
    seen = []

    def transport(method, url, **kw):
        seen.append(url)
        return Response(503, '{"error":"busy"}')

    client = make_client(retries=2, transport=transport)
    with pytest.raises(ApiError) as exc:
        client.get("/api/x")
    assert len(seen) == 3
    assert exc.value.status == 503


def test_post_is_not_retried_by_default():
    seen = []

    def transport(method, url, **kw):
        seen.append(method)
        return Response(500, "boom")

    client = make_client(retries=3, transport=transport)
    with pytest.raises(ApiError):
        client.post("/api/orders", json={})
    assert seen == ["POST"]


def test_4xx_raises_immediately_with_body():
    def transport(method, url, **kw):
        return Response(422, '{"error":"validation_error","message":"name 必填"}')

    client = make_client(retries=3, transport=transport)
    with pytest.raises(ApiError) as exc:
        client.post("/api/users", json={})
    assert exc.value.status == 422
    assert "name" in exc.value.body


def test_connection_error_is_wrapped():
    def transport(method, url, **kw):
        import requests

        raise requests.ConnectionError("refused")

    client = make_client(retries=1, transport=transport)
    with pytest.raises(ApiError) as exc:
        client.get("/api/health")
    assert exc.value.status == 0
    assert "connection_error" in str(exc.value)


def test_base_url_join_keeps_relative_paths():
    captured = {}

    def transport(method, url, **kw):
        captured["url"] = url
        return Response(200, "{}")

    client = HttpClient("http://host:8010/", transport=transport)
    client.get("/api/users")
    assert captured["url"] == "http://host:8010/api/users"


def test_default_headers_are_merged():
    captured = {}

    def transport(method, url, **kw):
        captured.update(kw["headers"])
        return Response(200, "{}")

    client = HttpClient("http://h", headers={"X-Team": "qa"}, transport=transport)
    client.get("/x", headers={"X-Trace": "1"})
    assert captured["X-Team"] == "qa" and captured["X-Trace"] == "1"


# ---------- 用真 SUT 测端到端 ----------


@pytest.fixture(scope="module")
def base():
    with serve() as url:
        yield url


@pytest.fixture
def users(base):
    client = HttpClient(base, timeout=5, retries=1)
    api = UserApi(client)
    api.with_token(api.login())
    return api


def test_api_layer_hides_paths(users):
    data = users.list(page=1, size=2)
    assert data["total"] >= 3
    assert len(data["items"]) <= 2


def test_create_and_delete_roundtrip(users):
    created = users.create("quinn")
    assert created["name"] == "quinn"
    users.delete(created["id"])
    with pytest.raises(ApiError) as exc:
        users.get(created["id"])
    assert exc.value.status == 404


def test_order_flow_through_api(base):
    client = HttpClient(base, timeout=5)
    user_api = UserApi(client)
    user_api.with_token(user_api.login())
    orders = OrderApi(client)
    order = orders.create([{"sku": "B-2", "qty": 3}])
    assert order["amount"] == 30
    assert orders.pay(order["id"])["status"] == "paid"


def test_client_remembers_calls(users):
    before = len(users.client.calls)
    users.list()
    assert len(users.client.calls) == before + 1
