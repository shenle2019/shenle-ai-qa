"""页面对象 + 定位注册表：类里只出现 key，不出现选择器。"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from registry import Registry


class BasePage:
    path = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.at = Registry(page).at

    def open(self):
        self.page.goto(f"{self.base_url}{self.path}")
        return self


class LoginPage(BasePage):
    path = "/login"

    def login(self, username: str, password: str):
        self.at("login.username").fill(username)
        self.at("login.password").fill(password)
        self.at("login.submit").click()
        return TodoPage(self.page, self.base_url)

    def error_text(self) -> str:
        expect(self.at("login.error")).to_be_visible()
        return self.at("login.error").inner_text()


class TodoPage(BasePage):
    path = "/todos"

    def add(self, title: str):
        self.at("todos.new_title").fill(title)
        self.at("todos.add_button").click()
        self.page.wait_for_load_state("load")
        return self

    def titles(self) -> list[str]:
        return [item.inner_text() for item in self.at("todos.item").all()]

    def start_async(self) -> str:
        self.at("todos.start").click()
        expect(self.at("todos.done")).to_be_visible(timeout=3000)
        return self.at("todos.done").inner_text()


class TablePage(BasePage):
    path = "/table"

    def row_count(self) -> int:
        return self.at("table.rows").count()

    def titles(self) -> list[str]:
        return [cell.inner_text() for cell in self.at("table.cell_title").all()]

    def pick(self, index: int) -> None:
        self.at("table.pick").nth(index).check()
