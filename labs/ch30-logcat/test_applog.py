"""第 30 章测试：日志解析离线跑，真机只验证「跑一遍应用没有崩溃」。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from labs._shared.app import App  # noqa: E402

from applog import digest, errors_related_to, find_crashes, lines_of, of_level  # noqa: E402

CRASH_LOG = """
08-01 10:00:01.001  1234  1250 I ActivityManager: Start proc com.demo.app
08-01 10:00:02.100  1250  1250 E AndroidRuntime: FATAL EXCEPTION: main
08-01 10:00:02.101  1250  1250 E AndroidRuntime: Process: com.demo.app, PID: 1250
08-01 10:00:02.102  1250  1250 E AndroidRuntime: java.lang.NullPointerException: 用户名不能为空
08-01 10:00:02.103  1250  1250 E AndroidRuntime: \tat com.demo.app.Login.onClick(Login.java:42)
08-01 10:00:09.000   900   900 E ActivityManager: ANR in com.demo.app
08-01 10:00:10.000  1234  1250 W System: some warning
"""

OK_LOG = """
08-01 10:01:00.000  1250  1250 I LoginActivity: tap login
08-01 10:01:01.000  1250  1260 E Network: failed to connect to /127.0.0.1:8080
"""


def test_lines_of_drops_blank() -> None:
    assert len(lines_of("a\n\n b \n")) == 2


def test_of_level_filters_errors() -> None:
    errors = of_level(CRASH_LOG, "E")
    assert errors and all(" E " in line or "E/" in line for line in errors)


def test_find_crashes_extracts_process_and_type() -> None:
    crashes = find_crashes(CRASH_LOG)
    kinds = [c.kind for c in crashes]
    assert kinds == ["CRASH", "ANR"]
    assert crashes[0].process == "com.demo.app"
    assert "NullPointerException" in crashes[0].summary
    assert "用户名不能为空" in crashes[0].summary


def test_errors_related_to_package() -> None:
    related = errors_related_to(CRASH_LOG, "com.demo.app")
    assert related
    assert all("com.demo.app" in line for line in related)


def test_digest_prefers_crashes() -> None:
    text = digest(CRASH_LOG, "com.demo.app")
    assert "CRASH" in text
    assert "ANR" in text


def test_digest_falls_back_to_errors() -> None:
    text = digest(OK_LOG, "com.demo.app")
    assert "failed to connect" in text


def test_digest_without_errors() -> None:
    assert digest("08-01 10:00 I Foo: hello", "com.demo.app") == "日志里没有异常"


@pytest.mark.device
def test_real_app_has_no_crash(login_app: App) -> None:
    login_app.device.clear_logcat()
    login_app.tap(text_contains="登录（正确密码）")
    login_app.wait_for(lambda n: "HTTP" in (n.text or ""), timeout=25)
    text = login_app.device.logcat(lines=400)
    # 只看被测进程：整机日志里常混着输入法、桌面等其它进程的崩溃/ANR
    crashes = [c for c in find_crashes(text) if "logindemo" in (c.process or "")]
    assert not crashes, [c.as_line() for c in crashes]
