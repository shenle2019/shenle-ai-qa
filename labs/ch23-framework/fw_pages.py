"""第 23 章的页面对象：只暴露业务动作，不暴露选择器。"""

from __future__ import annotations

from playwright.sync_api import Page, expect


class LoginPage:
    path = "/login"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self) -> "LoginPage":
        self.page.goto(self.base_url + self.path)
        return self

    @property
    def error(self):
        return self.page.get_by_test_id("error")

    def submit(self, username: str, password: str):
        self.page.get_by_test_id("username").fill(username)
        self.page.get_by_test_id("password").fill(password)
        self.page.get_by_test_id("login-submit").click()
        return self


class TodoPage:
    path = "/todos"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self) -> "TodoPage":
        self.page.goto(self.base_url + self.path)
        return self

    @property
    def current_user(self):
        return self.page.get_by_test_id("current-user")

    @property
    def items(self):
        return self.page.get_by_test_id("todo-item")

    def add(self, title: str) -> "TodoPage":
        self.page.get_by_test_id("new-title").fill(title)
        self.page.get_by_test_id("add-submit").click()
        return self

    def titles(self) -> list[str]:
        return [item.inner_text().strip() for item in self.items.all()]

    def expect_user(self, name: str):
        expect(self.current_user).to_contain_text(name)


class SearchPage:
    path = "/search"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def search(self, keyword: str) -> "SearchPage":
        self.page.goto(f"{self.base_url}{self.path}?q={keyword}")
        return self

    @property
    def results(self):
        return self.page.get_by_test_id("result-item")

    def count(self) -> int:
        return self.results.count()
