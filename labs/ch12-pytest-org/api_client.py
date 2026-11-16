"""第 12 章用的小 client：故意写得薄，把注意力放在 pytest 组织上。"""

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
    text: str
    elapsed_ms: float = 0.0
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def json(self):
        import json

        return json.loads(self.text)


class HttpClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers: dict[str, str] = {"Accept": "application/json"}
        self.session = requests.Session()

    def request(self, method: str, path: str, **kw) -> Response:
        started = time.perf_counter()
        raw = self.session.request(
            method.upper(),
            f"{self.base_url}{path}",
            timeout=self.timeout,
            headers={**self.headers, **kw.pop("headers", {})},
            **kw,
        )
        resp = Response(
            raw.status_code,
            raw.text,
            (time.perf_counter() - started) * 1000,
            dict(raw.headers),
        )
        if not resp.ok:
            raise ApiError(method, path, resp.status_code, resp.text)
        return resp

    def get(self, path: str, **kw) -> Response:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> Response:
        return self.request("POST", path, **kw)

    def put(self, path: str, **kw) -> Response:
        return self.request("PUT", path, **kw)

    def patch(self, path: str, **kw) -> Response:
        return self.request("PATCH", path, **kw)

    def delete(self, path: str, **kw) -> Response:
        return self.request("DELETE", path, **kw)
