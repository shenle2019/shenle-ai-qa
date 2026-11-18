r"""第 16 章：浏览器自动化基础与选择器。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch16-web-basics -q
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

BROWSERS = ROOT / ".pw-browsers"
if BROWSERS.is_dir():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BROWSERS))

from labs._shared.mini_site import serve  # noqa: E402

playwright_api = pytest.importorskip("playwright.sync_api", reason="没装 playwright 就跳过本章")
sync_playwright = playwright_api.sync_playwright
expect = playwright_api.expect
TimeoutError = playwright_api.TimeoutError


@pytest.fixture(scope="module")
def site():
    with serve() as base:
        yield base


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as pw:
        try:
            instance = pw.chromium.launch()
        except Exception as exc:  # noqa: BLE001 - 没浏览器时跳过而不是报错
            pytest.skip(f"本机没有可用的 Chromium：{exc}")
        yield instance
        instance.close()


@pytest.fixture()
def page(browser, site):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.goto(f"{site}/login")
    yield page
    context.close()


@pytest.fixture()
def logged(page, site):
    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("secret")
    page.get_by_role("button", name="登录").click()
    page.wait_for_url("**/todos")
    return page


def test_login_page_title(page):
    expect(page).to_have_title("登录 · 任务清单")
    expect(page.get_by_role("heading", level=1)).to_have_text("任务清单")


def test_locator_by_role(page):
    button = page.get_by_role("button", name="登录")
    expect(button).to_be_visible()
    assert button.inner_text() == "登录"


def test_locator_by_label(page):
    assert page.get_by_label("用户名").get_attribute("data-testid") == "username"
    assert page.get_by_label("密码").get_attribute("type") == "password"


def test_locator_by_test_id(page):
    expect(page.get_by_test_id("login-submit")).to_have_text("登录")


def test_locator_by_text(page):
    expect(page.get_by_text("任务清单", exact=False).first).to_be_visible()


def test_wrong_password_shows_error(page):
    page.get_by_label("用户名").fill("alice")
    page.get_by_label("密码").fill("wrong")
    page.get_by_role("button", name="登录").click()
    expect(page.get_by_test_id("error")).to_have_text("用户名或密码错误")
    assert page.url.endswith("/login")


def test_guard_redirects_to_login(browser, site):
    context = browser.new_context()
    fresh = context.new_page()
    fresh.goto(f"{site}/todos")
    fresh.wait_for_url("**/login")
    assert fresh.url.endswith("/login")
    context.close()


def test_login_reaches_todos(logged):
    expect(logged.get_by_test_id("current-user")).to_have_text("alice")
    expect(logged).to_have_title("待办 · 任务清单")


def test_auto_wait_for_async_node(logged):
    expect(logged.get_by_test_id("done")).to_have_count(0)
    logged.get_by_test_id("start").click()
    # 没有 sleep：expect 自己轮询，默认 5s 超时
    expect(logged.get_by_test_id("done")).to_have_text("异步结果已返回", timeout=3000)


def test_timeout_when_element_never_appears(page):
    with pytest.raises(TimeoutError):
        page.get_by_test_id("never-exists").wait_for(timeout=300)


def test_add_todo_increases_count(logged):
    before = logged.get_by_test_id("todo-item").count()
    logged.get_by_label("新任务").fill("第 16 章验证项")
    logged.get_by_test_id("add-submit").click()
    logged.wait_for_load_state("load")
    expect(logged.get_by_test_id("todo-item")).to_have_count(before + 1)
    expect(logged.get_by_test_id("todo-list")).to_contain_text("第 16 章验证项")


def test_screenshot_written(logged, tmp_path):
    target = tmp_path / "todos.png"
    logged.screenshot(path=str(target), full_page=True)
    assert target.exists() and target.stat().st_size > 1000
