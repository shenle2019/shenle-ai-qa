"""HTTP 静态服务 + WebSocket 端口共享。

`websockets.serve(..., process_request=...)` 在收到 HTTP 请求时同步回调本模块，
我们手动返 HTML / 静态资源响应；`/ws` 由 `http_process_request` 返回 `None`，
让 websockets 库走 WebSocket 升级分支。
"""
from __future__ import annotations

import asyncio
import mimetypes
from pathlib import Path
from typing import Any, Awaitable, Callable

import websockets
from websockets.datastructures import Headers
from websockets.http11 import Response

# 单条 WebSocket 消息上限（10MB），防止恶意客户端发送超大帧耗尽内存。
WS_MAX_MESSAGE_SIZE = 10 * 1024 * 1024

# 常用 status 对应的 reason phrase。websockets.http11.Response 要求显式给 reason。
_REASON_PHRASES = {
    200: "OK",
    404: "Not Found",
}

CONTENT_TYPES: dict[str, str] = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml; charset=utf-8",
    ".ico": "image/x-icon",
}


def _content_type_for(path: Path) -> str:
    # 内置表优先，保证 .js → application/javascript 等行为在不同 Windows 环境一致；
    # mimetypes 仅作为兜底。
    suffix = path.suffix.lower()
    if suffix in CONTENT_TYPES:
        return CONTENT_TYPES[suffix]
    guess, _ = mimetypes.guess_type(str(path))
    return guess or "application/octet-stream"


def _to_response(status: int, headers_list: list[tuple[str, str]], body: bytes) -> Response:
    """把 (status, headers, body) 元组转成 websockets.http11.Response。

    websockets 14+ 的 `process_request` 回调必须返回 `Optional[Response]`。
    """
    reason = _REASON_PHRASES.get(status, "")
    return Response(status, reason, Headers(headers_list), body)


class StaticHandler:
    def __init__(self, static_root: str | Path) -> None:
        self._root = Path(static_root).expanduser().resolve()

    def _resolve(self, url_path: str) -> Path | None:
        """把 URL 路径解析为 static_root 下的绝对路径。越界返回 None。"""
        # 去掉 query / fragment
        clean = url_path.split("?", 1)[0].split("#", 1)[0]
        # 不允许绝对路径
        if clean.startswith("//") or (len(clean) >= 2 and clean[1] == ":"):
            return None
        # 拼接并解析为绝对路径
        candidate = (self._root / clean.lstrip("/")).resolve()
        # 防穿越：必须仍在 root 下
        try:
            candidate.relative_to(self._root)
        except ValueError:
            return None
        return candidate

    def render(self, url_path: str) -> tuple[int, list[tuple[str, str]], bytes]:
        """返回 (status, headers, body)。

        `/ws` 返回 (101, [], b"") 作为"走升级"的哨兵；
        `http_process_request` 看到该 status 会把整体转换为 None，
        让 websockets 库接管并发起 WebSocket 升级。
        其他路径：命中文件 → 200 + Content-Type + Content-Length；
        未命中 → 404 text/plain + Content-Length。
        """
        WS_UPGRADE = 101
        HTTP_NOT_FOUND = 404
        HTTP_OK = 200

        if url_path == "/ws":
            return (WS_UPGRADE, [], b"")

        if url_path in ("/", "/index.html"):
            target = self._root / "index.html"
        else:
            target = self._resolve(url_path)

        if target is None or not target.is_file():
            body = b"404 Not Found"
            return (
                HTTP_NOT_FOUND,
                [
                    ("Content-Type", "text/plain; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                ],
                body,
            )

        body = target.read_bytes()
        return (
            HTTP_OK,
            [
                ("Content-Type", _content_type_for(target)),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-cache"),
            ],
            body,
        )


async def http_process_request(connection, request, static_handler: StaticHandler):
    """websockets 库的 process_request 回调。

    websockets 14+ 要求返回 `Optional[Response]`：
      - 返回 `None`：交给库处理（即触发 WebSocket 升级）。
      - 返回 `Response`：库用 `Response.status_code` / `Response.headers` / `Response.body`
        写 HTTP 响应。

    我们内部用 `StaticHandler.render()` 输出元组，再 `_to_response()` 转成 Response。
    """
    try:
        path = request.path
    except AttributeError:
        path = "/"
    response = static_handler.render(path)
    if response[0] == 101:  # WS_UPGRADE 哨兵
        return None
    status, headers, body = response
    return _to_response(status, headers, body)


async def run_server(
    host: str,
    port: int,
    ws_handler_factory: Callable[[Any], Awaitable[None]],
    static_root: str | Path,
) -> None:
    """启动 HTTP 静态服务 + WebSocket 服务（共享端口）。

    每来一个 WebSocket 连接，websockets 库调一次 `ws_handler_factory(websocket)`。
    HTTP 请求由 `http_process_request` 路由到 `StaticHandler.render`。
    函数通过 `await asyncio.Future()` 永久阻塞，直到外部 cancel / 关闭 loop。
    """
    static_handler = StaticHandler(static_root)

    async def proc_req(connection, request):
        return await http_process_request(connection, request, static_handler)

    async with websockets.serve(
        ws_handler_factory,
        host,
        port,
        process_request=proc_req,
        max_size=WS_MAX_MESSAGE_SIZE,
    ):
        await asyncio.Future()  # 永久服务，直到外部取消。