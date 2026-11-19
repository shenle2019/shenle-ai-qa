"""设备能力探测：把 adb 的一堆零散命令收成一个字典。

这一层不关心「怎么点」，只回答「这台设备是什么、现在在哪一屏、能不能截图」。
"""

from __future__ import annotations

from typing import Any

from labs._shared.adb import AdbError, Device


def collect(device: Device, *, screenshot_to=None) -> dict[str, Any]:
    """采集设备画像。任何一项失败都记进 errors，不中断整体探测。"""
    info: dict[str, Any] = {"serial": device.serial}
    errors: dict[str, str] = {}

    def attempt(key: str, func) -> None:
        try:
            info[key] = func()
        except AdbError as exc:
            info[key] = None
            errors[key] = str(exc)

    attempt("model", device.model)
    attempt("android", device.android_version)
    attempt("sdk", device.sdk)
    attempt("size", device.size)
    attempt("density", device.density)
    attempt("current_activity", device.current_activity)
    if screenshot_to is not None:
        attempt("screenshot", lambda: str(device.screenshot(screenshot_to)))

    info["errors"] = errors
    return info


def report(info: dict[str, Any]) -> str:
    """把画像做成几行人能读的文字。"""
    size = info.get("size")
    size_text = f"{size[0]}x{size[1]}" if size else "未知"
    lines = [
        f"设备序列号：{info.get('serial')}",
        f"型号：{info.get('model') or '未知'}",
        f"系统：Android {info.get('android')}（API {info.get('sdk')}）",
        f"分辨率：{size_text} @ {info.get('density') or '?'}dpi",
        f"当前界面：{info.get('current_activity') or '未知'}",
    ]
    if info.get("screenshot"):
        lines.append(f"截图：{info['screenshot']}")
    for key, message in (info.get("errors") or {}).items():
        lines.append(f"[失败] {key}：{message.splitlines()[0]}")
    return "\n".join(lines)


def quick_check(device: Device) -> bool:
    """设备在线且能响应 shell，才算真的可用。"""
    try:
        device.wait_ready(timeout=5)
        return bool(device.model())
    except AdbError:
        return False
