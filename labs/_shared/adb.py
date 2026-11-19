"""adb 封装：只包这一仓 APP 实操需要的那几个子命令。

设计原则：
1. 只依赖 platform-tools 的 adb.exe，不引入 Appium/uiautomator2 这类需要长期跑服务端组件的依赖；
2. 所有命令都走 subprocess，方便单测里用一个假的 adb 脚本替换掉；
3. 有设备就真连，没设备就抛 AdbError，由调用方决定跳过还是失败。
"""

from __future__ import annotations

import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT = 20.0
DEFAULT_ADB = "adb"


class AdbError(RuntimeError):
    """adb 执行失败，或者当前没有可用设备。"""


def resolve_adb(adb: str | None = None) -> str:
    """找到 adb 可执行文件：显式传入 > PATH > 常见安装目录。"""
    if adb:
        return adb
    found = shutil.which(DEFAULT_ADB)
    if found:
        return found
    for candidate in (
        r"D:\soft\platform-tools\adb.exe",
        r"C:\Android\platform-tools\adb.exe",
        r"E:\Android\platform-tools\adb.exe",
    ):
        if Path(candidate).exists():
            return candidate
    raise AdbError("找不到 adb，请把 platform-tools 加进 PATH 或显式传入路径")


@dataclass
class DeviceInfo:
    serial: str
    state: str
    model: str = ""

    @property
    def online(self) -> bool:
        return self.state == "device"


class Device:
    """一台设备（或唯一在线设备）的操作句柄。"""

    def __init__(self, serial: str | None = None, adb: str | None = None, timeout: float = DEFAULT_TIMEOUT):
        self.adb = resolve_adb(adb)
        self.serial = serial
        self.timeout = timeout

    # ---------- 基础执行 ----------

    def _base(self) -> list[str]:
        cmd = [self.adb]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def run(self, *args: str, timeout: float | None = None, binary: bool = False):
        cmd = self._base() + [str(a) for a in args]
        try:
            out = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout or self.timeout,
                check=False,
            )
        except FileNotFoundError as exc:  # adb 本身没找到
            raise AdbError(f"adb 不可执行：{self.adb}") from exc
        except subprocess.TimeoutExpired as exc:
            raise AdbError(f"adb 超时：{' '.join(cmd)}") from exc
        if out.returncode != 0:
            err = out.stderr.decode("utf-8", "replace").strip()
            raise AdbError(f"adb 失败({' '.join(args)})：{err or out.returncode}")
        return out.stdout if binary else out.stdout.decode("utf-8", "replace")

    def shell(self, *args: str, timeout: float | None = None) -> str:
        return self.run("shell", *args, timeout=timeout)

    # ---------- 设备列表 ----------

    @classmethod
    def devices(cls, adb: str | None = None) -> list[DeviceInfo]:
        out = subprocess.run(
            [resolve_adb(adb), "devices", "-l"], capture_output=True, timeout=DEFAULT_TIMEOUT, check=False
        ).stdout.decode("utf-8", "replace")
        result: list[DeviceInfo] = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            serial, state = parts[0], parts[1]
            model = ""
            for part in parts[2:]:
                if part.startswith("model:"):
                    model = part.split(":", 1)[1]
            result.append(DeviceInfo(serial=serial, state=state, model=model))
        return result

    @classmethod
    def online_devices(cls, adb: str | None = None) -> list[DeviceInfo]:
        return [d for d in cls.devices(adb) if d.online]

    @classmethod
    def first_online(cls, adb: str | None = None, timeout: float = DEFAULT_TIMEOUT) -> "Device":
        deadline = time.time() + timeout
        while time.time() < deadline:
            online = cls.online_devices(adb)
            if online:
                return cls(serial=online[0].serial, adb=adb)
            time.sleep(1.0)
        raise AdbError("没有在线设备：先确认 USB 调试已打开、手机上已点「允许」")

    def wait_ready(self, timeout: float = 30.0) -> "Device":
        self.run("wait-for-device", timeout=timeout)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.shell("getprop", "sys.boot_completed").strip() == "1":
                return self
            time.sleep(1.0)
        raise AdbError("设备已连接但系统还没启动完成")

    # ---------- 属性 ----------

    def model(self) -> str:
        return self.shell("getprop", "ro.product.model").strip()

    def android_version(self) -> str:
        return self.shell("getprop", "ro.build.version.release").strip()

    def sdk(self) -> int:
        raw = self.shell("getprop", "ro.build.version.sdk").strip()
        return int(raw) if raw.isdigit() else 0

    def size(self) -> tuple[int, int]:
        """返回 (宽, 高)，优先取 Override size。"""
        raw = self.shell("wm", "size")
        match = re.search(r"Override size:\s*(\d+)x(\d+)", raw) or re.search(r"Physical size:\s*(\d+)x(\d+)", raw)
        if not match:
            raise AdbError(f"读不到屏幕尺寸：{raw.strip()}")
        return int(match.group(1)), int(match.group(2))

    def density(self) -> int:
        raw = self.shell("wm", "density")
        match = re.search(r"Override density:\s*(\d+)", raw) or re.search(r"Physical density:\s*(\d+)", raw)
        if not match:
            raise AdbError(f"读不到屏幕密度：{raw.strip()}")
        return int(match.group(1))

    # ---------- 截图与窗口树 ----------

    def screenshot(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.run("exec-out", "screencap", "-p", binary=True)
        if not data.startswith(b"\x89PNG"):
            raise AdbError("截图不是 PNG，可能被设备截断")
        path.write_bytes(data)
        return path

    def dump_ui(self) -> str:
        """拿到当前窗口的 XML。优先 /dev/tty，失败再落盘 pull。"""
        self.shell("uiautomator", "dump", "/sdcard/window_dump.xml")
        return self.shell("cat", "/sdcard/window_dump.xml")

    # ---------- 输入 ----------

    def tap(self, x: int, y: int) -> None:
        self.shell("input", "tap", str(x), str(y))

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        self.shell("input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms))

    def long_press(self, x: int, y: int, duration_ms: int = 800) -> None:
        self.shell("input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms))

    def input_text(self, text: str) -> None:
        # adb input text 不认空格和中文，空格转 %s，中文交给输入法或 base64 方案
        escaped = text.replace(" ", "%s")
        self.shell("input", "text", escaped)

    def keyevent(self, code: str | int) -> None:
        self.shell("input", "keyevent", str(code))

    # ---------- 应用 ----------

    def start(self, package: str, activity: str | None = None) -> None:
        if activity:
            self.shell("am", "start", "-n", f"{package}/{activity}")
        else:
            self.shell("monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1")

    def force_stop(self, package: str) -> None:
        self.shell("am", "force-stop", package)

    def reverse(self, local_port: int, remote_port: int | None = None) -> None:
        """把设备的某个端口反代到本机，真机连本机服务就靠它。"""
        remote = remote_port or local_port
        self.run("reverse", f"tcp:{remote}", f"tcp:{local_port}")

    def reverse_list(self) -> str:
        return self.run("reverse", "--list")

    def clear_reverse(self) -> None:
        self.run("reverse", "--remove-all")

    def current_activity(self) -> str:
        """当前前台界面，返回 `包名/Activity`。

        优先 mCurrentFocus；通知栏、锁屏这类不是 Activity，会退化到 mFocusedApp。
        """
        raw = self.shell("dumpsys", "window")
        focus = re.search(r"mCurrentFocus=Window\{[^}]*?\s([\w.]+)/([\w.$]+)\}", raw)
        if focus:
            package, activity = focus.group(1), focus.group(2)
            if activity.startswith("."):
                activity = package + activity
            return f"{package}/{activity}"
        app = re.search(r"mFocusedApp=ActivityRecord\{[^}]*?\s([\w.]+)/([\w.$]+)", raw)
        if app:
            package, activity = app.group(1), app.group(2)
            if activity.startswith("."):
                activity = package + activity
            return f"{package}/{activity}"
        return ""

    def logcat(self, lines: int = 200, since: str | None = None) -> str:
        args = ["logcat", "-d", "-t", str(lines)]
        if since:
            args += ["-T", since]
        return self.run(*args)

    def clear_logcat(self) -> None:
        self.run("logcat", "-c")
