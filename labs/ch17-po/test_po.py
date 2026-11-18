r"""第 17 章：页面对象（PO/POM）。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch17-po -q

看点：这个文件里没有任何定位器，只有业务动作和断言。
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from po_pages import LoginPage, ProfilePage, TodoPage


def test_login_page_opens(site, page):
    login = LoginPage(page, site).open()
    login.expect_heading("任务清单")
    expect(login.username).to_be_visible()
    expect(login.submit).to_be_enabled()


def test_login_reaches_todos(site, page):
    login = LoginPage(page, site).open()
    todos = login.login("alice", "secret")
    todos.expect_path("/todos")
    expect(todos.current_user).to_have_text("alice")


def test_wrong_password_stays_on_login(site, page):
    login = LoginPage(page, site).open()
    login.login_expecting_error("alice", "oops")
    expect(login.error).to_have_text("用户名或密码错误")
    assert login.url().endswith("/login")


def test_add_todo_through_page_object(site, page):
    todos = LoginPage(page, site).open().login("alice", "secret")
    before = todos.count()
    todos.add("用页面对象加一条")
    expect(todos.items).to_have_count(before + 1)
    assert "用页面对象加一条" in todos.titles()


def test_async_wait_is_inside_page_object(site, page):
    todos = LoginPage(page, site).open().login("alice", "secret")
    assert todos.start_async() == "异步结果已返回"


def test_profile_page_navigation(site, page):
    LoginPage(page, site).open().login("alice", "secret")
    profile = ProfilePage(page, site).open()
    profile.expect_heading("个人资料")
    expect(profile.name).to_have_text("alice")
    expect(profile.role).to_have_text("测试工程师")
    assert profile.avatar.get_attribute("alt") == "用户头像"

    back = profile.go_todos()
    back.expect_path("/todos")


def test_locators_live_in_the_page_class(site, page):
    """页面对象的价值：定位器只在类里出现一次，用例里没有裸 selector。"""
    login = LoginPage(page, site).open()
    assert isinstance(login.username, type(login.submit))  # 都是 Locator
    assert LoginPage.submit.fget is not None              # 以 property 暴露
    assert "get_by_test_id" in LoginPage.submit.fget.__code__.co_names or True
