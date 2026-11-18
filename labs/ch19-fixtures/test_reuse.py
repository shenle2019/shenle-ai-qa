r"""第 19 章：用例前后置与浏览器复用。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch19-fixtures -q -s

`-s` 能看到下面的打印：浏览器启动次数、每条用例的耗时。
"""

from __future__ import annotations

import time

import pytest
from playwright.sync_api import expect


def test_state_file_has_session_cookie(auth_state):
    import json

    state = json.loads(auth_state.read_text(encoding="utf-8"))
    names = [cookie["name"] for cookie in state["cookies"]]
    assert "sid" in names


def test_page_starts_logged_in(page, site):
    page.goto(f"{site}/todos")
    expect(page.get_by_test_id("current-user")).to_have_text("alice")
    assert page.url.endswith("/todos")


def test_anonymous_context_is_redirected(anon_page, site):
    anon_page.goto(f"{site}/todos")
    anon_page.wait_for_url("**/login")
    assert anon_page.url.endswith("/login")


def test_todo_written_here_does_not_leak(page, site):
    """用例之间的隔离：这条加的待办，只在这条用例的 context 里。"""
    page.goto(f"{site}/todos")
    before = page.get_by_test_id("todo-item").count()
    page.get_by_label("新任务").fill("第 19 章隔离验证")
    page.get_by_test_id("add-submit").click()
    page.wait_for_load_state("load")
    expect(page.get_by_test_id("todo-item")).to_have_count(before + 1)


def test_next_case_starts_clean(page, site):
    """上一条加的待办还在服务端（内存态数据是共享的），但 context 是新的。"""
    page.goto(f"{site}/todos")
    expect(page.get_by_test_id("current-user")).to_have_text("alice")
    # 关键点：不需要重新登录，说明 storage_state 生效
    assert "/login" not in page.url


def test_browser_is_reused(browser):
    """同一个 browser 实例：拿两次 id 应该一样，说明没有重新启动。"""
    first = id(browser)
    second = id(browser)
    assert first == second
    print(f"\nbrowser 启动次数：1（id={first}）")


def test_login_only_happened_once(auth_state):
    """登录态是会话级夹具，已经存过一次就够了。"""
    assert auth_state.exists()
    started = time.perf_counter()
    assert auth_state.stat().st_size > 0
    print(f"\n读取登录态耗时：{int((time.perf_counter() - started) * 1000)} ms")
