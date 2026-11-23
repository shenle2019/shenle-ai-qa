"""和后台 daemon 拉起的浏览器建立临时 CDP 连接。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import Page, async_playwright

from . import state
from .errors import BrowserNotRunning, CliError


class ConnectFailed(CliError):
    """CDP 端口没监听或浏览器内部状态不对。"""


@asynccontextmanager
async def connect_page(port: int | None = None) -> AsyncIterator[Page]:
    """attach 到指定端口的后台浏览器，yield 默认 Page。

    port=None 时：自动选唯一的运行中端口；多个并发时抛错让调用方用 --port 明确。

    退出 with 块时只关 CDP 客户端连接；daemon 拉起的 Chromium
    进程不受影响。
    """
    if port is None:
        running = state.list_running_ports()
        if not running:
            raise BrowserNotRunning()
        if len(running) > 1:
            raise ConnectFailed(
                f"检测到 {len(running)} 个后台浏览器（端口：{running}）；"
                "请用 --port 明确指定要连接哪一个。"
            )
        port = running[0]

    if not state.is_running(port):
        raise BrowserNotRunning()

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}"
            )
        except Exception as e:
            raise ConnectFailed(
                f"无法连接 CDP 端口 {port}：{e}"
            ) from e

        if not browser.contexts:
            raise ConnectFailed(f"浏览器里没有任何 context（端口 {port}）")
        ctx = browser.contexts[0]
        if ctx.pages:
            page = ctx.pages[0]
        else:
            page = await ctx.new_page()

        try:
            yield page
        finally:
            pass
