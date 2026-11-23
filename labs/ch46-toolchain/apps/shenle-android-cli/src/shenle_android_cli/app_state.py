"""解析 dumpsys 输出拿到当前前台 App。

优先 mResumedActivity（前台活跃 Activity），回退 mCurrentFocus（最后焦点窗口）。
"""

from __future__ import annotations

import re

from .adb import run_adb
from .errors import AppStateFailed


# 匹配 "u0 com.example/.MainActivity" 或 "u0 com.example/com.example.MainActivity"
_APP_RE = re.compile(r"u0\s+([\w][\w.]*)/(\.?[\w$][\w.$]*)")


def get_current_app(serial: str) -> tuple[str, str]:
    """返回 (package, activity) 元组。无法解析抛 AppStateFailed。"""
    proc = run_adb(
        ["shell", "dumpsys", "activity", "activities"],
        serial=serial,
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "ResumedActivity" not in line:
            continue
        m = _APP_RE.search(line)
        if m:
            return m.group(1), m.group(2)

    # fallback：dumpsys window 的 mCurrentFocus / mFocusedApp
    proc2 = run_adb(["shell", "dumpsys", "window"], serial=serial)
    for line in proc2.stdout.splitlines():
        line = line.strip()
        if "mCurrentFocus" not in line and "mFocusedApp" not in line:
            continue
        m = _APP_RE.search(line)
        if m:
            return m.group(1), m.group(2)

    raise AppStateFailed(
        "dumpsys 输出里没找到 ResumedActivity / mCurrentFocus / mFocusedApp。"
        "可能 dumpsys 版本太老，或设备状态异常。"
    )
