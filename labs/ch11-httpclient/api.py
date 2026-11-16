"""业务语义层：用例只跟这些方法打交道，不关心 URL 与 header。"""

from __future__ import annotations

from http_client import HttpClient


class UserApi:
    def __init__(self, client: HttpClient):
        self.client = client

    def login(self, username: str = "alice", password: str = "secret") -> str:
        resp = self.client.post("/api/login", json={"username": username, "password": password})
        return resp.json()["token"]

    def with_token(self, token: str) -> "UserApi":
        self.client.headers["Authorization"] = f"Bearer {token}"
        return self

    def list(self, page: int = 1, size: int = 10) -> dict:
        return self.client.get("/api/users", params={"page": page, "size": size}).json()

    def create(self, name: str, role: str = "tester", email: str = "") -> dict:
        return self.client.post("/api/users", json={"name": name, "role": role, "email": email}).json()

    def get(self, user_id: int) -> dict:
        return self.client.get(f"/api/users/{user_id}").json()

    def delete(self, user_id: int) -> None:
        self.client.delete(f"/api/users/{user_id}")


class OrderApi:
    def __init__(self, client: HttpClient):
        self.client = client

    def create(self, items: list[dict], idempotency_key: str | None = None) -> dict:
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        return self.client.post("/api/orders", json={"items": items}, headers=headers).json()

    def pay(self, order_id: int) -> dict:
        return self.client.post(f"/api/orders/{order_id}/pay").json()

    def get(self, order_id: int) -> dict:
        return self.client.get(f"/api/orders/{order_id}").json()
