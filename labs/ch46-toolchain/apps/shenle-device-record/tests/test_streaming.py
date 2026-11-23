import asyncio
import json
import time
from pathlib import Path
from typing import Any

import pytest

from shenle_device_record.server import protocol
from shenle_device_record.server.streaming import (
    CONSECUTIVE_FAILURE_THRESHOLD,
    MAX_FPS,
    MIN_FPS,
    SCREENSHOT_FRAME_TIMEOUT,
    StreamController,
    StreamingMode,
    StreamingState,
)


def _decode(messages: list[str]) -> list[dict[str, Any]]:
    return [protocol.decode(m) for m in messages if m is not None]


def _payload_type(msg: dict[str, Any]) -> str | None:
    return msg.get("type") if msg else None


async def _async_dump_empty(device_id: str) -> str:
    """HierarchyFn 的 fake 实现：返回空字符串，签名是 async。"""
    return ""


class _FakeClock:
    """单调时钟 + 睡眠队列，测试可控推进时间。"""
    def __init__(self, start: float = 0.0):
        self.now_value = start
        self.sleeps: list[float] = []
        self.sleep_resume: list[asyncio.Event] = []

    def now(self) -> float:
        return self.now_value

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        # 默认：调用方把时间推进若干秒
        self.now_value += seconds


def _make_controller(tmp_path, *, screenshot_return: bytes = b"\x89PNG\r\n\x1a\n",
                     screenshot_side_effect: BaseException | None = None,
                     hierarchy: str = "<hierarchy/>",
                     screenshot_delay: float = 0.0):
    """构造一个测试用的 StreamController。所有外部依赖都是 fake。"""
    send_log: list[str] = []
    clock = _FakeClock()

    async def send(raw: str) -> None:
        send_log.append(raw)

    if screenshot_side_effect is not None:
        async def shoot(device_id: str) -> bytes:
            if screenshot_delay:
                await asyncio.sleep(0)
            raise screenshot_side_effect
    else:
        async def shoot(device_id: str) -> bytes:
            if screenshot_delay:
                await asyncio.sleep(0)
            return screenshot_return

    async def dump_hierarchy(device_id: str) -> str:
        return hierarchy

    from shenle_device_record.server import streaming as st

    state = StreamingState(
        mode=StreamingMode.REALTIME,
        target_fps=2.0,
    )
    controller = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=shoot,
        dump_hierarchy_fn=dump_hierarchy,
        output_root=str(tmp_path),
        platform="android",
        state=state,
        sleep_fn=clock.sleep,
        now_fn=clock.now,
    )
    return controller, send_log, clock, state


# --- 实时模式正常出帧 --------------------------------------------------------


@pytest.mark.asyncio
async def test_realtime_sends_frames_and_increments_seq(tmp_path):
    controller, log, clock, state = _make_controller(tmp_path)
    await controller.start()
    # 给它 3 帧的预算：2 fps 时一帧约 0.5s
    for _ in range(3):
        await asyncio.sleep(0)
    await controller.stop()
    await asyncio.sleep(0)

    msgs = _decode(log)
    frames = [m for m in msgs if _payload_type(m) == "frame"]
    assert len(frames) == 3
    assert [f["seq"] for f in frames] == [1, 2, 3]
    assert state.total_frames == 3


# --- 跳帧：上一帧还没完时跳过本帧 ----------------------------------------------


@pytest.mark.asyncio
async def test_realtime_skips_frame_when_inflight(tmp_path):
    """截图耗时比帧间隔长时，下一帧应被跳过而不是排队。

    验证两条语义：
      1. inflight=True 期间主循环跳过本帧（不是排队），所以 rounds 个回合里只能截出 <rounds 帧
      2. 循环退出后 inflight 必须被复位为 False
    另外用更慢的 shoot 真正观察 inflight=True 期间的状态，咬住"跳帧"语义。
    """
    # ---- 第一段：shoot 耗时 0.01s，5 回合只能截出 <5 帧 ----
    state = StreamingState(mode=StreamingMode.REALTIME, target_fps=20.0)  # 帧间隔 0.05s
    send_log: list[str] = []

    async def slow_shoot(device_id: str) -> bytes:
        # 真 await 让事件循环有机会调度；只推进 fake clock 不会 yield
        await asyncio.sleep(0.01)
        return b"\x89PNG"

    async def send(raw: str) -> None:
        send_log.append(raw)

    controller = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=slow_shoot,
        dump_hierarchy_fn=_async_dump_empty,
        output_root=str(tmp_path),
        platform="android",
        state=state,
        sleep_fn=asyncio.sleep,  # 用真 sleep 让帧间隔真的等
        now_fn=time.monotonic,
    )

    await controller.start()
    rounds = 5
    for _ in range(rounds):
        await asyncio.sleep(0.01)
    await controller.stop()
    await asyncio.sleep(0)

    frames = [m for m in _decode(send_log) if _payload_type(m) == "frame"]
    # 必须严格少于回合数 —— 否则说明跳帧没生效
    assert len(frames) < rounds, f"期望跳帧，但实际截到 {len(frames)} 帧"
    assert state.total_frames == len(frames)
    # 循环退出后 inflight 必须被复位
    assert state.inflight is False

    # ---- 第二段：shoot 真 await 0.5s（远超帧间隔 0.05s），观察 inflight=True ----
    state2 = StreamingState(mode=StreamingMode.REALTIME, target_fps=20.0)
    inflight_seen = {"v": False}

    async def very_slow_shoot(device_id: str) -> bytes:
        await asyncio.sleep(0.5)
        return b"\x89PNG"

    controller2 = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=very_slow_shoot,
        dump_hierarchy_fn=_async_dump_empty,
        output_root=str(tmp_path),
        platform="android",
        state=state2,
        sleep_fn=asyncio.sleep,
        now_fn=time.monotonic,
    )
    await controller2.start()
    # 等到 inflight=True 被观察到
    for _ in range(20):
        await asyncio.sleep(0.02)
        if state2.inflight:
            inflight_seen["v"] = True
            break
    await controller2.stop()
    await asyncio.sleep(0)
    assert inflight_seen["v"] is True, "没观察到 inflight=True，跳帧语义没被真正测到"
    assert state2.inflight is False


# --- 失败计数与自动降级到按需 --------------------------------------------------


@pytest.mark.asyncio
async def test_consecutive_failures_switch_to_on_demand(tmp_path):
    from shenle_device_record.server import streaming as st

    state = StreamingState(mode=StreamingMode.REALTIME, target_fps=2.0)
    send_log: list[str] = []
    clock = _FakeClock()

    async def always_fail(device_id: str) -> bytes:
        raise st.MidsceneError("device offline")

    async def send(raw: str) -> None:
        send_log.append(raw)

    controller = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=always_fail,
        dump_hierarchy_fn=_async_dump_empty,
        output_root=str(tmp_path),
        platform="android",
        state=state,
        sleep_fn=clock.sleep,
        now_fn=clock.now,
    )

    await controller.start()
    for _ in range(CONSECUTIVE_FAILURE_THRESHOLD + 2):
        await asyncio.sleep(0)
    await controller.stop()
    await asyncio.sleep(0)

    assert state.consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD
    assert state.mode == StreamingMode.ON_DEMAND
    mode_changes = [m for m in _decode(send_log) if _payload_type(m) == "mode_changed"]
    assert any(m["to"] == "on_demand" for m in mode_changes)


@pytest.mark.asyncio
async def test_single_failure_resets_on_success(tmp_path):
    controller, log, clock, state = _make_controller(tmp_path)
    # 装成第一次失败、之后成功的混合场景
    calls = {"n": 0}

    async def shoot(device_id: str) -> bytes:
        calls["n"] += 1
        from shenle_device_record.server import streaming as st
        if calls["n"] == 1:
            raise st.MidsceneError("首次失败")
        return b"\x89PNG"

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]
    await controller.start()
    for _ in range(3):
        await asyncio.sleep(0)
    await controller.stop()
    await asyncio.sleep(0)

    # 第一次失败后状态被自增；之后成功时被清零
    # 我们只断言"过程中没到阈值"，即中途没有切到 on_demand
    msgs = _decode(log)
    assert not any(m["to"] == "on_demand" for m in msgs if _payload_type(m) == "mode_changed")
    # 计数器最终应被清零
    assert state.consecutive_failures == 0


# --- 按需模式：啥也不干，等 capture -------------------------------------------


@pytest.mark.asyncio
async def test_on_demand_does_nothing_until_capture(tmp_path):
    controller, log, clock, state = _make_controller(tmp_path)
    state.mode = StreamingMode.ON_DEMAND
    await controller.start()
    for _ in range(3):
        await asyncio.sleep(0)
    await controller.stop()
    await asyncio.sleep(0)

    frames = [m for m in _decode(log) if _payload_type(m) == "frame"]
    assert frames == []


# --- 采集动作：暂停推流、截图、落盘、回 captured --------------------------------


@pytest.mark.asyncio
async def test_capture_now_writes_png_and_json(tmp_path):
    controller, log, clock, state = _make_controller(tmp_path)
    state.mode = StreamingMode.ON_DEMAND
    await controller.start()

    fake_png = b"\x89PNG\r\n\x1a\nFAKE"
    calls = {"n": 0}

    async def shoot(device_id: str) -> bytes:
        calls["n"] += 1
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    captured = await controller.capture_now(
        capture_id="cap-1",
        module="个人中心",
        func="登录功能",
        desc="通过账号密码登录",
    )

    await controller.stop()
    await asyncio.sleep(0)

    assert captured["ok"] is True
    assert captured["capture_id"] == "cap-1"
    assert "img_path" in captured and "json_path" in captured

    img_path = Path(captured["img_path"])
    json_path = Path(captured["json_path"])
    assert img_path.is_file()
    assert img_path.read_bytes() == fake_png
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert list(payload.keys()) == ["content", "img", "module", "func", "desc"]
    assert payload["module"] == "个人中心"
    assert payload["func"] == "登录功能"
    assert payload["desc"] == "通过账号密码登录"
    assert payload["content"] == "<hierarchy/>"

    # 必须有 captured 消息回给客户端
    msgs = _decode(log)
    captured_msgs = [m for m in msgs if _payload_type(m) == "captured"]
    assert any(m["capture_id"] == "cap-1" and m["ok"] is True for m in captured_msgs)


@pytest.mark.asyncio
async def test_capture_now_reports_failure_on_error(tmp_path):
    from shenle_device_record.server import streaming as st

    state = StreamingState(mode=StreamingMode.ON_DEMAND, target_fps=2.0)
    send_log: list[str] = []
    clock = _FakeClock()

    async def boom(device_id: str) -> bytes:
        raise st.MidsceneError("截图炸了")

    async def send(raw: str) -> None:
        send_log.append(raw)

    controller = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=boom,
        dump_hierarchy_fn=_async_dump_empty,
        output_root=str(tmp_path),
        platform="android",
        state=state,
        sleep_fn=clock.sleep,
        now_fn=clock.now,
    )
    await controller.start()

    captured = await controller.capture_now(
        capture_id="cap-2", module="m", func="f", desc="",
    )
    await controller.stop()
    await asyncio.sleep(0)

    assert captured["ok"] is False
    assert "截图炸了" in captured["error"]
    msgs = _decode(send_log)
    assert any(m.get("capture_id") == "cap-2" and m["ok"] is False for m in msgs
               if _payload_type(m) == "captured")


# --- 设置模式 / 帧率 ---------------------------------------------------------


@pytest.mark.asyncio
async def test_set_mode_realtime_emits_mode_changed(tmp_path):
    controller, log, clock, state = _make_controller(tmp_path)
    state.mode = StreamingMode.ON_DEMAND
    await controller.start()
    await controller.set_mode(StreamingMode.REALTIME)
    await asyncio.sleep(0)
    await controller.stop()
    await asyncio.sleep(0)

    msgs = _decode(log)
    mode_changes = [m for m in msgs if _payload_type(m) == "mode_changed"]
    assert any(m["from"] == "on_demand" and m["to"] == "realtime" for m in mode_changes)


@pytest.mark.asyncio
async def test_set_target_fps_clamps_to_range(tmp_path):
    controller, _, _, state = _make_controller(tmp_path)
    await controller.start()
    try:
        controller.set_target_fps(-1)
        assert state.target_fps == MIN_FPS
        controller.set_target_fps(99)
        assert state.target_fps == MAX_FPS
        controller.set_target_fps(2.5)
        assert state.target_fps == 2.5
    finally:
        await controller.stop()
        await asyncio.sleep(0)


# --- 单帧超时不影响后续帧（midscene 偶尔超时不会让推流卡死） -------------------


@pytest.mark.asyncio
async def test_take_screenshot_timeout_does_not_hang_loop(tmp_path):
    """截图抛 MidsceneError 后 inflight 必须被复位，连续失败 3 次后切到按需。

    旧版 fake 只推进 fake clock 但不抛异常，SCREENSHOT_FRAME_TIMEOUT 完全没被走到。
    现在 fake shoot 真抛 MidsceneError，验证 Important 1 修复后两种异常走同一路径。
    """
    from shenle_device_record.server import streaming as st

    state = StreamingState(mode=StreamingMode.REALTIME, target_fps=2.0)
    send_log: list[str] = []

    async def always_fail(device_id: str) -> bytes:
        # 真抛 MidsceneError —— 模拟单帧超时
        raise st.MidsceneError(f"单帧截图超时（{SCREENSHOT_FRAME_TIMEOUT}s）")

    async def send(raw: str) -> None:
        send_log.append(raw)

    controller = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=always_fail,
        dump_hierarchy_fn=_async_dump_empty,
        output_root=str(tmp_path),
        platform="android",
        state=state,
        sleep_fn=asyncio.sleep,
        now_fn=time.monotonic,
    )

    await controller.start()
    # 让协程跑到 ≥3 次失败（fps=2 → 帧间隔 0.5s，需要 ≥1.5s 调度窗口）
    for _ in range(60):
        await asyncio.sleep(0.05)
    await controller.stop()
    await asyncio.sleep(0)

    # 失败次数必须到阈值
    assert state.consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD
    # 必须已切到按需
    assert state.mode == StreamingMode.ON_DEMAND
    # inflight 必须被复位（没卡死）
    assert state.inflight is False
    # 必须有 mode_changed 消息
    msgs = _decode(send_log)
    mode_changes = [m for m in msgs if _payload_type(m) == "mode_changed"]
    assert any(m["to"] == "on_demand" for m in mode_changes)


@pytest.mark.asyncio
async def test_non_midscene_exception_switches_to_on_demand(tmp_path):
    """非 MidsceneError 异常（如 asyncio.TimeoutError）也应归一为 MidsceneError，
    走 ≥3 切按需的同一路径 —— Important 1 修复的核心保证。

    旧版 except Exception 分支只发 ERROR 不切按需，这条测试是反向验证的关键。
    """
    state = StreamingState(mode=StreamingMode.REALTIME, target_fps=2.0)
    send_log: list[str] = []

    async def always_timeout(device_id: str) -> bytes:
        # 抛非 MidsceneError 异常 —— 走 except Exception 分支
        raise asyncio.TimeoutError("screenshot timed out")

    async def send(raw: str) -> None:
        send_log.append(raw)

    controller = StreamController(
        device_id="ABC",
        send_message=send,
        take_screenshot_fn=always_timeout,
        dump_hierarchy_fn=_async_dump_empty,
        output_root=str(tmp_path),
        platform="android",
        state=state,
        sleep_fn=asyncio.sleep,
        now_fn=time.monotonic,
    )

    await controller.start()
    # 让协程跑到 ≥3 次失败（fps=2 → 帧间隔 0.5s，需要 ≥1.5s 调度窗口）
    for _ in range(60):
        await asyncio.sleep(0.05)
    await controller.stop()
    await asyncio.sleep(0)

    assert state.consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD
    assert state.mode == StreamingMode.ON_DEMAND
    assert state.inflight is False
    msgs = _decode(send_log)
    mode_changes = [m for m in msgs if _payload_type(m) == "mode_changed"]
    assert any(m["to"] == "on_demand" for m in mode_changes)


# --- 同一 controller 内多次采集共享 batch_id（产品需求：一次 serve 会话=一个批次）


@pytest.mark.asyncio
async def test_capture_now_reuses_batch_id_across_calls(tmp_path):
    """同一 serve 会话内多次采集必须落到同一批次目录；重启 serve 才换批次。"""
    controller, _log, _clock, _state = _make_controller(tmp_path)
    await controller.start()
    fake_png = b"\x89PNG\r\n\x1a\nFAKE"

    async def shoot(_device_id):
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    captured1 = await controller.capture_now(capture_id="c1", module="m", func="f", desc="")
    captured2 = await controller.capture_now(capture_id="c2", module="m", func="f", desc="")
    captured3 = await controller.capture_now(capture_id="c3", module="m", func="f", desc="")
    await controller.stop()
    await asyncio.sleep(0)

    # 三个 captured 必须在同一批次目录
    dir1 = Path(captured1["json_path"]).parent.parent.parent
    dir2 = Path(captured2["json_path"]).parent.parent.parent
    dir3 = Path(captured3["json_path"]).parent.parent.parent
    assert dir1 == dir2 == dir3, (
        f"同一 controller 内三次采集应共享 batch_id，实际："
        f"{dir1.name}, {dir2.name}, {dir3.name}"
    )

    # 序号 001/002/003 依次递增
    assert captured1["seq"] == 1
    assert captured2["seq"] == 2
    assert captured3["seq"] == 3


@pytest.mark.asyncio
async def test_capture_now_batch_id_stable_under_clock_jump(tmp_path):
    """同一 controller 即便"时间过了一秒"也仍共享批次（不被 generate_batch_id 时钟影响）。"""
    import time as time_mod
    from unittest.mock import patch
    controller, _log, _clock, _state = _make_controller(tmp_path)
    await controller.start()

    fake_png = b"\x89PNG"

    async def shoot(_d):
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    # 第一次采集锁定 batch_id
    captured1 = await controller.capture_now(capture_id="c1", module="m", func="f", desc="")
    first_batch_id = controller._batch_id
    # 把 generate_batch_id 桩成永远返回新值，模拟"过了 N 秒"
    counter = {"n": 0}
    def fake_gen(now=None):
        counter["n"] += 1
        return f"DIFFERENT-{counter['n']}"
    with patch("shenle_device_record.paths.generate_batch_id", side_effect=fake_gen):
        captured2 = await controller.capture_now(capture_id="c2", module="m", func="f", desc="")

    await controller.stop()
    await asyncio.sleep(0)

    # 第二次应仍用第一次的 batch_id（不是 DIFFERENT-1）
    assert controller._batch_id == first_batch_id
    dir1 = Path(captured1["json_path"]).parent.parent.parent
    dir2 = Path(captured2["json_path"]).parent.parent.parent
    assert dir1 == dir2


# --- AI 分析：capture_now 的 ai_analyze 参数


@pytest.mark.asyncio
async def test_capture_now_ai_analyze_disabled_writes_no_ai_fields(tmp_path):
    """ai_analyze=False（默认）：JSON 不含 AI 字段。"""
    controller, _log, _clock, _state = _make_controller(tmp_path)
    await controller.start()
    fake_png = b"\x89PNG\r\n\x1a\n"

    async def shoot(_d):
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    captured = await controller.capture_now(
        capture_id="c", module="m", func="f", desc="",
    )
    await controller.stop()
    await asyncio.sleep(0)

    payload = json.loads(Path(captured["json_path"]).read_text(encoding="utf-8"))
    # 原五字段在，AI 三个字段不在
    assert list(payload.keys()) == ["content", "img", "module", "func", "desc"]
    assert "interface_desc" not in payload


@pytest.mark.asyncio
async def test_capture_now_ai_analyze_enabled_writes_three_fields(tmp_path, monkeypatch):
    """ai_analyze=True + AI 配置存在 + 调用成功：JSON 含三个 AI 字段。"""
    from shenle_device_record import ai as ai_mod

    monkeypatch.setattr(
        ai_mod,
        "load_config",
        lambda env_path=None: ai_mod.AIConfig(
            api_key="sk", base_url="https://x.com/v1", model="gpt-4o",
        ),
    )
    monkeypatch.setattr(
        ai_mod,
        "analyze_image",
        lambda config, png_bytes: {
            "interface_desc": "登录页",
            "layout_desc": "上下布局",
            "elements_desc": ["账号输入框", "密码输入框", "登录按钮"],
        },
    )

    controller, _log, _clock, _state = _make_controller(tmp_path)
    await controller.start()
    fake_png = b"\x89PNG\r\n\x1a\n"

    async def shoot(_d):
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    captured = await controller.capture_now(
        capture_id="c", module="m", func="f", desc="", ai_analyze=True,
    )
    await controller.stop()
    await asyncio.sleep(0)

    payload = json.loads(Path(captured["json_path"]).read_text(encoding="utf-8"))
    assert list(payload.keys()) == [
        "content", "img", "module", "func", "desc",
        "interface_desc", "layout_desc", "elements_desc",
    ]
    assert payload["interface_desc"] == "登录页"
    assert payload["layout_desc"] == "上下布局"
    assert payload["elements_desc"] == ["账号输入框", "密码输入框", "登录按钮"]


@pytest.mark.asyncio
async def test_capture_now_ai_analyze_no_config_writes_nulls(tmp_path, monkeypatch):
    """ai_analyze=True 但 .env 缺配置：AI 三个字段写 null，截图与 UI 层级照常落盘。"""
    from shenle_device_record import ai as ai_mod

    monkeypatch.setattr(ai_mod, "load_config", lambda env_path=None: None)

    controller, _log, _clock, _state = _make_controller(tmp_path)
    await controller.start()
    fake_png = b"\x89PNG\r\n\x1a\n"

    async def shoot(_d):
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    captured = await controller.capture_now(
        capture_id="c", module="m", func="f", desc="", ai_analyze=True,
    )
    await controller.stop()
    await asyncio.sleep(0)

    assert captured["ok"] is True, "缺 AI 配置不应让采集失败"
    payload = json.loads(Path(captured["json_path"]).read_text(encoding="utf-8"))
    assert payload["interface_desc"] is None
    assert payload["layout_desc"] is None
    assert payload["elements_desc"] is None


@pytest.mark.asyncio
async def test_capture_now_ai_analyze_call_failure_writes_nulls(tmp_path, monkeypatch):
    """ai_analyze=True + 有配置但调用失败：三个字段写 null，采集仍 ok。"""
    from shenle_device_record import ai as ai_mod

    monkeypatch.setattr(
        ai_mod,
        "load_config",
        lambda env_path=None: ai_mod.AIConfig(
            api_key="sk", base_url="https://x.com/v1", model="gpt-4o",
        ),
    )
    monkeypatch.setattr(ai_mod, "analyze_image", lambda config, png_bytes: None)

    controller, _log, _clock, _state = _make_controller(tmp_path)
    await controller.start()
    fake_png = b"\x89PNG\r\n\x1a\n"

    async def shoot(_d):
        return fake_png

    controller._take_screenshot_fn = shoot  # type: ignore[attr-defined]

    captured = await controller.capture_now(
        capture_id="c", module="m", func="f", desc="", ai_analyze=True,
    )
    await controller.stop()
    await asyncio.sleep(0)

    assert captured["ok"] is True
    payload = json.loads(Path(captured["json_path"]).read_text(encoding="utf-8"))
    assert payload["interface_desc"] is None
    assert payload["layout_desc"] is None
    assert payload["elements_desc"] is None