"""窗口树解析的单元测试：不连设备，全部用离线 dump。"""

from __future__ import annotations

from pathlib import Path

import pytest

from labs._shared.ui_tree import Bounds, Node, parse_dump

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture()
def login_tree() -> Node:
    return parse_dump((FIXTURES / "sample_login.xml").read_text(encoding="utf-8"))


@pytest.fixture()
def list_tree() -> Node:
    return parse_dump((FIXTURES / "sample_list.xml").read_text(encoding="utf-8"))


def test_parse_returns_hierarchy_root(login_tree: Node) -> None:
    assert login_tree.class_name == "android.widget.FrameLayout"
    assert login_tree.package == "com.demo.app"
    assert len(login_tree.walk()) == 10


def test_id_short_strips_package(login_tree: Node) -> None:
    username = login_tree.find(id_short="username")
    assert username.class_name == "android.widget.EditText"
    assert username.text == "alice"
    assert username.resource_id == "com.demo.app:id/username"


def test_bounds_center_and_size(login_tree: Node) -> None:
    button = login_tree.find(id_short="login")
    assert button.bounds.width == 936
    assert button.bounds.height == 120
    assert button.center == (540, 840)
    assert button.bounds.contains(540, 840) is True
    assert button.bounds.contains(10, 10) is False


def test_label_prefers_text_then_desc_then_id(login_tree: Node) -> None:
    assert login_tree.find(id_short="login").label == "登录"
    assert login_tree.find(text="遇到问题？").label == "遇到问题？"
    # 密码框的 text 是掩码，正好验证「有 text 就用 text」
    assert login_tree.find(id_short="password").label == "••••••"


def test_find_all_by_clickable(login_tree: Node) -> None:
    clickable = login_tree.find_all(clickable=True)
    assert [n.id_short for n in clickable] == ["username", "password", "login"]


def test_text_contains_matches_substring(list_tree: Node) -> None:
    row = list_tree.find(text_contains="周报")
    assert row.class_name == "android.widget.TextView"
    assert row.center == (288, 302)


def test_ambiguous_match_lists_candidates(list_tree: Node) -> None:
    with pytest.raises(LookupError) as exc:
        list_tree.find(id_short="row")
    message = str(exc.value)
    assert "匹配到 3 个节点" in message
    assert "row" in message


def test_missing_node_raises(login_tree: Node) -> None:
    with pytest.raises(LookupError):
        login_tree.find(text="不存在的按钮")


def test_clickable_ancestor_from_text(list_tree: Node) -> None:
    row = list_tree.find(text="跑一次回归")
    assert row.clickable is False
    assert row.clickable_ancestor().id_short == "row"


def test_scrollable_flag(list_tree: Node) -> None:
    scrollable = [n for n in list_tree.walk() if n.scrollable]
    assert len(scrollable) == 1
    assert scrollable[0].class_name == "androidx.recyclerview.widget.RecyclerView"


def test_dumps_is_readable(list_tree: Node) -> None:
    text = list_tree.dumps()
    assert "<写周报>" in text
    assert text.splitlines()[0].startswith("-E- <")


def test_parse_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        parse_dump("<html></html>")
    with pytest.raises(ValueError):
        parse_dump("")


def test_bounds_parse_without_match_is_zero() -> None:
    assert Bounds.parse("") == Bounds(0, 0, 0, 0)
