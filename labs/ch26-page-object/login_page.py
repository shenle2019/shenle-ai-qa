"""把登录联调 App 的界面收进一个页面类。

用例里不再出现坐标和文字，只写「点正确密码登录」「读结果」。
"""

from __future__ import annotations

from labs._shared.app import App, AppError

PACKAGE = "com.shenjiahang.logindemo"
ACTIVITY = f"{PACKAGE}.LoginActivity"
TITLE = "登录联调 Demo"
USERNAME_ID = "et_username"
PASSWORD_ID = "et_password"


class LoginDemoPage:
    def __init__(self, app: App):
        self.app = app

    # ---------- 页面动作 ----------

    def open(self, *, timeout: float = 15) -> "LoginDemoPage":
        self.app.device.force_stop(PACKAGE)
        self.app.device.start(PACKAGE, ACTIVITY)
        self.app.wait_text(TITLE, timeout=timeout)
        return self

    def tap_correct(self) -> "LoginDemoPage":
        self.app.tap_text("登录（正确密码）")
        return self

    def tap_wrong(self) -> "LoginDemoPage":
        self.app.tap_text("登录（错误密码）")
        return self

    def tap_photo(self) -> "LoginDemoPage":
        self.app.tap(text_contains="加载网络图片")
        return self

    def set_credentials(self, username: str, password: str) -> "LoginDemoPage":
        self.app.input_into(username, id_short=USERNAME_ID)
        self.app.input_into(password, id_short=PASSWORD_ID)
        return self

    def update_result(self) -> "LoginDemoPage":
        self.app.tap_text("登录（正确密码）")
        return self

    # ---------- 页面状态 ----------

    @property
    def title(self) -> str:
        return self.app.find(text=TITLE).text

    def result_text(self, *, timeout: float = 15) -> str:
        """结果区：没点之前显示目标地址，点完显示 `HTTP xxx（xx ms）` + 响应 JSON。"""
        node = self.app.wait_for(
            lambda n: bool(n.text) and ("HTTP" in n.text or "目标地址" in n.text or '"code"' in n.text),
            timeout=timeout,
        )
        return node.text

    def wait_result(self, keyword: str, *, timeout: float = 20) -> str:
        node = self.app.wait_for(
            lambda n: keyword in (n.text or ""),
            timeout=timeout,
        )
        return node.text

    def is_loaded(self) -> bool:
        try:
            self.app.find(text=TITLE)
            return True
        except LookupError:
            return False

    def current_activity(self) -> str:
        return self.app.current_activity()


def open_login_demo(app: App) -> LoginDemoPage:
    return LoginDemoPage(app).open()


__all__ = ["LoginDemoPage", "open_login_demo", "PACKAGE", "ACTIVITY", "TITLE", "AppError"]
