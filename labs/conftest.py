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


@pytest.fixture()
def logged(page, site):
    page.goto(f"{site}/login")
    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("secret")
    page.get_by_role("button", name="登录").click()
    page.wait_for_url("**/todos")
    return page
