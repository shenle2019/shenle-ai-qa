"""生命周期管理：起服务 → 起 Playwright → 等浏览器关 → 干净退出。

依赖注入进程枚举器与 WS handler 工厂，单测可同步验证退出逻辑。
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Awaitable, Callable

import psutil

from shenle_device_record import LOG_PREFIX
from shenle_device_record.server.http_server import (
    StaticHandler,
    http_process_request,
)

# Windows 下默认 ProactorEventLoop 在子线程里与主线程的 socket 探测
# 一起跑时会触发"Future attached to a different loop" / proactor 内部
# 异常崩溃。强制使用 SelectorEventLoop（websockets 16.x 完全兼容）。
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:  # 极老 Python 3.11 之前的兼容性兜底
        pass

LOG = logging.getLogger("shenle_device_record.server.lifecycle")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
BROWSER_POLL_INTERVAL = 2.0
# Playwright 启动到 chromium 子进程真正被 psutil 看见有 ~1-2 秒延迟。
# 在此期间枚举子进程是空的，降级看 WS 信号又会因 _last_client_activity=0.0
# 立即退出。给一个启动宽限期，期间不判"playwright 已死"。
BROWSER_STARTUP_GRACE = 5.0
WS_CLIENT_IDLE_TIMEOUT = 10.0
PROCESS_ENUM_TIMEOUT = 1.5


ProcessEnumerator = Callable[[int], list[str]]


def _default_process_enumerator(pid: int) -> list[str]:
    """用 psutil 枚举某个 pid 的子进程名。出错返回空列表。"""
    try:
        parent = psutil.Process(pid)
        names = []
        for child in parent.children(recursive=True):
            try:
                names.append(child.name())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return names
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []


class LifecycleManager:
    def __init__(
        self,
        host: str,
        port: int,
        device_id: str,
        output_root: str,
        platform: str,
        no_browser: bool,
        ws_handler_factory,
        static_root: str,
        process_enumerator: ProcessEnumerator | None = None,
        browser_name_hint: str = "chrom",
    ) -> None:
        self.host = host
        self.port = port
        self.device_id = device_id
        self.output_root = output_root
        self.platform = platform
        self.no_browser = no_browser
        self._ws_handler_factory = ws_handler_factory
        self._static_handler = StaticHandler(static_root)
        self._enumerate = process_enumerator or _default_process_enumerator
        self._browser_name_hint = browser_name_hint.lower()

        self._stop_event = threading.Event()
        self._ws_server = None
        self._ws_thread: threading.Thread | None = None
        self._browser_proc: subprocess.Popen | None = None
        self._browser_proc_pid: int | None = None
        # 记录 Playwright 启动时刻，用于 _browser_alive 的启动宽限
        self._browser_started_at: float | None = None
        # 初始为 0（epoch），表示"尚无 WS 客户端活动"。
        # 这样 no_browser 模式下刚启动但还没客户端连进来时，
        # _browser_alive() 直接返回 False、不会等满 WS_CLIENT_IDLE_TIMEOUT。
        self._last_client_activity = 0.0
        self._loop: asyncio.AbstractEventLoop | None = None

    # ---------- 启动序列 ----------

    def start_and_wait(self) -> int:
        self._start_ws_in_thread()
        # 等 WS 起来
        if not self._wait_for_port(timeout=5.0):
            print(f"{LOG_PREFIX} 错误：服务起不来（端口 {self.port} 无响应）", flush=True)
            self._stop_event.set()
            return 1

        print(f"{LOG_PREFIX} 服务已就绪：http://{self.host}:{self.port}/", flush=True)

        if not self.no_browser:
            self._start_browser()

        try:
            self.wait_for_browser_exit()
        except KeyboardInterrupt:
            self._stop_event.set()

        self.shutdown()
        return 0

    def _start_ws_in_thread(self) -> None:
        import websockets

        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._run_ws_server())
            finally:
                self._loop.close()

        self._ws_thread = threading.Thread(target=run_loop, daemon=True, name="ws-loop")
        self._ws_thread.start()

    async def _run_ws_server(self) -> None:
        import websockets

        async def handler(websocket):
            self._last_client_activity = time.monotonic()
            try:
                await self._ws_handler_factory(websocket)
            finally:
                # WS 关闭作为加速退出信号
                self._last_client_activity = time.monotonic() - WS_CLIENT_IDLE_TIMEOUT
                self._stop_event.set()

        # process_request 在收到 HTTP 请求时同步调用
        async def proc_req(connection, request):
            return await http_process_request(connection, request, self._static_handler)

        async with websockets.serve(handler, self.host, self.port,
                                     process_request=proc_req,
                                     max_size=10 * 1024 * 1024):  # 10MB 上限
            self._ws_server = asyncio.current_task()
            print(f"{LOG_PREFIX} WebSocket 监听 ws://{self.host}:{self.port}/ws", flush=True)
            # 用 run_in_executor 把同步 Event.wait() 放线程池里执行，
            # 不阻塞事件循环；事件触发后立刻 resume。
            # shutdown 时外部 cancel 会让 CancelledError 传到 await 链上，
            # 捕获让它干净退出而不是把栈喷到 stderr。
            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, self._stop_event.wait)
            except asyncio.CancelledError:
                pass

    def _wait_for_port(self, timeout: float) -> bool:
        import socket
        # 给子线程里的事件循环一个稳定窗口：
        # 避免主线程立刻开始 connect 时，子线程里 websockets.serve 还没把
        # socket bind/listen 起来被立刻 reject（Windows 上尤其明显）。
        time.sleep(0.2)
        # 发一个最小但合法的 HTTP/1.1 请求，让 websockets 走 process_request
        # 路径返 404（合法响应，不会触发 InvalidMessage）。空 TCP 连接探测
        # 会被 websockets 当作 HTTP 请求读到 0 字节抛 EOFError，刷一屏误报。
        # 注：websockets 16.x 强制 HTTP/1.1，1.0 会被当作"unsupported protocol"拒绝。
        probe_request = (
            b"GET /__wait_for_port__ HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with socket.create_connection((self.host, self.port), timeout=0.2) as s:
                    s.sendall(probe_request)
                    try:
                        s.recv(1)  # 任意 1 字节表示服务存活
                    except OSError:
                        pass
                return True
            except OSError:
                time.sleep(0.1)
        return False

    def _start_browser(self) -> None:
        npx = shutil.which("npx")
        if npx is None:
            print(f"{LOG_PREFIX} 警告：找不到 npx，跳过自动开浏览器（用 --no-browser 或手动访问 http://{self.host}:{self.port}/）", flush=True)
            return
        url = f"http://{self.host}:{self.port}/"
        # 把 Playwright 的输出写到临时文件——DEVNULL 吞了的话用户没法排查
        # "为什么浏览器没起来"。路径在启动日志里打出来。
        import tempfile
        log_path = os.path.join(
            tempfile.gettempdir(),
            f"shenle-playwright-{os.getpid()}.log",
        )
        try:
            log_file = open(log_path, "w", encoding="utf-8")
        except OSError as exc:
            print(f"{LOG_PREFIX} 警告：无法创建 Playwright 日志文件：{exc}", flush=True)
            log_file = subprocess.DEVNULL
        try:
            self._browser_proc = subprocess.Popen(
                [npx, "--yes", "playwright", "open", url],
                stdout=log_file,
                stderr=subprocess.STDOUT,  # 合并到同一文件
            )
            self._browser_proc_pid = self._browser_proc.pid
            self._browser_started_at = time.monotonic()
            print(f"{LOG_PREFIX} 已启动 Playwright 浏览器（pid {self._browser_proc_pid}）", flush=True)
            print(f"{LOG_PREFIX} Playwright 输出写到：{log_path}", flush=True)
        except OSError as exc:
            print(f"{LOG_PREFIX} 警告：启动 Playwright 失败：{exc}", flush=True)

    # ---------- 退出判定 ----------

    def _browser_alive(self) -> bool:
        # 双信号：浏览器进程还在 OR WS 客户端最近活跃。
        # 1) pid 已设：枚举 Playwright 子进程；若枚举为空（进程消失），
        #    降级看 WS 客户端活跃度 —— spec "双信号任一触发即退"。
        if self._browser_proc_pid is not None:
            names = self._enumerate(self._browser_proc_pid)
            if any(self._browser_name_hint in n.lower() for n in names):
                return True
            # 进程枚举空：刚启 Playwright 不久（< BROWSER_STARTUP_GRACE）→ 给
            # 启动宽限不判死；超过宽限才降级 WS 信号。
            if self._browser_started_at is not None and \
                    (time.monotonic() - self._browser_started_at) < BROWSER_STARTUP_GRACE:
                return True
            # 真正超时 → 降级 WS 信号
            return (time.monotonic() - self._last_client_activity) < WS_CLIENT_IDLE_TIMEOUT
        # 2) pid 未设（--no-browser 或启动失败）：只看 WS 信号
        return (time.monotonic() - self._last_client_activity) < WS_CLIENT_IDLE_TIMEOUT

    def wait_for_browser_exit(self, timeout: float | None = None) -> bool:
        deadline = time.monotonic() + timeout if timeout else None
        while not self._stop_event.is_set():
            if not self._browser_alive():
                self._stop_event.set()
                return True
            if deadline is not None and time.monotonic() >= deadline:
                return False
            self._stop_event.wait(timeout=BROWSER_POLL_INTERVAL)
        return True

    def shutdown(self) -> None:
        # 1. 让 WS loop 退出
        self._stop_event.set()
        if self._ws_server is not None and self._loop is not None:
            self._loop.call_soon_threadsafe(self._ws_server.cancel)
        if self._ws_thread is not None:
            self._ws_thread.join(timeout=3.0)
        # 2. 关浏览器
        if self._browser_proc is not None and self._browser_proc.poll() is None:
            try:
                self._browser_proc.terminate()
            except OSError:
                pass
        # 3. 清理 midscene 临时文件
        self._cleanup_temp_screenshots()

    def _cleanup_temp_screenshots(self) -> None:
        import glob
        import tempfile

        # 只清理本工具自己写的前缀 (shenle_shot_*.png) —— midscene 在 base64 兜底
        # 分支会用这个前缀；tmp*.png 太宽，会误删用户/其他工具的临时文件，故移除。
        pattern = os.path.join(tempfile.gettempdir(), "shenle_shot_*.png")
        removed = 0
        for path in glob.glob(pattern):
            try:
                os.unlink(path)
                removed += 1
            except OSError:
                pass
        if removed:
            print(f"{LOG_PREFIX} 清理临时截图 {removed} 个", flush=True)