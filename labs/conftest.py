"""整层共享的浏览器与站点夹具。

放这里的原因是：pytest 会把 `labs/` 下所有用例放进同一个进程跑。
每个章节目录各自 `sync_playwright()` 一次，第二个目录就会撞上「Sync API inside asyncio loop」。
统一在这里开一次，各章只声明自己需要的 page。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BROWSERS = ROOT / ".pw-browsers"
if BROWSERS.is_dir():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BROWSERS))

from labs._shared.mini_site import serve  # noqa: E402

playwright_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="session")
def site():
    with serve() as base:
        yield base


@pytest.fixture(scope="session")
def browser():
    with playwright_api.sync_playwright() as pw:
        try:
            instance = pw.chromium.launch()
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"本机没有可用的 Chromium：{exc}")
        yield instance
        instance.close()


@pytest.fixture()
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def device():
    """有真机就用真机，没有就跳过——APP 章节的用例都挂在这个夹具上。"""
    from labs._shared.adb import AdbError, Device

    try:
        instance = Device.first_online(timeout=8)
    except AdbError as exc:
        pytest.skip(f"没有可用的 Android 设备：{exc}")
    return instance


@pytest.fixture(scope="session")
def backend(device):
    """APP 章节用的联调后端：本机 8080 + adb reverse，手机访问 127.0.0.1:8080 即本机。"""
    from labs._shared.login_server import LoginServer

    with LoginServer(8080) as server:
        device.reverse(8080)
        yield server


APP_PACKAGE = "com.shenjiahang.logindemo"
APP_ACTIVITY = "com.shenjiahang.logindemo.LoginActivity"


@pytest.fixture()
def login_app(device, backend):
    """每条用例都从干净的首屏开始：杀进程 → 冷启动 → 等首屏出现。"""
    from labs._shared.app import App

    device.force_stop(APP_PACKAGE)
    device.start(APP_PACKAGE, APP_ACTIVITY)
    app = App(device)
    app.wait_text("登录联调 Demo", timeout=15)
    yield app
    device.force_stop(APP_PACKAGE)


@pytest.fixture()
def logged(page, site):
    page.goto(f"{site}/login")
    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("secret")
    page.get_by_role("button", name="登录").click()
    page.wait_for_url("**/todos")
    return page
