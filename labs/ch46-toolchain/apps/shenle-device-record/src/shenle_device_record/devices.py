"""adb 设备发现。解析与选取是纯函数，只有 list_devices 会起子进程。"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

ADB_TIMEOUT = 15.0


class AdbError(RuntimeError):
    """adb 本身不可用或执行失败。"""


class DeviceSelectionError(RuntimeError):
    """设备列表里选不出可用设备。"""


@dataclass(frozen=True)
class Device:
    serial: str
    state: str
    model: str = ""

    def describe(self) -> str:
        extra = f", {self.model}" if self.model else ""
        return f"{self.serial} ({self.state}{extra})"


def parse_adb_devices(stdout: str) -> list[Device]:
    """解析 `adb devices -l` 的 stdout。忽略表头、空行和 daemon 提示行。"""
    result: list[Device] = []
    for raw_line in (stdout or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("*") or line.startswith("List of devices"):
            continue
        fields = line.split()
        if len(fields) < 2:
            continue
        model = ""
        for prop in fields[2:]:
            if prop.startswith("model:"):
                model = prop[len("model:"):]
        result.append(Device(serial=fields[0], state=fields[1], model=model))
    return result


def list_devices(timeout: float = ADB_TIMEOUT) -> list[Device]:
    """跑 `adb devices -l` 并解析。adb 缺失或执行失败时抛 AdbError。"""
    adb = shutil.which("adb")
    if adb is None:
        raise AdbError(
            "找不到 adb。请安装 Android SDK platform-tools，并把它所在目录加入 PATH。"
        )
    try:
        proc = subprocess.run(
            [adb, "devices", "-l"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdbError(f"adb devices 执行超时（{timeout}s）。") from exc
    if proc.returncode != 0:
        # adb 退出非零但 stderr 为空时给个兜底文案，避免尾巴只剩冒号。
        stderr_text = (proc.stderr or "").strip()
        tail = stderr_text or "（adb 未给出具体错误信息，请检查驱动 / USB 连接）"
        raise AdbError(f"adb devices 执行失败（退出码 {proc.returncode}）：{tail}")
    return parse_adb_devices(proc.stdout)


_STATE_HINTS = {
    "unauthorized": "请在手机屏幕上点「允许 USB 调试」。如反复弹窗，可执行 adb kill-server 后重新插线重连。",
    "offline": "请重新插拔 USB 线，或执行 adb kill-server 后重试。",
}


def pick_device(devices: list[Device], device_id: str | None = None) -> Device:
    """选定目标设备。不传 device_id 时取第一台 state 为 device 的设备。"""
    if not devices:
        raise DeviceSelectionError(
            "没有检测到任何安卓设备。请按以下顺序排查：\n"
            "  1. 用 USB 线连上手机，确认手机上弹出「是否允许 USB 调试」并点「允许」。\n"
            "  2. 在手机的「设置 → 关于本机」里连点「版本号」7 次打开「开发者选项」，"
            "在「开发者选项」里开启「USB 调试」。\n"
            "  3. 如仍无设备，执行 adb kill-server && adb start-server 后重新插拔 USB 线。"
        )
    if device_id:
        for dev in devices:
            if dev.serial == device_id:
                if dev.state != "device":
                    hint = _STATE_HINTS.get(dev.state, "")
                    # 未识别状态（sideload / recovery 等）时没有提示，
                    # 不输出末尾那个孤立的句号 / 分隔符。
                    if hint:
                        raise DeviceSelectionError(
                            f"设备 {device_id} 当前状态为 {dev.state}，不可用。{hint}"
                        )
                    raise DeviceSelectionError(
                        f"设备 {device_id} 当前状态为 {dev.state}，不可用。"
                    )
                return dev
        available = ", ".join(d.describe() for d in devices)
        raise DeviceSelectionError(f"找不到设备 {device_id}。当前设备列表：{available}")

    ready = [d for d in devices if d.state == "device"]
    if not ready:
        detail = ", ".join(d.describe() for d in devices)
        hints = " ".join(
            dict.fromkeys(_STATE_HINTS.get(d.state, "") for d in devices)
        ).strip()
        # 未识别状态（sideload / recovery 等）时没有提示，不输出孤立的句号。
        if hints:
            raise DeviceSelectionError(f"检测到设备但均不可用：{detail}。{hints}")
        raise DeviceSelectionError(f"检测到设备但均不可用：{detail}")
    return ready[0]
