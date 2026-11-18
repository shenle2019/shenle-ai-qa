"""前后置与浏览器复用：浏览器只起一次，登录态只做一次。

`browser` / `site` 由 `labs/conftest.py` 统一提供（整个 labs 共用一个进程，
每章各自开一遍 Playwright 会撞「Sync API inside asyncio loop」）。这里只加两件事：

1. `auth_state` 会话级——只登录一次，把 cookie 存成 JSON，排错时能直接打开看；
2. `page` 函数级——每条用例一个新 context，用 storage_state 恢复登录态，用例之间互不污染。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


@pytest.fixture(scope="session")
def auth_state(browser, site, tmp_path_factory):
    """登录一次，把登录态存盘。"""
    path = tmp_path_factory.mktemp("auth") / "state.json"
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{site}/login")
    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("secret")
    page.get_by_role("button", name="登录").click()
    page.wait_for_url("**/todos")
    context.storage_state(path=str(path))
    context.close()
    assert json.loads(path.read_text(encoding="utf-8"))["cookies"], "登录态里应该有 cookie"
    return path


@pytest.fixture()
def page(browser, auth_state):
    context = browser.new_context(storage_state=str(auth_state))
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def anon_page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
