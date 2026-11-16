"""薄 client：只为这一章服务，重点在结构与可注入。"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import requests


class ApiError(RuntimeError):
    def __init__(self, method: str, path: str, status: int, body: str):
        super().__init__(f"{method} {path} -> {status}: {body[:160]}")
        self.status = status
        self.body = body


@dataclass
class Response:
    status_code: int
    content: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_ms: float = 0.0

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", "replace")

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def json(self):
        import json

        return json.loads(self.text)


class HttpClient:
    def __init__(self, base_url: str, timeout: float = 5.0, retries: int = 0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.headers = {"Accept": "application/json"}

    def request(self, method: str, path: str, **kw) -> Response:
        url = f"{self.base_url}{path}"
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            started = time.perf_counter()
            try:
                raw = self.session.request(
                    method.upper(),
                    url,
                    timeout=self.timeout,
                    headers={**self.headers, **kw.pop("headers", {})},
                    **kw,
                )
            except (requests.ConnectionError, requests.Timeout) as exc:
                last = exc
                continue
            resp = Response(raw.status_code, raw.content, dict(raw.headers), (time.perf_counter() - started) * 1000)
            if resp.status_code >= 500 and attempt < self.retries and method.upper() in ("GET", "PUT", "DELETE"):
                continue
            if not resp.ok:
                raise ApiError(method, path, resp.status_code, resp.text)
            return resp
        raise ApiError(method, path, 0, f"connection_error: {last}")

    def get(self, path: str, **kw) -> Response:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> Response:
        return self.request("POST", path, **kw)

    def delete(self, path: str, **kw) -> Response:
        return self.request("DELETE", path, **kw)
