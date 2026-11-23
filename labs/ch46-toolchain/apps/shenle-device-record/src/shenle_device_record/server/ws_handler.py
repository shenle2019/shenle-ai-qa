"""一个 WebSocket 连接 = 一个 WSHandler。

负责：
- 连上立即发 hello
- 启 StreamController 跑推流
- 入站消息按 protocol.decode → 分发到 controller 或自己处理
- 心跳超时检测（pong 时间戳）
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Awaitable, Callable

from shenle_device_record.server import protocol
from shenle_device_record.server.streaming import (
    StreamController,
    StreamingMode,
)

LOG = logging.getLogger("shenle_device_record.server.ws_handler")

WS_HEARTBEAT_TIMEOUT = 10.0

ScreenshotFn = Callable[[str], Awaitable[bytes]]
HierarchyFn = Callable[[str], Awaitable[str]]


class WSHandler:
    def __init__(
        self,
        websocket,
        device_id: str,
        output_root: str,
        platform: str = "android",
        take_screenshot_fn: ScreenshotFn | None = None,
        dump_hierarchy_fn: HierarchyFn | None = None,
        initial_frame_rate: float = 1.0,
    ) -> None:
        self._ws = websocket
        self.device_id = device_id
        self._output_root = output_root
        self._platform = platform
        self._last_pong = time.monotonic()

        self.controller = StreamController(
            device_id=device_id,
            send_message=self._send,
            take_screenshot_fn=take_screenshot_fn,
            dump_hierarchy_fn=dump_hierarchy_fn,
            output_root=output_root,
            platform=platform,
        )
        self.controller.set_target_fps(initial_frame_rate)
        self._closed = False

    async def serve(self) -> None:
        # 连上发 hello
        await self._send(protocol.encode(
            protocol.HELLO,
            platform=self._platform,
            screen_width=0,
            screen_height=0,
            frame_rate=self.controller.state.target_fps,
        ))

        await self.controller.start()

        try:
            while not self._closed:
                # 心跳超时检测
                if time.monotonic() - self._last_pong > WS_HEARTBEAT_TIMEOUT:
                    LOG.warning("客户端 %s 心跳超时", self.device_id)
                    break
                try:
                    raw = await asyncio.wait_for(self._ws.recv(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                except (ConnectionError, asyncio.CancelledError):
                    break
                await self._handle_raw(raw)
        finally:
            await self.controller.stop()

    async def _send(self, raw: str) -> None:
        try:
            await self._ws.send(raw)
        except Exception as exc:
            LOG.warning("send 失败：%s", exc)

    async def _handle_raw(self, raw: Any) -> None:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        if not isinstance(raw, str):
            return
        payload = protocol.decode(raw)
        if payload is None:
            LOG.warning("收到非合法 JSON，忽略：%r", raw[:120])
            return
        if not protocol.is_valid_inbound(payload):
            LOG.warning("收到未知 type=%r，忽略", payload.get("type"))
            return
        try:
            await self._dispatch(payload)
        except Exception as exc:
            LOG.exception("处理入站消息失败：%s", exc)

    async def _dispatch(self, payload: dict) -> None:
        kind = payload.get("type")
        if kind == protocol.PONG:
            # 客户端的 pong（响应服务端的 ping，目前不用，但收到就刷时间戳）
            self._last_pong = time.monotonic()
            return
        if kind == protocol.PING:
            # 客户端发 ping 心跳 → 立即回 pong + 刷时间戳
            self._last_pong = time.monotonic()
            await self._send(protocol.encode(protocol.PONG))
            return
        if kind == protocol.SET_MODE:
            mode_raw = payload.get("mode")
            if mode_raw not in ("realtime", "on_demand"):
                LOG.warning("set_mode 收到非法 mode=%r", mode_raw)
                return
            await self.controller.set_mode(StreamingMode(mode_raw))
            return
        if kind == protocol.SET_FRAME_RATE:
            fps = payload.get("fps")
            if not isinstance(fps, (int, float)):
                LOG.warning("set_frame_rate fps 非数字：%r", fps)
                return
            self.controller.set_target_fps(float(fps))
            return
        if kind == protocol.CAPTURE:
            await self._handle_capture(payload)
            return

    async def _handle_capture(self, payload: dict) -> None:
        capture_id = str(payload.get("capture_id") or "")
        module = str(payload.get("module") or "")
        func = str(payload.get("func") or "")
        desc = str(payload.get("desc") or "")
        # ai_analyze 是 checkbox 状态：true 时调用 AI 描述界面。
        # 缺 .env 配置或 AI 调用失败都不影响截图与 JSON 落盘。
        ai_analyze = bool(payload.get("ai_analyze"))
        # 关键：用 create_task 让 capture_now 在后台跑，**不等它**。
        # 否则 AI 调用 30s 期间 ws 协程被阻塞，前端 ping 不响应，10s 后
        # 心跳超时 → 服务自退。
        # capture_now 内部仍负责把 captured 消息发回客户端。
        asyncio.create_task(
            self.controller.capture_now(
                capture_id=capture_id,
                module=module,
                func=func,
                desc=desc,
                ai_analyze=ai_analyze,
            )
        )
