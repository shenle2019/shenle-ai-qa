"""第 25 章测试：离调用样例 dump 覆盖策略，真机跑一遍真实界面。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labs._shared.app import App, AppError  # noqa: E402
from labs._shared.ui_tree import Node, parse_dump  # noqa: E402

from locate import by_desc, by_id, by_text, by_type, describe, first_tappable  # noqa: E402

FIXTURES = ROOT / "labs" / "_shared" / "fixtures"


class FakeDevice:
    """把 App 需要的最小接口假装出来：给一帧固定的 dump。"""

    def __init__(self, xml: str):
        self.xml = xml
        self.taps: list[tuple[int, int]] = []

    def dump_ui(self) -> str:
        return self.xml

    def tap(self, x: int, y: int) -> None:
        self.taps.append((x, y))

    def size(self):
        return (1080, 1920)


def make_app(name: str) -> tuple[App, FakeDevice]:
    xml = (FIXTURES / name).read_text(encoding="utf-8")
    device = FakeDevice(xml)
    return App(device, poll=0.01), device


def test_by_id_on_sample() -> None:
    app, _ = make_app("sample_login.xml")
    node = by_id(app, "username")
    assert node.class_name.endswith("EditText")
    assert "username" in describe(node)


def test_by_text_exact_and_contains() -> None:
    app, _ = make_app("sample_login.xml")
    assert by_text(app, "登录").id_short == "login"
    assert by_text(app, "遇到问题", exact=False).text == "遇到问题？"


def test_by_desc_prefers_icon_buttons() -> None:
    app, _ = make_app("sample_login.xml")
    node = by_desc(app, "立即登录")
    assert node.id_short == "login"


def test_by_type_uses_index() -> None:
    app, _ = make_app("sample_list.xml")
    assert by_type(app, "android.widget.CheckBox", index=1).checked is True
    with pytest.raises(AppError):
        by_type(app, "android.widget.CheckBox", index=9)


def test_first_tappable_skips_text_nodes() -> None:
    app, _ = make_app("sample_login.xml")
    node = first_tappable(app)
    assert node.clickable is True
    assert node.id_short in {"username", "password", "login"}


def test_tap_uses_center_coordinates() -> None:
    app, device = make_app("sample_login.xml")
    node = app.tap(text="登录")
    assert device.taps[-1] == node.center


def test_missing_node_message_has_current_screen() -> None:
    app, _ = make_app("sample_login.xml")
    with pytest.raises(AppError) as exc:
        app.tap(text="不存在的按钮", timeout=0.2)
    assert "当前界面" in str(exc.value)


@pytest.mark.device
def test_real_app_locators(login_app: App) -> None:
    """真机：三种定位都能落到同一个登录页上。"""
    tree = login_app.tree()
    assert tree.find(text="登录联调 Demo") is not None
    assert login_app.find(text="登录（正确密码）").clickable is True
    assert login_app.find(text="登录（错误密码）").clickable is True
    assert isinstance(by_type(login_app, "android.widget.Button", index=0), Node)
