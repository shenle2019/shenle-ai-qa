"""一个只用标准库写的小型被测系统（SUT）。

后面的接口章节都用它来练手，不依赖外网、不依赖数据库：

- 鉴权：``POST /api/login`` 拿 token，之后请求带 ``Authorization: Bearer <token>``
- 用户：增删改查 + 分页 + 参数校验
- 订单：下单（支持幂等键）、查详情、列表
- 文件：multipart 上传、下载、CSV 导出

启动：``python mini_api.py``（默认 8010 端口），或者用 :func:`serve` 在测试里起一个。
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

TOKEN_TTL = 3600
USERS: dict[int, dict[str, Any]] = {}
ORDERS: dict[int, dict[str, Any]] = {}
TOKENS: dict[str, dict[str, Any]] = {}
IDEMPOTENCY: dict[str, int] = {}
FILES: dict[str, bytes] = {}
FLAKY: dict[str, int] = {}
_NEXT = {"user": 0, "order": 0}


def reset() -> None:
    """把内存数据清空，测试之间互不影响。"""
    USERS.clear()
    ORDERS.clear()
    TOKENS.clear()
    IDEMPOTENCY.clear()
    FILES.clear()
    FLAKY.clear()
    _NEXT["user"] = 0
    _NEXT["order"] = 0


def _seed() -> None:
    if USERS:
        return
    for name, role in [("alice", "admin"), ("bob", "tester"), ("carol", "viewer")]:
        _create_user({"name": name, "role": role, "email": f"{name}@example.com"})


def _create_user(payload: dict[str, Any]) -> dict[str, Any]:
    _NEXT["user"] += 1
    user = {
        "id": _NEXT["user"],
        "name": payload["name"],
        "role": payload.get("role", "tester"),
        "email": payload.get("email", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    USERS[user["id"]] = user
    return user


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "MiniSUT/1.0"

    # ---------- 基础工具 ----------

    def log_message(self, fmt: str, *args: Any) -> None:  # 静音，避免刷屏
        return

    def _send(self, status: int, body: Any = None, headers: dict[str, str] | None = None) -> None:
        raw = b""
        if body is not None:
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if raw:
            self.wfile.write(raw)

    def _send_bytes(self, status: int, raw: bytes, content_type: str, filename: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("body 不是合法 JSON")
        if not isinstance(data, dict):
            raise ValueError("body 必须是 JSON 对象")
        return data

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlparse(self.path).query)

    def _current_user(self) -> dict[str, Any] | None:
        auth = self.headers.get("Authorization") or ""
        if not auth.startswith("Bearer "):
            return None
        info = TOKENS.get(auth[7:])
        if not info or info["expires_at"] < time.time():
            return None
        return info

    # ---------- 路由 ----------

    def do_GET(self) -> None:  # noqa: N802
        self._route("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._route("POST")

    def do_PUT(self) -> None:  # noqa: N802
        self._route("PUT")

    def do_PATCH(self) -> None:  # noqa: N802
        self._route("PATCH")

    def do_DELETE(self) -> None:  # noqa: N802
        self._route("DELETE")

    def _route(self, method: str) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        parts = [p for p in path.split("/") if p]

        try:
            if method == "GET" and path == "/api/health":
                return self._send(200, {"status": "ok", "time": time.strftime("%H:%M:%S")})

            if method == "GET" and path == "/api/flaky":
                key = self._query().get("key", ["default"])[0]
                remain = FLAKY.get(key, 2)
                if remain > 0:
                    FLAKY[key] = remain - 1
                    return self._send(503, {"error": "temporarily_unavailable", "remain": remain - 1})
                return self._send(200, {"ok": True, "key": key})

            if method == "POST" and path == "/api/login":
                return self._login()

            if parts[:2] != ["api", "users"] and parts[:2] != ["api", "orders"]:
                if not (method == "GET" and parts[:2] == ["api", "files"]):
                    return self._send(404, {"error": "not_found", "path": path})

            if parts[:2] == ["api", "users"]:
                return self._users(method, parts[2:])
            if parts[:2] == ["api", "orders"]:
                return self._orders(method, parts[2:])
            if parts[:2] == ["api", "files"] and method == "GET":
                return self._files(parts[2:])
            return self._send(405, {"error": "method_not_allowed", "method": method})
        except ValueError as exc:
            return self._send(422, {"error": "validation_error", "message": str(exc)})

    # ---------- 鉴权 ----------

    def _login(self) -> None:
        body = self._json_body()
        name, password = body.get("username"), body.get("password")
        if not name or not password:
            return self._send(422, {"error": "validation_error", "message": "username 和 password 必填"})
        if password != "secret":
            return self._send(401, {"error": "bad_credentials"})
        token = uuid.uuid4().hex
        TOKENS[token] = {"username": name, "expires_at": time.time() + TOKEN_TTL}
        return self._send(200, {"token": token, "expires_in": TOKEN_TTL})

    def _users(self, method: str, rest: list[str]) -> None:
        if method == "GET" and not rest:
            user = self._current_user()
            if not user:
                return self._send(401, {"error": "unauthorized"})
            page = int(self._query().get("page", ["1"])[0])
            size = int(self._query().get("size", ["10"])[0])
            if page < 1 or size < 1 or size > 100:
                return self._send(422, {"error": "validation_error", "message": "page>=1 且 1<=size<=100"})
            items = list(USERS.values())
            start = (page - 1) * size
            return self._send(
                200,
                {"total": len(items), "page": page, "size": size, "items": items[start : start + size]},
            )

        if method == "POST" and not rest:
            body = self._json_body()
            if not body.get("name"):
                return self._send(422, {"error": "validation_error", "message": "name 必填"})
            if any(u["name"] == body["name"] for u in USERS.values()):
                return self._send(409, {"error": "duplicate_name"})
            return self._send(201, _create_user(body), {"Location": f"/api/users/{_NEXT['user']}"})

        if not rest or not rest[0].isdigit():
            return self._send(404, {"error": "not_found"})
        uid = int(rest[0])
        if uid not in USERS:
            return self._send(404, {"error": "user_not_found", "id": uid})

        if method == "GET":
            return self._send(200, USERS[uid])

        if method in ("PUT", "PATCH"):
            body = self._json_body()
            for field in ("name", "role", "email"):
                if field in body:
                    USERS[uid][field] = body[field]
            return self._send(200, USERS[uid])

        if method == "DELETE":
            del USERS[uid]
            return self._send(204)
        return self._send(405, {"error": "method_not_allowed"})

    # ---------- 订单 ----------

    def _orders(self, method: str, rest: list[str]) -> None:
        if not self._current_user():
            return self._send(401, {"error": "unauthorized"})

        if method == "POST" and not rest:
            body = self._json_body()
            items = body.get("items")
            if not isinstance(items, list) or not items:
                return self._send(422, {"error": "validation_error", "message": "items 不能为空"})
            for item in items:
                if not isinstance(item, dict) or "sku" not in item or int(item.get("qty", 0)) <= 0:
                    return self._send(422, {"error": "validation_error", "message": "每项需要 sku 且 qty>0"})

            key = self.headers.get("Idempotency-Key")
            if key and key in IDEMPOTENCY:
                return self._send(200, ORDERS[IDEMPOTENCY[key]])

            _NEXT["order"] += 1
            order = {
                "id": _NEXT["order"],
                "user": self._current_user()["username"],
                "items": items,
                "amount": sum(int(i["qty"]) * 10 for i in items),
                "status": "created",
            }
            ORDERS[order["id"]] = order
            if key:
                IDEMPOTENCY[key] = order["id"]
            return self._send(201, order)

        if method == "GET" and not rest:
            return self._send(200, {"total": len(ORDERS), "items": list(ORDERS.values())})

        if method == "GET" and rest[0].isdigit():
            oid = int(rest[0])
            if oid not in ORDERS:
                return self._send(404, {"error": "order_not_found", "id": oid})
            return self._send(200, ORDERS[oid])

        if method == "POST" and len(rest) == 2 and rest[1] == "pay":
            oid = int(rest[0])
            if oid not in ORDERS:
                return self._send(404, {"error": "order_not_found", "id": oid})
            if ORDERS[oid]["status"] == "paid":
                return self._send(409, {"error": "already_paid"})
            ORDERS[oid]["status"] = "paid"
            return self._send(200, ORDERS[oid])

        return self._send(405, {"error": "method_not_allowed"})

    # ---------- 文件 ----------

    def _files(self, rest: list[str]) -> None:
        if not rest:
            return self._send(200, {"total": len(FILES), "names": sorted(FILES)})
        if rest[0] not in FILES:
            return self._send(404, {"error": "file_not_found", "name": rest[0]})
        return self._send_bytes(200, FILES[rest[0]], "application/octet-stream", rest[0])

    def do_POST_upload(self) -> None:  # pragma: no cover - 见 _route
        return None


def _handle_upload(handler: Handler) -> None:
    """解析最简 multipart，单文件字段名 ``file``。"""
    content_type = handler.headers.get("Content-Type") or ""
    length = int(handler.headers.get("Content-Length") or 0)
    if "multipart/form-data" not in content_type:
        # 必须把 body 读干净，否则 keep-alive 连接会错位，下一个请求收到 400
        if length:
            handler.rfile.read(length)
        return handler._send(415, {"error": "unsupported_media_type"})
    boundary = content_type.split("boundary=")[-1].strip().strip('"')
    raw = handler.rfile.read(length)
    for chunk in raw.split(b"--" + boundary.encode()):
        if b'name="file"' not in chunk:
            continue
        head, _, data = chunk.partition(b"\r\n\r\n")
        filename = "upload.bin"
        for line in head.decode("latin-1").splitlines():
            if "filename=" in line:
                filename = line.split("filename=")[-1].strip().strip('"')
        FILES[filename] = data.rstrip(b"\r\n")
        return handler._send(201, {"name": filename, "size": len(FILES[filename])})
    return handler._send(422, {"error": "validation_error", "message": "缺少 file 字段"})


_original_route = Handler._route


def _route_with_upload(self: Handler, method: str) -> None:  # noqa: ANN001
    path = urlparse(self.path).path.rstrip("/")
    if method == "POST" and path == "/api/upload":
        return _handle_upload(self)
    return _original_route(self, method)


Handler._route = _route_with_upload  # type: ignore[method-assign]


@contextmanager
def serve(port: int = 0):
    """在后台线程起一个 SUT，用完自动关。``with serve() as base:``"""
    reset()
    _seed()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, real_port = httpd.server_address[:2]
    try:
        yield f"http://{host}:{real_port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    with serve(8010) as base_url:
        print(f"MiniSUT 已启动：{base_url}")
        print("按 Ctrl+C 结束")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("bye")
