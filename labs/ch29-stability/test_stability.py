"""第 29 章测试：重试与留证的逻辑都可以离线验证，真机只验「失败时真的产出了文件」。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labs._shared.app import App  # noqa: E402

from stability import Attempt, capture_on_failure, retry, wait_until  # noqa: E402


class Flaky:
    def __init__(self, failures: int, value="ok"):
        self.failures = failures
        self.value = value
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError(f"第 {self.calls} 次失败")
        return self.value


def test_retry_succeeds_after_failures() -> None:
    flaky = Flaky(2)
    assert retry(flaky, attempts=3, delay=0) == "ok"
    assert flaky.calls == 3


def test_retry_raises_after_exhausting() -> None:
    flaky = Flaky(5)
    with pytest.raises(RuntimeError):
        retry(flaky, attempts=2, delay=0)
    assert flaky.calls == 2


def test_retry_records_attempts() -> None:
    seen: list[Attempt] = []
    retry(Flaky(1), attempts=2, delay=0, on_attempt=seen.append)
    assert [a.ok for a in seen] == [False, True]
    assert "第 1 次失败" in seen[0].error


def test_retry_rejects_bad_attempts() -> None:
    with pytest.raises(ValueError):
        retry(lambda: 1, attempts=0)


def test_wait_until_true_and_false() -> None:
    counter = {"n": 0}

    def predicate() -> bool:
        counter["n"] += 1
        return counter["n"] >= 3

    assert wait_until(predicate, timeout=2, interval=0.01) is True
    assert wait_until(lambda: False, timeout=0.2, interval=0.01) is False


class StubDevice:
    def __init__(self, log: str = "E/AndroidRuntime: FATAL EXCEPTION"):
        self.log = log
        self.shots: list[str] = []

    def logcat(self, lines: int = 200) -> str:
        return self.log

    def screenshot(self, path):
        self.shots.append(str(path))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"\x89PNG\r\n\x1a\n")
        return path


class StubApp:
    def __init__(self):
        self.device = StubDevice()

    def screenshot(self, path):
        return self.device.screenshot(path)


def test_capture_on_failure_writes_three_files(tmp_path) -> None:
    app = StubApp()

    def boom():
        raise AssertionError("界面没出现")

    with pytest.raises(AssertionError):
        capture_on_failure(app, tmp_path, "login", boom)

    files = sorted(p.suffix for p in tmp_path.iterdir())
    assert files == [".log", ".png", ".txt"]
    assert "FATAL EXCEPTION" in next(tmp_path.glob("*.log")).read_text(encoding="utf-8")
    assert "界面没出现" in next(tmp_path.glob("*.txt")).read_text(encoding="utf-8")


def test_capture_on_failure_passes_through_success(tmp_path) -> None:
    app = StubApp()
    assert capture_on_failure(app, tmp_path, "ok", lambda: 42) == 42
    assert list(tmp_path.iterdir()) == []


@pytest.mark.device
def test_capture_on_real_device(login_app: App, tmp_path) -> None:
    def boom():
        raise AssertionError("故意失败")

    with pytest.raises(AssertionError):
        capture_on_failure(login_app, tmp_path, "device", boom)
    shot = next(tmp_path.glob("*.png"))
    assert shot.stat().st_size > 1000
