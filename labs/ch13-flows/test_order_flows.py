"""链路测试：一条用例走完业务，断言状态组合而不是运气。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from api_client import ApiError
from factories import make_order, make_user, unique_name


def test_full_order_flow(client, created_orders):
    order = make_order(client, [{"sku": "A-1", "qty": 2}])
    created_orders.append(order["id"])
    assert order["status"] == "created"
    assert order["amount"] == 20

    paid = client.post(f"/api/orders/{order['id']}/pay").json()
    assert paid["status"] == "paid"

    got = client.get(f"/api/orders/{order['id']}").json()
    assert got["status"] == "paid"
    assert got["amount"] == 20


def test_idempotency_key_returns_same_order(client, created_orders):
    key = unique_name("idem")
    first = make_order(client, idem=key)
    created_orders.append(first["id"])
    second = client.post(
        "/api/orders",
        json={"items": [{"sku": "A-1", "qty": 1}]},
        headers={"Idempotency-Key": key},
    ).json()
    assert second["id"] == first["id"]


def test_pay_twice_conflicts(client, created_orders):
    order = make_order(client)
    created_orders.append(order["id"])
    client.post(f"/api/orders/{order['id']}/pay")
    with pytest.raises(ApiError) as exc:
        client.post(f"/api/orders/{order['id']}/pay")
    assert exc.value.status == 409


def test_concurrent_pay_yields_one_winner(client, created_orders):
    order = make_order(client)
    created_orders.append(order["id"])

    def pay(_):
        try:
            return client.post(f"/api/orders/{order['id']}/pay").status_code
        except ApiError as exc:
            return exc.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = sorted(pool.map(pay, range(2)))

    assert statuses == [200, 409], f"并发支付结果异常：{statuses}"


def test_make_user_is_unique(client):
    a = make_user(client)
    b = make_user(client)
    assert a["id"] != b["id"]
    assert a["name"] != b["name"]


def test_missing_order_is_404(client):
    with pytest.raises(ApiError) as exc:
        client.get("/api/orders/987654")
    assert exc.value.status == 404
