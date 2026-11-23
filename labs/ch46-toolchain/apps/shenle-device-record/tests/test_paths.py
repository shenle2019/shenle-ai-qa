from datetime import datetime
from pathlib import Path

import pytest

from shenle_device_record import paths


def test_generate_batch_id_format():
    assert paths.generate_batch_id(datetime(2026, 8, 29, 17, 11, 49)) == "20260829-171149"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("个人中心", "个人中心"),
        ("  登录  ", "登录"),
        ("..", ""),
        (".", ""),
        ("", ""),
        ('a<b>c:d"e|f?g*h\\i/j', "abcdefghij"),
        ("trail...", "trail"),
        ("  ...  ", ""),
        ("a" * 150, "a" * 100),
    ],
)
def test_sanitize_segment(raw, expected):
    assert paths.sanitize_segment(raw) == expected


@pytest.mark.parametrize(
    "module, expected",
    [
        ("个人中心-登录", ["个人中心", "登录"]),
        ("电商/用户中心/收货地址", ["电商", "用户中心", "收货地址"]),
        ("A-B/C", ["A", "B", "C"]),
        ("单级", ["单级"]),
        ("", ["未分类"]),
        ("   ", ["未分类"]),
        ("../../etc", ["etc"]),
        ("..-..", ["未分类"]),
        ("C:/Windows/System32", ["C", "Windows", "System32"]),
        ("-a--b-", ["a", "b"]),
    ],
)
def test_split_module(module, expected):
    assert paths.split_module(module) == expected


def test_sanitize_func_falls_back():
    assert paths.sanitize_func("..") == "未分类"
    assert paths.sanitize_func("  登录功能 ") == "登录功能"


def test_build_target_dir_normal(tmp_path):
    batch = tmp_path / "20260829-171149"
    got = paths.build_target_dir(batch, "个人中心-登录", "登录功能")
    assert got == batch / "个人中心" / "登录" / "登录功能"


def test_build_target_dir_blocks_traversal(tmp_path):
    batch = tmp_path / "20260829-171149"
    got = paths.build_target_dir(batch, "../../etc-passwd", "..")
    assert got == batch / "etc" / "passwd" / "未分类"
    assert str(got.resolve()).startswith(str(batch.resolve()))


def test_make_batch_dir_creates(tmp_path):
    got = paths.make_batch_dir(tmp_path, "20260829-171149")
    assert got.is_dir()
    assert got.name == "20260829-171149"
    assert got.parent.name == "AI-信息采集"


def test_next_seq_starts_at_one(tmp_path):
    assert paths.next_seq(tmp_path) == 1


def test_next_seq_increments(tmp_path):
    img = tmp_path / "img"
    img.mkdir()
    (img / "screenshot_001.png").write_bytes(b"")
    (img / "screenshot_002.png").write_bytes(b"")
    assert paths.next_seq(tmp_path) == 3


def test_next_seq_ignores_non_matching(tmp_path):
    img = tmp_path / "img"
    img.mkdir()
    (img / "screenshot_005.png").write_bytes(b"")
    (img / "screenshot_abc.png").write_bytes(b"")
    (img / "other.png").write_bytes(b"")
    assert paths.next_seq(tmp_path) == 6


def test_filenames():
    assert paths.screenshot_filename(1) == "screenshot_001.png"
    assert paths.json_filename("android", 7) == "android_007.json"
    assert paths.json_filename("ios", 12) == "ios_012.json"
    assert paths.img_relpath(1) == "img/screenshot_001.png"


def test_build_payload_keys_and_order():
    payload = paths.build_payload(
        content="<hierarchy/>",
        img="img/screenshot_001.png",
        module="个人中心-登录",
        func="登录功能",
        desc="说明",
    )
    assert list(payload.keys()) == ["content", "img", "module", "func", "desc"]
    assert payload["module"] == "个人中心-登录"
    assert payload["content"] == "<hierarchy/>"


def test_build_payload_allows_empty_content():
    payload = paths.build_payload("", "img/screenshot_001.png", "未分类", "未分类", "")
    assert payload["content"] == ""
    assert payload["desc"] == ""
