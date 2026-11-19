"""真机联调用的小后端：只做两件事，收登录表单、发一张图片。

用标准库实现，避免为了跑一章再去装 Flask。
启动后配合 `adb reverse tcp:8080 tcp:8080`，手机访问 127.0.0.1:8080 就等于访问本机。
"""

from __future__ import annotations

import io
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

TOKEN = secrets.token_hex(16)
USERNAME = "justin"
PASSWORD = "123"

# 1×1 的透明 PNG，Pillow 不可用时退回它
_FALLBACK_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


def _photo_bytes() -> bytes:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return _FALLBACK_PNG

    width, height = 720, 960
    image = Image.new("RGB", (width, height), "#FFF9F6")
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / float(height)
        draw.line([(0, y), (width, y)], fill=(int(255 - 20 * ratio), int(240 - 70 * ratio), 220))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:  # 安静一点
        pass

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/login":
            self._json({"code": 404, "msg": "not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace")
        form = parse_qs(raw)
        username = (form.get("username") or [""])[0]
        password = (form.get("password") or [""])[0]
        if username == USERNAME and password == PASSWORD:
            self._json({"code": 100, "msg": "登录成功", "token": TOKEN})
        else:
            self._json({"code": 101, "msg": "用户名或密码错误"})

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/photo":
            body = _photo_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.rstrip("/") in ("/health", ""):
            self._json({"ok": True})
            return
        self._json({"code": 404, "msg": "not found"}, status=404)


class LoginServer:
    def __init__(self, port: int = 8080):
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def start(self) -> "LoginServer":
        self._server = ThreadingHTTPServer(("127.0.0.1", self.port), _Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

    def __enter__(self) -> "LoginServer":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()


if __name__ == "__main__":
    server = LoginServer().start()
    print(f"listening on {server.base_url}（Ctrl+C 退出）")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.stop()
