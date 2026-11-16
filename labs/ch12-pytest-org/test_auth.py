"""鉴权：401 是「没证明你是谁」，403 是「证明了但没权限」。"""

from __future__ import annotations

import pytest

from api_client import ApiError


def test_missing_token_is_401(anon):
    anon.headers.pop("Authorization", None)
    with pytest.raises(ApiError) as exc:
        anon.get("/api/users")
    assert exc.value.status == 401


def test_wrong_password_is_401(session_client):
    with pytest.raises(ApiError) as exc:
        session_client.post("/api/login", json={"username": "alice", "password": "nope"})
    assert exc.value.status == 401
    assert "bad_credentials" in exc.value.body


def test_bad_token_is_401(anon):
    anon.headers["Authorization"] = "Bearer not-a-real-token"
    try:
        with pytest.raises(ApiError) as exc:
            anon.get("/api/users")
        assert exc.value.status == 401
    finally:
        anon.headers.pop("Authorization", None)


def test_token_works_after_login(session_client):
    token = session_client.post(
        "/api/login", json={"username": "bob", "password": "secret"}
    ).json()["token"]
    session_client.headers["Authorization"] = f"Bearer {token}"
    try:
        assert session_client.get("/api/users").status_code == 200
    finally:
        session_client.headers.pop("Authorization", None)
