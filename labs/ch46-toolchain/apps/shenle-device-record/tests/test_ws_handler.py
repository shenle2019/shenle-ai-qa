import asyncio
from unittest.mock import AsyncMock

import pytest

from shenle_device_record.server import protocol
from shenle_device_record.server.streaming import (
    MIN_FPS,
    MAX_FPS,
    StreamingMode,
    StreamingState,
)
from shenle_device_record.server.ws_handler import WSHandler


def _decode_msgs(raw_list):
    out = []
    for r in raw_list:
        if r is None:
            continue
        msg = protocol.decode(r)
        if msg is not None:
            out.append(msg)
    return out


def _fake_websocket(send_log: list, recv_queue: asyncio.Queue):
    """构造一个最小可用的 WebSocket fake：send 入 log、recv 出 queue。
    收到哨兵 None 时抛 ConnectionError，让 handler 走 break 路径立即退出。
    """

    class FakeWS:
        async def send(self, raw):
            send_log.append(raw)

        async def recv(self):
            item = await recv_queue.get()
            if item is None:
                raise ConnectionError("closed")
            return item

        async def close(self):
            pass

    return FakeWS()


def _async_h(xml: str):
    """构造一个返回固定 xml 的 async HierarchyFn。

    dump_hierarchy_fn 现在必须是 async（H3 修复）；单测里这个 helper 让我们
    用 `dump_hierarchy_fn=_async_h("<h/>")` 一行代替每个测试手写 async def。
    """

    async def _fn(device_id: str) -> str:
        return xml

    return _fn


@pytest.mark.asyncio
async def test_serve_sends_hello_and_accepts_pong(tmp_path):
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()

    ws = _fake_websocket(send_log, recv_q)
    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=_async_h("<h/>"),
    )

    serve_task = asyncio.create_task(handler.serve())
    # 让 hello 发出去
    await asyncio.sleep(0.05)

    msgs = _decode_msgs(send_log)
    hellos = [m for m in msgs if m.get("type") == "hello"]
    assert len(hellos) == 1
    hello = hellos[0]
    assert hello["platform"] == "android"
    assert "frame_rate" in hello

    # 发一个 pong，不应报错
    await recv_q.put(protocol.encode("pong"))
    await asyncio.sleep(0.05)

    # 让 handler 退出
    await recv_q.put(None)
    await serve_task


@pytest.mark.asyncio
async def test_serve_handles_set_mode(tmp_path):
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=_async_h(""),
    )

    serve_task = asyncio.create_task(handler.serve())
    await asyncio.sleep(0.05)

    await recv_q.put(protocol.encode("set_mode", mode="on_demand"))
    await asyncio.sleep(0.05)

    msgs = _decode_msgs(send_log)
    mode_changes = [m for m in msgs if m.get("type") == "mode_changed"]
    assert any(m["to"] == "on_demand" for m in mode_changes)

    await recv_q.put(None)
    await serve_task


@pytest.mark.asyncio
async def test_serve_responds_to_ping_with_pong(tmp_path):
    """前端发 ping 心跳，服务端必须立即回 pong —— 否则前端 10s 心跳超时。"""
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=lambda d: "",
    )

    serve_task = asyncio.create_task(handler.serve())
    # 等 hello 到达
    for _ in range(20):
        if any(m.startswith('{"type":"hello"') for m in send_log):
            break
        await asyncio.sleep(0.05)

    await recv_q.put(protocol.encode("ping"))
    # 等 pong
    for _ in range(40):
        if any(m.startswith('{"type":"pong"') for m in send_log):
            break
        await asyncio.sleep(0.05)

    msgs = _decode_msgs(send_log)
    pongs = [m for m in msgs if m.get("type") == "pong"]
    assert len(pongs) >= 1, f"服务端必须对 ping 回 pong，实际：{msgs!r}"

    await recv_q.put(None)
    try:
        await asyncio.wait_for(serve_task, timeout=1.0)
    except (asyncio.TimeoutError, ConnectionError):
        pass


@pytest.mark.asyncio
async def test_handle_capture_does_not_block_ping_response(tmp_path):
    """AI 慢调用期间（capture_now 阻塞），ws 协程仍必须能响应 ping。

    模拟：让 controller.capture_now 睡 2 秒（模拟 AI 30s 调用的极端情形）。
    _handle_capture 收到命令后**必须**用后台 task 跑 capture_now，否则 ws 协程被
    阻塞期间前端 ping 拿不到 pong → 10s 心跳超时 → 服务自退。
    """
    import asyncio
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=lambda d: "",
    )

    # 把 controller.capture_now 替换为睡 2 秒的版本
    async def slow_capture(**kwargs):
        await asyncio.sleep(2)

    handler.controller.capture_now = slow_capture  # type: ignore[assignment]

    serve_task = asyncio.create_task(handler.serve())
    # 等 hello
    for _ in range(20):
        if any(m.startswith('{"type":"hello"') for m in send_log):
            break
        await asyncio.sleep(0.05)

    # 发 capture 命令（capture_now 会睡 2 秒）
    await recv_q.put(protocol.encode("capture", capture_id="c1"))
    await asyncio.sleep(0.2)  # capture_now 已经在后台跑

    # 在 capture_now 阻塞期间发 ping —— 必须能在 1 秒内拿到 pong
    await recv_q.put(protocol.encode("ping"))
    for _ in range(20):
        if any(m.startswith('{"type":"pong"') for m in send_log):
            break
        await asyncio.sleep(0.05)

    msgs = _decode_msgs(send_log)
    pongs = [m for m in msgs if m.get("type") == "pong"]
    assert len(pongs) >= 1, (
        f"capture_now 阻塞期间 ws 协程必须仍能响应 ping，实际：{msgs!r}"
    )

    await recv_q.put(None)
    try:
        await asyncio.wait_for(serve_task, timeout=3.0)
    except (asyncio.TimeoutError, ConnectionError):
        pass


@pytest.mark.asyncio
async def test_serve_handles_set_frame_rate(tmp_path):
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=_async_h(""),
    )

    serve_task = asyncio.create_task(handler.serve())
    await asyncio.sleep(0.05)

    # 极小值应被 clamp 到 MIN_FPS
    await recv_q.put(protocol.encode("set_frame_rate", fps=-5))
    await asyncio.sleep(0.05)
    assert handler.controller.state.target_fps == MIN_FPS  # 强断言：必须被 clamp 到 0.5

    await recv_q.put(None)
    await serve_task


@pytest.mark.asyncio
async def test_serve_handles_capture_command(tmp_path):
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG\r\n\x1a\n"),
        dump_hierarchy_fn=_async_h("<h/>"),
    )

    serve_task = asyncio.create_task(handler.serve())
    await asyncio.sleep(0.01)

    await recv_q.put(protocol.encode(
        "capture", capture_id="cap-1", module="m", func="f", desc="d", ai_analyze=False
    ))
    # 给 capture_now 一点时间
    await asyncio.sleep(0.1)

    msgs = _decode_msgs(send_log)
    captured = [m for m in msgs if m.get("type") == "captured"]
    assert any(m["capture_id"] == "cap-1" and m["ok"] for m in captured)

    await recv_q.put(None)
    await serve_task


@pytest.mark.asyncio
async def test_serve_ignores_unknown_type_and_bad_json(tmp_path, caplog):
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=_async_h(""),
    )

    serve_task = asyncio.create_task(handler.serve())
    await asyncio.sleep(0.05)

    # 未知 type、坏 JSON、空字符串：handler 不崩、不抛回客户端
    await recv_q.put('{"type": "weird", "x": 1}')
    await recv_q.put("not json")
    await recv_q.put("")
    await recv_q.put(protocol.encode("pong"))  # 已知合法，确保没被前面的乱数据搅乱
    await asyncio.sleep(0.05)

    # 最后再收一次 hello 仍发得出（说明 handler 还在）
    msgs = _decode_msgs(send_log)
    assert any(m.get("type") == "hello" for m in msgs)

    await recv_q.put(None)
    await serve_task


@pytest.mark.asyncio
async def test_serve_does_not_raise_on_close(tmp_path):
    """测试 harness 在外部关掉 WS 时，serve 不应抛异常。"""
    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()

    class ClosedWS:
        async def send(self, raw):
            send_log.append(raw)

        async def recv(self):
            raise ConnectionError("closed by test")

        async def close(self):
            pass

    handler = WSHandler(
        websocket=ClosedWS(),
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=_async_h(""),
    )
    # 不应抛
    await handler.serve()


@pytest.mark.asyncio
async def test_serve_exits_on_heartbeat_timeout(tmp_path):
    """WS_HEARTBEAT_TIMEOUT=10.0 是硬约束；若客户端长时间无 pong，serve() 必须立刻退出。

    通过把 `_last_pong` 拨回到 11 秒前，首轮 while 即可触发 break 分支：
    - 退出耗时 < 3 秒（远小于 WS_HEARTBEAT_TIMEOUT=10.0，证明是首轮 break）
    - controller 任务已 done
    """
    import time

    send_log: list[str] = []
    recv_q: asyncio.Queue = asyncio.Queue()
    ws = _fake_websocket(send_log, recv_q)

    handler = WSHandler(
        websocket=ws,
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        take_screenshot_fn=AsyncMock(return_value=b"\x89PNG"),
        dump_hierarchy_fn=_async_h(""),
    )

    # 把上一次 pong 时间戳拨到 11 秒前 → 首轮 while 立刻 break
    handler._last_pong = time.monotonic() - 11.0

    start = time.monotonic()
    await handler.serve()
    elapsed = time.monotonic() - start

    assert elapsed < 3.0, f"心跳超时未在首轮 break，耗时 {elapsed:.2f}s"
    assert handler.controller._task is not None
    assert handler.controller._task.done()
