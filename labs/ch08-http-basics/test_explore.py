"""第 8 章的测试：把「接口契约」写成断言。

这里测的不是业务，是**契约本身**：状态码、错误码、必要响应头、幂等与状态机。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from mini_api import serve  # noqa: E402


@pytest.fixture(scope="module")
def base():
    with serve() as url:
        yield url


@pytest.fixture(scope="module")
def auth(base):
    resp = requests.post(f"{base}/api/login", json={"username": "alice", "password": "secret"}, timeout=5)
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['token']}"}


def test_health_is_plain_json(base):
    resp = requests.get(f"{base}/api/health", timeout=5)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")
    assert resp.json()["status"] == "ok"


def test_login_rejects_wrong_password(base):
    resp = requests.post(f"{base}/api/login", json={"username": "alice", "password": "nope"}, timeout=5)
    assert resp.status_code == 401
    assert resp.json()["error"] == "bad_credentials"


def test_login_requires_both_fields(base):
    resp = requests.post(f"{base}/api/login", json={"username": "alice"}, timeout=5)
    assert resp.status_code == 422
    assert "password" in resp.json()["message"]


def test_list_requires_token(base):
    resp = requests.get(f"{base}/api/users", timeout=5)
    assert resp.status_code == 401
    assert resp.json()["error"] == "unauthorized"


def test_list_shape_and_pagination(base, auth):
    resp = requests.get(f"{base}/api/users?page=1&size=2", headers=auth, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert set(data) == {"total", "page", "size", "items"}
    assert data["size"] == 2
    assert len(data["items"]) <= 2
    first = data["items"][0]
    assert {"id", "name", "role"} <= set(first)


def test_page_size_upper_bound(base, auth):
    resp = requests.get(f"{base}/api/users?size=101", headers=auth, timeout=5)
    assert resp.status_code == 422
    assert "size" in resp.json()["message"]


def test_create_returns_201_and_location(base):
    resp = requests.post(f"{base}/api/users", json={"name": "erin"}, timeout=5)
    assert resp.status_code == 201
    assert resp.headers["Location"].startswith("/api/users/")
    assert resp.json()["name"] == "erin"


def test_duplicate_name_conflicts(base):
    requests.post(f"{base}/api/users", json={"name": "frank"}, timeout=5)
    resp = requests.post(f"{base}/api/users", json={"name": "frank"}, timeout=5)
    assert resp.status_code == 409
    assert resp.json()["error"] == "duplicate_name"


def test_missing_field_points_at_the_field(base):
    resp = requests.post(f"{base}/api/users", json={"role": "tester"}, timeout=5)
    assert resp.status_code == 422
    assert "name" in resp.json()["message"]


def test_unknown_user_is_404(base, auth):
    resp = requests.get(f"{base}/api/users/9999", headers=auth, timeout=5)
    assert resp.status_code == 404
    assert resp.json()["error"] == "user_not_found"


def test_delete_returns_204_without_body(base):
    created = requests.post(f"{base}/api/users", json={"name": "gina"}, timeout=5).json()
    resp = requests.delete(f"{base}/api/users/{created['id']}", timeout=5)
    assert resp.status_code == 204
    assert resp.content == b""


def test_idempotency_key_makes_post_safe(base, auth):
    headers = {**auth, "Idempotency-Key": "case-key-1"}
    payload = {"items": [{"sku": "S-1", "qty": 1}]}
    first = requests.post(f"{base}/api/orders", json=payload, headers=headers, timeout=5)
    second = requests.post(f"{base}/api/orders", json=payload, headers=headers, timeout=5)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


def test_paying_twice_is_conflict(base, auth):
    order = requests.post(
        f"{base}/api/orders", json={"items": [{"sku": "S-2", "qty": 1}]}, headers=auth, timeout=5
    ).json()
    assert requests.post(f"{base}/api/orders/{order['id']}/pay", headers=auth, timeout=5).status_code == 200
    again = requests.post(f"{base}/api/orders/{order['id']}/pay", headers=auth, timeout=5)
    assert again.status_code == 409
    assert again.json()["error"] == "already_paid"


def test_upload_and_download_roundtrip(base):
    up = requests.post(f"{base}/api/upload", files={"file": ("r.txt", b"roundtrip")}, timeout=5)
    assert up.status_code == 201
    assert up.json()["size"] == len(b"roundtrip")
    down = requests.get(f"{base}/api/files/r.txt", timeout=5)
    assert down.status_code == 200
    assert down.content == b"roundtrip"


def test_upload_rejects_non_multipart(base):
    resp = requests.post(f"{base}/api/upload", json={"file": "x"}, timeout=5)
    assert resp.status_code == 415
