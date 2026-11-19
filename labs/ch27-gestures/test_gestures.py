"""第 27 章测试：输入、按键、滑动都在真机上跑。

没有设备时整组跳过；离调用例验证参数拼装，不碰硬件。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labs._shared.app import App  # noqa: E402

from gestures import (  # noqa: E402
    clear_and_type,
    foreground_package,
    hide_keyboard,
    press_back,
    press_home,
    swipe_up,
)

PACKAGE = "com.shenjiahang.logindemo"


class StubDevice:
    def __init__(self):
        self.calls: list[tuple] = []

    def keyevent(self, key: str) -> None:
        self.calls.append(("key", key))

    def input_text(self, text: str) -> None:
        self.calls.append(("text", text))

    def shell(self, *args) -> str:
        self.calls.append(("shell", args))
        return ""

    def tap(self, x, y):
        self.calls.append(("tap", x, y))

    def long_press(self, x, y, duration):
        self.calls.append(("long", x, y, duration))

    def size(self):
        return (1080, 1920)


class StubApp:
    def __init__(self):
        self.device = StubDevice()

    def tap(self, **criteria):
        self.device.calls.append(("tap_node", criteria))
        return None

    def find(self, **criteria):
        return type("N", (), {"center": (540, 840), "text": criteria.get("text", "")})()

    def wait_for(self, predicate, timeout=8):
        return type("N", (), {"text": "ok"})()

    def swipe_up(self, steps=1):
        self.device.calls.append(("swipe_up", steps))

    def current_activity(self):
        return f"{PACKAGE}/.LoginActivity"


def test_clear_and_type_sequence() -> None:
    app = StubApp()
    clear_and_type(app, "qa_user", id_short="et_username")
    kinds = [c[0] for c in app.device.calls]
    assert kinds[0] == "tap_node"
    assert kinds.count("key") >= 2
    assert ("text", "qa_user") in app.device.calls


def test_hide_keyboard_uses_back_key() -> None:
    app = StubApp()
    hide_keyboard(app)
    assert ("shell", ("input", "keyevent", "KEYCODE_BACK")) in app.device.calls


def test_swipe_and_back_are_recorded() -> None:
    app = StubApp()
    swipe_up(app, steps=2)
    press_back(app)
    press_home(app)
    assert ("swipe_up", 2) in app.device.calls
    assert ("key", "KEYCODE_BACK") in app.device.calls
    assert ("key", "KEYCODE_HOME") in app.device.calls


def test_foreground_package() -> None:
    assert foreground_package(StubApp()) == PACKAGE


@pytest.mark.device
def test_type_into_username_replaces_content(login_app: App) -> None:
    """用户名框会被输入法接管，所以只断言「内容变了」，不比对字符。"""
    before = login_app.find(id_short="et_username").text
    clear_and_type(login_app, "qa", id_short="et_username")
    after = login_app.find(id_short="et_username").text
    assert after != before
    assert after


@pytest.mark.device
def test_type_into_password_is_literal(login_app: App) -> None:
    """密码框不参与联想，输入多少位就会显示多少个掩码点。"""
    typed = clear_and_type(login_app, "abc123", id_short="et_password")
    assert len(typed) == len("abc123")


@pytest.mark.device
def test_hide_keyboard_keeps_page(login_app: App) -> None:
    clear_and_type(login_app, "123", id_short="et_password")
    hide_keyboard(login_app)
    assert login_app.find(text="登录联调 Demo") is not None


@pytest.mark.device
def test_back_leaves_the_app(login_app: App) -> None:
    press_back(login_app)
    login_app.wait_for(lambda n: True, timeout=1)
    assert foreground_package(login_app) != PACKAGE


@pytest.mark.device
def test_swipe_keeps_title_visible(login_app: App) -> None:
    swipe_up(login_app)
    swipe_up(login_app)
    assert login_app.find(text="登录联调 Demo") is not None
