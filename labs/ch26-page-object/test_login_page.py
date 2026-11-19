"""第 26 章测试：页面对象把「怎么点」藏起来，用例只写业务。

真机部分要求后端已 adb reverse 到 8080，`backend` 夹具会处理。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labs._shared.app import App  # noqa: E402

from login_page import ACTIVITY, LoginDemoPage  # noqa: E402


class RecordingApp:
    """只记录动作的假 App：用来证明页面类点的是对的控件。"""

    def __init__(self):
        self.actions: list[tuple] = []

    def tap_text(self, text: str, timeout: float = 10):
        self.actions.append(("tap", text))
        return None

    def tap(self, timeout: float = 10, **criteria):
        self.actions.append(("tap_criteria", criteria))
        return None

    def input_into(self, text: str, id_short: str | None = None, timeout: float = 10):
        self.actions.append(("input", id_short, text))
        return None

    def wait_text(self, text: str, timeout: float = 10):
        self.actions.append(("wait", text))
        return None

    def find(self, **criteria):
        self.actions.append(("find", criteria))
        return type("N", (), {"text": "登录联调 Demo"})()

    def wait_for(self, predicate, timeout: float = 10):
        self.actions.append(("wait_for",))
        return type("N", (), {"text": "HTTP 200（18ms）\n{\"code\": 100}"})()

    def wait_gone(self, text: str, timeout: float = 10):
        self.actions.append(("wait_gone", text))

    def screenshot(self, path):
        self.actions.append(("shot", str(path)))
        return str(path)

    def current_activity(self):
        return ACTIVITY


def test_actions_are_expressed_as_business_steps() -> None:
    app = RecordingApp()
    page = LoginDemoPage(app)
    page.tap_correct().tap_wrong().tap_photo()
    assert app.actions == [
        ("tap", "登录（正确密码）"),
        ("tap", "登录（错误密码）"),
        ("tap_criteria", {"text_contains": "加载网络图片"}),
    ]


def test_set_credentials_targets_fields_by_id() -> None:
    app = RecordingApp()
    LoginDemoPage(app).set_credentials("justin", "123")
    assert ("input", "et_username", "justin") in app.actions
    assert ("input", "et_password", "123") in app.actions


def test_result_text_reads_response_block() -> None:
    page = LoginDemoPage(RecordingApp())
    assert page.result_text().startswith("HTTP 200")


def test_title_property(monkeypatch) -> None:
    page = LoginDemoPage(RecordingApp())
    assert page.title == "登录联调 Demo"


@pytest.mark.device
def test_correct_login_reaches_backend(login_app: App) -> None:
    page = LoginDemoPage(login_app)
    page.tap_correct()
    text = page.wait_result("登录成功", timeout=25)
    assert '"code": 100' in text


@pytest.mark.device
def test_wrong_login_reports_failure(login_app: App) -> None:
    page = LoginDemoPage(login_app)
    page.tap_wrong()
    text = page.wait_result("用户名或密码错误", timeout=25)
    assert '"code": 101' in text


@pytest.mark.device
def test_photo_endpoint_renders_image(login_app: App) -> None:
    page = LoginDemoPage(login_app)
    page.tap_photo()
    node = login_app.wait_for(
        lambda n: n.class_name.endswith("ImageView") and "网络图片" in (n.content_desc or ""),
        timeout=25,
    )
    assert node.bounds.width > 100
    assert node.bounds.height > 100
