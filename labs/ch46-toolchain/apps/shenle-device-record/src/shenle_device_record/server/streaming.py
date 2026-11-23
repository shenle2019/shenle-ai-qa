"""推流协程：实时模式循环截图、按需模式等待、失败降级。

所有时间与 IO 抽象成可注入函数，单测可同步、确定性地跑。
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Awaitable, Callable

from shenle_device_record import midscene, paths
from shenle_device_record.server import protocol

# 暴露给单测使用：测试通过 `from shenle_device_record.server import streaming as st`
# 然后 `st.MidsceneError(...)` 来构造失败场景。
MidsceneError = midscene.MidsceneError

LOG = logging.getLogger("shenle_device_record.server.streaming")

SCREENSHOT_FRAME_TIMEOUT = 10.0
CONSECUTIVE_FAILURE_THRESHOLD = 3
MIN_FPS = 0.5
MAX_FPS = 10.0


class StreamingMode(str, Enum):
    REALTIME = "realtime"
    ON_DEMAND = "on_demand"


@dataclass
class StreamingState:
    mode: StreamingMode = StreamingMode.REALTIME
    target_fps: float = 1.0
    inflight: bool = False
    consecutive_failures: int = 0
    pause_for_capture: bool = False
    total_frames: int = 0
    last_error: str | None = None
    last_capture_seq: int = 0


ScreenshotFn = Callable[[str], Awaitable[bytes]]
HierarchyFn = Callable[[str], Awaitable[str]]
SendFn = Callable[[str], Awaitable[None]]
SleepFn = Callable[[float], Awaitable[None]]
NowFn = Callable[[], float]


class StreamController:
    def __init__(
        self,
        device_id: str,
        send_message: SendFn,
        take_screenshot_fn: ScreenshotFn | None = None,
        dump_hierarchy_fn: HierarchyFn | None = None,
        output_root: str = ".",
        platform: str = "android",
        state: StreamingState | None = None,
        sleep_fn: SleepFn | None = None,
        now_fn: NowFn | None = None,
    ) -> None:
        self.device_id = device_id
        self._send = send_message
        self._take_screenshot_fn = take_screenshot_fn or self._default_screenshot
        self._dump_hierarchy_fn = dump_hierarchy_fn or self._default_dump_hierarchy
        self._output_root = output_root
        self._platform = platform
        self.state = state or StreamingState()
        self._sleep = sleep_fn or asyncio.sleep
        self._now = now_fn or time.monotonic

        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None
        # 同一 controller 实例（= 同一 serve 会话）内多次采集共享同一批次号，
        # 在第一次 capture_now 时算出来。重启 serve 自然得到新批次号。
        self._batch_id: str | None = None

    def _ensure_batch_id(self) -> str:
        """第一次采集时算 batch_id 并缓存，后续采集复用。"""
        if self._batch_id is None:
            self._batch_id = paths.generate_batch_id()
        return self._batch_id

    # ---------- 默认 screenshot 包装：调 midscene、走线程池、加超时 ----------

    async def _default_screenshot(self, device_id: str) -> bytes:
        try:
            png_path = await asyncio.wait_for(
                asyncio.to_thread(midscene.take_screenshot, device_id),
                timeout=SCREENSHOT_FRAME_TIMEOUT,
            )
        except asyncio.TimeoutError as exc:
            raise midscene.MidsceneError(
                f"单帧截图超时（{SCREENSHOT_FRAME_TIMEOUT}s）"
            ) from exc
        png_path = Path(png_path)
        try:
            return png_path.read_bytes()
        finally:
            # midscene 写的临时文件，归我们清掉；missing_ok=True 兜底
            # 万一文件已被其他流程删除。
            try:
                png_path.unlink(missing_ok=True)
            except OSError:
                pass

    async def _default_dump_hierarchy(self, device_id: str) -> str:
        """默认实现：在线程池里跑同步 midscene.dump_hierarchy，避免阻塞事件循环。"""
        return await asyncio.to_thread(midscene.dump_hierarchy, device_id)

    # ---------- 生命周期 ----------

    async def start(self) -> None:
        self._stop_event.clear()
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="streaming")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None and not self._task.done():
            try:
                await asyncio.wait_for(self._task, timeout=2.0)
            except asyncio.TimeoutError:
                self._task.cancel()

    # ---------- 主循环 ----------

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            # 让出事件循环：测试用 FakeClock sleep 时不会真的 yield，
            # 必须显式 await asyncio.sleep(0) 才能让 stop() / capture_now() 拿到调度机会。
            await asyncio.sleep(0)
            if self.state.mode == StreamingMode.ON_DEMAND:
                try:
                    await self._sleep(0.1)
                except asyncio.CancelledError:
                    return
                continue
            # realtime
            if self.state.pause_for_capture or self.state.inflight:
                try:
                    await self._sleep(0.05)
                except asyncio.CancelledError:
                    return
                continue

            self.state.inflight = True
            loop_start = self._now()
            try:
                png_bytes = await self._take_screenshot_fn(self.device_id)
                self.state.total_frames += 1
                self.state.consecutive_failures = 0
                self.state.last_error = None
                await self._send_frame(png_bytes, seq=self.state.total_frames)
            except midscene.MidsceneError as exc:
                self.state.consecutive_failures += 1
                self.state.last_error = str(exc)
                if self.state.consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                    if self.state.mode != StreamingMode.ON_DEMAND:
                        prev = self.state.mode
                        self.state.mode = StreamingMode.ON_DEMAND
                        await self._send_mode_changed(prev, StreamingMode.ON_DEMAND,
                                                      reason=f"连续失败 {self.state.consecutive_failures} 次")
                else:
                    await self._send_message(protocol.ERROR, message=str(exc))
            except Exception as exc:  # 任何非 Midscene 异常：归一为 MidsceneError，统一计数 / 切模式
                if not isinstance(exc, midscene.MidsceneError):
                    exc = midscene.MidsceneError(f"推流出错：{exc}")
                self.state.consecutive_failures += 1
                self.state.last_error = str(exc)
                if self.state.consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                    if self.state.mode != StreamingMode.ON_DEMAND:
                        prev = self.state.mode
                        self.state.mode = StreamingMode.ON_DEMAND
                        await self._send_mode_changed(prev, StreamingMode.ON_DEMAND,
                                                      reason=f"连续失败 {self.state.consecutive_failures} 次")
                else:
                    await self._send_message(protocol.ERROR, message=str(exc))
            finally:
                self.state.inflight = False

            if self.state.consecutive_failures >= CONSECUTIVE_FAILURE_THRESHOLD:
                # 已切到按需，不再 sleep；下一轮外层走按需分支
                continue

            elapsed = self._now() - loop_start
            interval = max(0.0, 1.0 / self.state.target_fps - elapsed)
            if interval > 0:
                try:
                    await self._sleep(interval)
                except asyncio.CancelledError:
                    return

    # ---------- 采集（高清） ----------

    async def capture_now(
        self,
        capture_id: str,
        module: str,
        func: str,
        desc: str,
        ai_analyze: bool = False,
    ) -> dict:
        """暂停推流、截一张高清、抓层级、（可选）AI 描述、落盘。

        不调 recorder.record_once，因为 record_once 自己 print 日志，不适合 WS 场景。
        同一 controller 实例内多次采集共享同一 batch_id（在 _ensure_batch_id 中缓存）。

        ai_analyze=True 时：截图后调 AI 模块生成三段描述（interface_desc /
        layout_desc / elements_desc）。AI 配置从运行目录 .env 读；缺配置或调用失败
        都会让三个字段存为 null，但截图与 UI 层级照常落盘。
        """
        self.state.pause_for_capture = True
        self.state.pause_for_capture = True
        try:
            # 给推流循环一个回合让它看到标志
            try:
                await self._sleep(0.05)
            except asyncio.CancelledError:
                pass

            try:
                png_bytes = await self._take_screenshot_fn(self.device_id)
                content = await self._dump_hierarchy_fn(self.device_id)
            except midscene.MidsceneError as exc:
                result = {
                    "capture_id": capture_id,
                    "seq": 0,
                    "img_path": "",
                    "json_path": "",
                    "ok": False,
                    "error": str(exc),
                }
                await self._send_message(protocol.CAPTURED, **result)
                return result

            batch_id = self._ensure_batch_id()
            batch_dir = paths.make_batch_dir(self._output_root, batch_id)
            target_dir = paths.build_target_dir(batch_dir, module or paths.DEFAULT_SEGMENT,
                                                 func or paths.DEFAULT_SEGMENT)
            img_dir = target_dir / paths.IMG_SUBDIR
            json_dir = target_dir / paths.JSON_SUBDIR
            img_dir.mkdir(parents=True, exist_ok=True)
            json_dir.mkdir(parents=True, exist_ok=True)
            seq = paths.next_seq(target_dir)
            img_path = img_dir / paths.screenshot_filename(seq)
            json_path = json_dir / paths.json_filename(self._platform, seq)
            img_path.write_bytes(png_bytes)

            # 可选 AI 描述：缺配置 / 调用失败都不影响截图与 JSON 落盘
            ai_result: dict | None = None
            if ai_analyze:
                from shenle_device_record import ai as _ai
                config = _ai.load_config()
                if config is not None:
                    ai_result = await asyncio.to_thread(_ai.analyze_image, config, png_bytes)
                # 任何失败（无配置 / 调用错 / 返回 None）→ 三个字段写 null，
                # 让前端看到 AI 被启用但结果为空。
                if ai_result is None:
                    ai_result = {
                        "interface_desc": None,
                        "layout_desc": None,
                        "elements_desc": None,
                    }

            payload = paths.build_payload(
                content=content,
                img=paths.img_relpath(seq),
                module=module,
                func=func,
                desc=desc,
                ai=ai_result,
            )
            json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.state.last_capture_seq = max(self.state.last_capture_seq, seq)

            result = {
                "capture_id": capture_id,
                "seq": seq,
                "img_path": str(img_path),
                "json_path": str(json_path),
                "ok": True,
            }
            await self._send_message(protocol.CAPTURED, **result)
            return result
        finally:
            self.state.pause_for_capture = False

    # ---------- 模式 / 帧率 ----------

    async def set_mode(self, mode: StreamingMode) -> None:
        if mode == self.state.mode:
            return
        prev = self.state.mode
        self.state.mode = mode
        await self._send_mode_changed(prev, mode, reason="用户切换")

    def set_target_fps(self, fps: float) -> None:
        self.state.target_fps = max(MIN_FPS, min(MAX_FPS, fps))

    # ---------- 发消息的内部 helper ----------

    async def _send_message(self, type_: str, **fields) -> None:
        try:
            await self._send(protocol.encode(type_, **fields))
        except Exception as exc:  # WS 挂了不应当把推流拉崩
            LOG.warning("send %s 失败：%s", type_, exc)

    async def _send_frame(self, png_bytes: bytes, *, seq: int) -> None:
        encoded = base64.b64encode(png_bytes).decode("ascii")
        await self._send_message(
            protocol.FRAME,
            mime="image/png",
            data=encoded,
            seq=seq,
            ts=self._now(),
        )

    async def _send_mode_changed(self, prev: StreamingMode, new: StreamingMode, *, reason: str) -> None:
        await self._send_message(
            protocol.MODE_CHANGED,
            **{"from": prev.value, "to": new.value, "reason": reason},
        )