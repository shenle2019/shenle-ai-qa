"""第 24 章的测试：探测逻辑用假 adb 覆盖，真机只做一次冒烟。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labs._shared import adb as adb_module  # noqa: E402
from labs._shared.adb import AdbError, Device  # noqa: E402

from probe import collect, quick_check, report  # noqa: E402


class Result:
    def __init__(self, out: str, code: int = 0, err: str = ""):
        self.returncode = code
        self.stdout = out.encode("utf-8")
        self.stderr = err.encode("utf-8")


@pytest.fixture()
def fake_adb(monkeypatch):
    responses = {
        "shell getprop ro.product.model": "Pixel 5\n",
        "shell getprop ro.build.version.release": "13\n",
        "shell getprop ro.build.version.sdk": "33\n",
        "shell wm size": "Physical size: 1080x2340\n",
        "shell wm density": "Physical density: 440\n",
        "shell dumpsys window": "  mCurrentFocus=Window{1 u0 com.demo.app/com.demo.app.TodoList}\n",
        "exec-out screencap": b"\x89PNG\r\n\x1a\n0000",
    }

    def run(cmd, **kwargs):
        joined = " ".join(cmd[1:])
        for prefix, value in responses.items():
            if joined.startswith(prefix):
                return Result(value) if isinstance(value, str) else type(
                    "Bin", (), {"returncode": 0, "stdout": value, "stderr": b""}
                )()
        return Result("")

    monkeypatch.setattr(adb_module.subprocess, "run", run)
    return responses


def test_collect_collects_every_field(fake_adb, tmp_path) -> None:
    info = collect(Device(adb="adb"), screenshot_to=tmp_path / "s.png")
    assert info["model"] == "Pixel 5"
    assert info["android"] == "13"
    assert info["sdk"] == 33
    assert info["size"] == (1080, 2340)
    assert info["density"] == 440
    assert info["current_activity"] == "com.demo.app/com.demo.app.TodoList"
    assert info["errors"] == {}


def test_collect_records_errors_without_aborting(fake_adb, monkeypatch) -> None:
    def boom(cmd, **kwargs):
        if "getprop ro.product.model" in " ".join(cmd):
            return Result("", code=1, err="error: closed")
        return Result("")

    monkeypatch.setattr(adb_module.subprocess, "run", boom)
    info = collect(Device(adb="adb"))
    assert info["model"] is None
    assert "model" in info["errors"]
    assert "closed" in info["errors"]["model"]


def test_report_renders_readable_lines(fake_adb) -> None:
    info = collect(Device(adb="adb"))
    text = report(info)
    assert "设备序列号" in text
    assert "1080x2340" in text
    assert "Android 13（API 33）" in text
    assert "TodoList" in text


def test_report_marks_missing_fields() -> None:
    text = report({"serial": "x", "size": None, "errors": {"model": "boom"}})
    assert "分辨率：未知" in text
    assert "[失败] model：boom" in text


def test_quick_check_false_when_device_offline(monkeypatch) -> None:
    monkeypatch.setattr(adb_module.subprocess, "run", lambda *a, **k: Result("", code=1, err="device offline"))
    assert quick_check(Device(adb="adb")) is False


@pytest.mark.device
def test_real_device_is_reachable(device: Device) -> None:
    """真机冒烟：这一条只在真的有在线设备时跑。"""
    assert device.serial
    assert quick_check(device) is True
