"""第 11 章实验：把 requests 包成一个可测的 HttpClient。

设计目标：
- 用例里只写 ``/api/users`` 这种相对路径；
- 超时、重试、日志、异常收敛集中在一处；
- 传输层可注入（``transport``），于是封装本身也能被测试。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import requests

logger = logging.getLogger("httpclient")

Transport = Callable[..., "Response"]


class ApiError(RuntimeError):
    """带上下文的接口异常：状态码 + 响应体前 200 字符。"""

    def __init__(self, method: str, path: str, status: int, body: str):
        super().__init__(f"{method} {path} -> {status}: {body[:200]}")
        self.method = method
        self.path = path
        self.status = status
        self.body = body


@dataclass
class Response:
    status_code: int
    text: str
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    attempts: int = 1

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def json(self) -> Any:
        import json

        return json.loads(self.text)

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return f"<Response {self.status_code} {self.elapsed_ms:.1f}ms>"


def requests_transport(session: requests.Session):
    """默认传输层：用 requests 真发。"""

    def send(method: str, url: str, *, timeout: float, headers: dict, params=None, json=None, files=None) -> Response:
        started = time.perf_counter()
        raw = session.request(
            method.upper(), url, timeout=timeout, headers=headers, params=params, json=json, files=files
        )
        return Response(
            status_code=raw.status_code,
            text=raw.text,
            headers=dict(raw.headers),
            elapsed_ms=(time.perf_counter() - started) * 1000,
        )

    return send


class HttpClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        retries: int = 0,
        backoff: float = 0.0,
        headers: dict[str, str] | None = None,
        session: requests.Session | None = None,
        transport: Transport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.headers = {"Accept": "application/json", **(headers or {})}
        self._session = session or requests.Session()
        self._transport = transport or requests_transport(self._session)
        self.calls: list[tuple[str, str, int]] = []

    # ---------- 对外 ----------

    def request(self, method: str, path: str, **kwargs) -> Response:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        method = method.upper()
        attempt = 0
        last: Response | None = None

        while attempt <= self.retries:
            attempt += 1
            try:
                resp = self._transport(
                    method,
                    url,
                    timeout=self.timeout,
                    headers={**self.headers, **kwargs.pop("headers", {})},
                    params=kwargs.get("params"),
                    json=kwargs.get("json"),
                    files=kwargs.get("files"),
                )
            except (requests.ConnectionError, requests.Timeout) as exc:
                last = None
                logger.warning("%s %s 连接失败 (try %d): %s", method, path, attempt, exc.__class__.__name__)
                if attempt > self.retries:
                    raise ApiError(method, path, 0, f"connection_error: {exc}") from exc
                time.sleep(self.backoff * attempt)
                continue

            resp.attempts = attempt
            self.calls.append((method, path, resp.status_code))
            self._log(method, path, resp)

            if resp.status_code >= 500 and attempt <= self.retries and method in ("GET", "PUT", "DELETE", "HEAD"):
                time.sleep(self.backoff * attempt)
                last = resp
                continue
            if not resp.ok:
                raise ApiError(method, path, resp.status_code, resp.text)
            return resp

        if last is not None:
            raise ApiError(method, path, last.status_code, last.text)
        raise ApiError(method, path, 0, "retries exhausted")

    def get(self, path: str, **kw) -> Response:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> Response:
        return self.request("POST", path, **kw)

    def put(self, path: str, **kw) -> Response:
        return self.request("PUT", path, **kw)

    def delete(self, path: str, **kw) -> Response:
        return self.request("DELETE", path, **kw)

    # ---------- 内部 ----------

    def _log(self, method: str, path: str, resp: Response) -> None:
        has_token = "Authorization" in self.headers
        logger.info(
            "%s %s -> %d in %.0fms (try %d, token=%s)",
            method,
            path,
            resp.status_code,
            resp.elapsed_ms,
            resp.attempts,
            "yes" if has_token else "no",
        )
        if not resp.ok:
            logger.info("  body: %s", resp.text[:200])
