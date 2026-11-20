"""第 40 章：一个不依赖框架的迷你 Web 层（路由 + 请求 + 响应）。

刻意做成 FastAPI 的形状：`@app.get("/x")`、`Request`/`Response` 数据类、`app.handle(method, path, ...)`。
这样换成 FastAPI 时只替换这一层，业务代码与测试都不用改。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable

__all__ = ["Request", "Response", "Route", "App", "json_response", "error"]


@dataclass
class Request:
    method: str
    path: str
    query: dict[str, str] = field(default_factory=dict)
    body: dict | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class Response:
    status: int = 200
    body: object = None
    headers: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.body, ensure_ascii=False)


def json_response(body: object, status: int = 200) -> Response:
    return Response(status=status, body=body, headers={"Content-Type": "application/json; charset=utf-8"})


def error(status: int, message: str) -> Response:
    return json_response({"error": message}, status=status)


@dataclass
class Route:
    method: str
    pattern: str
    handler: Callable[[Request], Response]
    regex: re.Pattern = field(init=False)

    def __post_init__(self) -> None:
        # /projects/{project_id} -> ^/projects/(?P<project_id>[^/]+)$
        regex = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", r"(?P<\1>[^/]+)", self.pattern)
        self.regex = re.compile("^" + regex + "$")


class App:
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add(self, method: str, pattern: str, handler: Callable[[Request], Response]) -> None:
        self.routes.append(Route(method.upper(), pattern, handler))

    def get(self, pattern: str):
        def wrap(fn: Callable[[Request], Response]):
            self.add("GET", pattern, fn)
            return fn

        return wrap

    def post(self, pattern: str):
        def wrap(fn: Callable[[Request], Response]):
            self.add("POST", pattern, fn)
            return fn

        return wrap

    def patch(self, pattern: str):
        def wrap(fn: Callable[[Request], Response]):
            self.add("PATCH", pattern, fn)
            return fn

        return wrap

    def delete(self, pattern: str):
        def wrap(fn: Callable[[Request], Response]):
            self.add("DELETE", pattern, fn)
            return fn

        return wrap

    def match(self, method: str, path: str) -> tuple[Callable[[Request], Response], dict[str, str]] | None:
        for route in self.routes:
            if route.method != method.upper():
                continue
            found = route.regex.match(path)
            if found:
                return route.handler, {k: v for k, v in found.groupdict().items()}
        return None

    def handle(self, method: str, path: str, *, query: dict[str, str] | None = None, body: dict | None = None) -> Response:
        matched = self.match(method, path)
        if matched is None:
            return error(404, f"没有这个路由：{method} {path}")
        handler, params = matched
        request = Request(method=method.upper(), path=path, query=query or {}, body=body)
        # 路径参数塞进 query，handler 里统一 req.query["id"] 取值（真实框架是 kwargs）
        request.query = {**params, **request.query}
        return handler(request)
