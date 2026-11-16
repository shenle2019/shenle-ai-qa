"""订单状态机：created → paid，重复支付 409。"""

from __future__ import annotations

import pytest

from api_client import ApiError


@pytest.mark.smoke
def test_create_order_computes_amount(client):
    order = client.post("/api/orders", json={"items": [{"sku": "A-1", "qty": 2}]}).json()
    assert order["status"] == "created"
    assert order["amount"] == 20, f"金额计算错：{order}"


def test_pay_moves_to_paid(client):
    created = client.post("/api/orders", json={"items": [{"sku": "B-2", "qty": 1}]}).json()
    paid = client.post(f"/api/orders/{created['id']}/pay").json()
    assert paid["status"] == "paid"


def test_pay_twice_conflicts(client):
    created = client.post("/api/orders", json={"items": [{"sku": "C-3", "qty": 1}]}).json()
    client.post(f"/api/orders/{created['id']}/pay")
    with pytest.raises(ApiError) as exc:
        client.post(f"/api/orders/{created['id']}/pay")
    assert exc.value.status == 409


def test_idempotency_key_reuses_order(client):
    payload = {"items": [{"sku": "D-4", "qty": 1}]}
    first = client.post("/api/orders", json=payload, headers={"Idempotency-Key": "k-1"}).json()
    second = client.post("/api/orders", json=payload, headers={"Idempotency-Key": "k-1"}).json()
    assert first["id"] == second["id"], "幂等键失效，生成了两单"


def test_missing_order_is_404(client):
    with pytest.raises(ApiError) as exc:
        client.get("/api/orders/999999")
    assert exc.value.status == 404
