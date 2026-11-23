"""adb 设备发现：解析 + 选取。

`parse_adb_devices` 是纯函数，方便单测；`list_devices` 跑 `adb devices -l`；
`pick_device` 按规则选定目标（用户指定 / 第一台可用）。
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from .adb import ADB_TIMEOUT
from .errors import (
    AdbNotFound,
    DeviceNotFound,
    DeviceNotReady,
    NoDevice,
)


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
    """跑 `adb devices -l` 并解析。adb 缺失或执行失败时抛对应 CliError。

    注意：本函数不抛 NoDevice——返回空列表即可，由调用方决定如何呈现。
    NoDevice 的提示放在 `pick_device` 里，配合具体操作一并抛出更合适。
    """
    adb = shutil.which("adb")
    if adb is None:
        raise AdbNotFound()
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
        # 这里直接 raise AdbNotFound 不合适；用 RuntimeError 让上层知道是 adb 卡了。
        # 实际场景很少出现，宁可让上层看到原始异常也不误导用户。
        raise RuntimeError(f"adb devices 执行超时（{timeout}s）。") from exc
    if proc.returncode != 0:
        stderr_text = (proc.stderr or "").strip()
        tail = stderr_text or "（adb 未给出具体错误信息，请检查驱动 / USB 连接）"
        raise RuntimeError(f"adb devices 执行失败（退出码 {proc.returncode}）：{tail}")
    return parse_adb_devices(proc.stdout)


def pick_device(devices: list[Device], device_id: str | None = None) -> Device:
    """按规则选定目标设备。

    - device_id 给定：精确匹配 serial；状态非 device 时抛 DeviceNotReady
    - device_id 未给：从 state == "device" 的设备里取第一台；都没有时抛 NoDevice
    """
    if not devices:
        raise NoDevice()

    if device_id:
        for dev in devices:
            if dev.serial == device_id:
                if dev.state != "device":
                    raise DeviceNotReady(dev.serial, dev.state)
                return dev
        available = ", ".join(d.describe() for d in devices) or "（空）"
        raise DeviceNotFound(device_id, available)

    ready = [d for d in devices if d.state == "device"]
    if not ready:
        # 列出全部设备 + 状态，方便用户诊断（unauthorized/offline/...）
        detail = ", ".join(d.describe() for d in devices)
        # NoDevice 的文案是面向"完全没插线"场景的；这里覆盖一下，保留设备列表
        raise NoDevice(
            f"未检测到任何可用设备（adb 看到了 {len(devices)} 台但都不是 device 状态）："
            f"{detail}"
        )
    return ready[0]
