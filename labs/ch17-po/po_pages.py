"""页面对象：把「页面长什么样」和「业务要做什么」分开。

三个类，对应三个页面：登录、待办、个人资料。定位器全部收在类里，
用例只调方法名——以后前端改了一个 id，只改这里一处。
"""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect


class BasePage:
    """所有页面共用的东西：地址拼接、跳转、等页面就绪。"""

    path = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- 基础设施 ---
    def open(self) -> "BasePage":
        self.page.goto(f"{self.base_url}{self.path}")
        return self

    def url(self) -> str:
        return self.page.url

    def title(self) -> str:
        return self.page.title()

    def expect_path(self, suffix: str) -> None:
        expect(self.page).to_have_url(re.compile(re.escape(suffix) + r"$"))

    def expect_heading(self, text: str) -> None:
        expect(self.page.get_by_role("heading", level=1)).to_have_text(text)


class LoginPage(BasePage):
    path = "/login"

    # 定位器集中在这里，用方法而不是属性，避免用例直接摸到 locator
    @property
    def username(self):
        return self.page.get_by_label("用户名")

    @property
    def password(self):
        return self.page.get_by_label("密码")

    @property
    def submit(self):
        return self.page.get_by_role("button", name="登录")

    @property
    def error(self):
        return self.page.get_by_test_id("error")

    def login(self, username: str, password: str) -> "TodoPage":
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
        return TodoPage(self.page, self.base_url)

    def login_expecting_error(self, username: str, password: str) -> "LoginPage":
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
        return self


class TodoPage(BasePage):
    path = "/todos"

    @property
    def current_user(self):
        return self.page.get_by_test_id("current-user")

    @property
    def new_title(self):
        return self.page.get_by_label("新任务")

    @property
    def add_button(self):
        return self.page.get_by_test_id("add-submit")

    @property
    def items(self):
        return self.page.get_by_test_id("todo-item")

    def add(self, title: str) -> "TodoPage":
        self.new_title.fill(title)
        self.add_button.click()
        self.page.wait_for_load_state("load")
        return self

    def titles(self) -> list[str]:
        return [item.inner_text() for item in self.items.all()]

    def count(self) -> int:
        return self.items.count()

    def start_async(self) -> str:
        self.page.get_by_test_id("start").click()
        done = self.page.get_by_test_id("done")
        expect(done).to_be_visible(timeout=3000)
        return done.inner_text()


class ProfilePage(BasePage):
    path = "/profile"

    @property
    def name(self):
        return self.page.get_by_test_id("profile-name")

    @property
    def role(self):
        return self.page.get_by_test_id("profile-role")

    @property
    def avatar(self):
        return self.page.get_by_test_id("avatar")

    def go_todos(self) -> TodoPage:
        self.page.get_by_test_id("nav-todos").click()
        self.page.wait_for_load_state("load")
        return TodoPage(self.page, self.base_url)
