r"""第 18 章：元素定位集中管理。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch18-locators -q
"""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import expect

from locator_pages import LoginPage, TablePage, TodoPage
from registry import LocatorError, Registry, load

YAML = Path(__file__).resolve().parent / "locators.yaml"


def test_yaml_has_three_pages():
    data = load(YAML)
    assert set(data) == {"login", "todos", "profile", "table"}
    assert data["login"]["submit"]["by"] == "role"


def test_registry_resolves_each_kind(site, page):
    page.goto(f"{site}/login")
    reg = Registry(page, YAML)
    for key, spec in (("login.username", "label"), ("login.password", "label"),
                      ("login.submit", "role"), ("login.error", "testid")):
        locator = reg.at(key)
        assert locator.count() == 1, f"{key} 应该只命中一个元素"
        assert reg.spec(key)["by"] == spec


def test_unknown_key_raises(site, page):
    page.goto(f"{site}/login")
    reg = Registry(page, YAML)
    with pytest.raises(LocatorError):
        reg.at("login.nope")
    with pytest.raises(LocatorError):
        reg.at("loginnope")


def test_bad_by_raises(site, page):
    page.goto(f"{site}/login")
    reg = Registry(page, YAML)
    with pytest.raises(ValueError):
        reg.resolve({"by": "xpath-like-magic", "value": "//div"})


def test_login_flow_uses_only_keys(site, page):
    login = LoginPage(page, site).open()
    todos = login.login("alice", "secret")
    expect(todos.at("todos.current_user")).to_have_text("alice")


def test_table_page_from_registry(site, page):
    LoginPage(page, site).open().login("alice", "secret")
    table = TablePage(page, site).open()
    assert table.row_count() >= 2
    table.pick(0)
    assert table.at("table.pick").nth(0).is_checked()
    assert "写测试" in table.titles()


def test_swapping_yaml_swaps_behaviour(site, page, tmp_path):
    """同一份页面代码，换一份 yaml 就能指向另一套定位。"""
    custom = tmp_path / "custom.yaml"
    custom.write_text(
        "login:\n"
        "  username: { by: css, value: '#username' }\n"
        "  password: { by: css, value: '#password' }\n"
        "  submit: { by: text, value: 登录 }\n"
        "  error: { by: css, value: '[data-testid=error]' }\n",
        encoding="utf-8",
    )
    page.goto(f"{site}/login")
    reg = Registry(page, custom)
    assert reg.at("login.username").get_attribute("id") == "username"
