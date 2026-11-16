"""CRUD 主流程：一条用例走完「建 → 查 → 改 → 删」。"""

from __future__ import annotations

import pytest

from api_client import ApiError
from data import PAGE_SIZE_CASES, PAGE_SIZE_IDS, USER_PAYLOADS, USER_PAYLOAD_IDS


@pytest.mark.smoke
def test_list_users_returns_page(client):
    resp = client.get("/api/users", params={"page": 1, "size": 2})
    assert resp.status_code == 200, resp.text[:200]
    data = resp.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 2, f"分页失效，返回 {len(data['items'])} 条"


@pytest.mark.parametrize("size, expected", PAGE_SIZE_CASES, ids=PAGE_SIZE_IDS)
def test_page_size_bounds(client, size, expected):
    try:
        resp = client.get("/api/users", params={"page": 1, "size": size})
        actual = resp.status_code
    except ApiError as exc:
        actual = exc.status
    assert actual == expected, f"size={size} 期望 {expected}，实际 {actual}"


@pytest.mark.parametrize("payload, expected", USER_PAYLOADS, ids=USER_PAYLOAD_IDS)
def test_create_user_validates_payload(client, payload, expected):
    try:
        resp = client.post("/api/users", json=payload)
    except ApiError as exc:
        assert exc.status == expected, f"{payload} 期望 {expected}，实际 {exc.status}: {exc.body[:120]}"
        return
    assert resp.status_code == expected


@pytest.mark.smoke
def test_crud_roundtrip(client):
    created = client.post("/api/users", json={"name": "ivy"}).json()
    uid = created["id"]

    got = client.get(f"/api/users/{uid}").json()
    assert got["name"] == "ivy"

    updated = client.patch(f"/api/users/{uid}", json={"role": "dev"}).json()
    assert updated["role"] == "dev"

    client.delete(f"/api/users/{uid}")
    with pytest.raises(ApiError) as exc:
        client.get(f"/api/users/{uid}")
    assert exc.value.status == 404


@pytest.mark.slow
def test_duplicate_name_conflicts(client):
    client.post("/api/users", json={"name": "dup-check"})
    with pytest.raises(ApiError) as exc:
        client.post("/api/users", json={"name": "dup-check"})
    assert exc.value.status == 409
