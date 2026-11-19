"""adb 封装的单元测试：把 subprocess.run 换成一个按参数返回预设输出的假实现。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

import pytest

from labs._shared import adb as adb_module
from labs._shared.adb import AdbError, Device


@dataclass
class FakeCompleted:
    returncode: int
    stdout: bytes
    stderr: bytes = b""


class FakeExecutor:
    """记录调用，并按「命令前缀」返回预设输出（str 或 bytes 都行）。"""

    def __init__(self, responses: dict[str, str | bytes], returncode: int = 0, stderr: str = ""):
        self.responses = responses
        self.returncode = returncode
        self.stderr = stderr
        self.calls: list[list[str]] = []

    def __call__(self, cmd, capture_output=True, timeout=None, check=False, **_):
        self.calls.append(list(cmd))
        args = " ".join(cmd[1:])
        for key, value in self.responses.items():
            if args.startswith(key):
                payload = value.encode("utf-8") if isinstance(value, str) else value
                return FakeCompleted(self.returncode, payload, self.stderr.encode("utf-8"))
        return FakeCompleted(self.returncode, b"", self.stderr.encode("utf-8"))


@pytest.fixture()
def fake(monkeypatch):
    def install(responses: dict[str, str | bytes], returncode: int = 0, stderr: str = "") -> FakeExecutor:
        executor = FakeExecutor(responses, returncode=returncode, stderr=stderr)
        monkeypatch.setattr(adb_module.subprocess, "run", executor)
        return executor

    return install


def test_devices_parses_online_and_offline(fake) -> None:
    fake(
        {
            "devices": (
                "List of devices attached\n"
                "emulator-5554\tdevice product:sdk model:Pixel_5 device:generic\n"
                "R58M12345\tunauthorized usb:1-1 model:SM_G9910\n"
                "\n"
            )
        }
    )
    devices = Device.devices("adb")
    assert [d.serial for d in devices] == ["emulator-5554", "R58M12345"]
    assert devices[0].model == "Pixel_5"
    assert devices[1].state == "unauthorized"
    assert [d.serial for d in Device.online_devices("adb")] == ["emulator-5554"]


def test_first_online_raises_when_empty(fake) -> None:
    fake({"devices": "List of devices attached\n\n"})
    with pytest.raises(AdbError):
        Device.first_online("adb", timeout=1.0)


def test_size_prefers_override(fake) -> None:
    fake({"shell wm size": "Physical size: 1080x2400\nOverride size: 720x1600\n"})
    assert Device(adb="adb").size() == (720, 1600)


def test_density_prefers_override(fake) -> None:
    fake({"shell wm density": "Physical density: 440\nOverride density: 320\n"})
    assert Device(adb="adb").density() == 320


def test_screenshot_writes_png(fake, tmp_path) -> None:
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    fake({"exec-out screencap": png})
    target = tmp_path / "shot.png"
    written = Device(adb="adb").screenshot(target)
    assert written == target
    assert target.read_bytes() == png


def test_screenshot_rejects_non_png(fake, tmp_path) -> None:
    fake({"exec-out screencap": "not a png"})
    with pytest.raises(AdbError):
        Device(adb="adb").screenshot(tmp_path / "x.png")


def test_input_text_escapes_spaces(fake) -> None:
    executor = fake({"shell input text": ""})
    Device(adb="adb").input_text("hello world")
    assert executor.calls[-1][-1] == "hello%sworld"


def test_tap_and_swipe_build_arguments(fake) -> None:
    executor = fake({"shell input": ""})
    device = Device(adb="adb")
    device.tap(540, 840)
    device.swipe(100, 1500, 100, 300, 250)
    device.long_press(50, 60, 700)
    assert executor.calls[0][-4:] == ["input", "tap", "540", "840"]
    assert executor.calls[1][-6:] == ["swipe", "100", "1500", "100", "300", "250"]
    assert executor.calls[2][-6:] == ["swipe", "50", "60", "50", "60", "700"]


def test_shell_failure_raises_with_stderr(fake) -> None:
    fake({"shell getprop": ""}, returncode=1, stderr="error: device offline")
    with pytest.raises(AdbError) as exc:
        Device(adb="adb").shell("getprop", "ro.product.model")
    assert "device offline" in str(exc.value)


def test_current_activity_regex(fake) -> None:
    fake(
        {
            "shell dumpsys window": (
                "  mCurrentFocus=Window{8f2a1 u0 com.demo.app/com.demo.app.LoginActivity}\n"
                "  mFocusedApp=ActivityRecord{1 u0 com.demo.app/.LoginActivity}\n"
            )
        }
    )
    assert Device(adb="adb").current_activity() == "com.demo.app/com.demo.app.LoginActivity"


def test_timeout_becomes_adb_error(monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="adb", timeout=1)

    monkeypatch.setattr(adb_module.subprocess, "run", boom)
    with pytest.raises(AdbError) as exc:
        Device(adb="adb", timeout=1).shell("getprop")
    assert "超时" in str(exc.value)
