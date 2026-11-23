"""统一错误类型 + 面向用户的中文友好提示。

所有 CLI 子命令应当只抛出下面这些异常（或 `KeyboardInterrupt`），
由 `cli.main` 统一捕获并打印为一行可读消息，避免给用户呈现 Python
堆栈。Phase 1 只用到其中一小部分，其余给后续阶段预留。
"""

from __future__ import annotations


class CliError(Exception):
    """所有 CLI 可见错误的基类。`main` 会把它打印成一行人类可读消息。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class AdbNotFound(CliError):
    """系统 PATH 里找不到 adb 可执行文件。"""

    def __init__(self) -> None:
        super().__init__(
            "找不到 adb。请安装 Android SDK platform-tools，"
            "并把它所在目录加入 PATH 后重试。"
        )


class AdbCommandFailed(CliError):
    """adb 命令执行了但返回非零退出码，或抛了 TimeoutExpired。"""

    def __init__(self, cmd: str, detail: str) -> None:
        super().__init__(f"adb {cmd} 执行失败：{detail}")


class NoDevice(CliError):
    """adb 存在，但没有任何设备在线。"""

    def __init__(self) -> None:
        super().__init__(
            "未检测到任何安卓设备。请按以下顺序排查：\n"
            "  1. 用 USB 线连上手机，确认屏幕上弹出「是否允许 USB 调试」并点「允许」。\n"
            "  2. 在手机的「设置 → 关于本机」里连点「版本号」7 次打开「开发者选项」，"
            "在「开发者选项」里开启「USB 调试」。\n"
            "  3. 如仍无设备，执行 adb kill-server && adb start-server 后重新插拔 USB 线。"
        )


class DeviceNotReady(CliError):
    """找到指定序列号的设备，但状态不是 device（unauthorized / offline / ...）。"""

    _STATE_HINTS = {
        "unauthorized": "请在手机屏幕上点「允许 USB 调试」。"
        "如反复弹窗，可执行 adb kill-server 后重新插线重连。",
        "offline": "请重新插拔 USB 线，或执行 adb kill-server 后重试。",
    }

    def __init__(self, serial: str, state: str) -> None:
        hint = self._STATE_HINTS.get(state, "")
        msg = f"设备 {serial} 当前状态为 {state}，不可用。"
        if hint:
            msg += hint
        super().__init__(msg)


class DeviceNotFound(CliError):
    """用户指定的 -s/--serial 在当前设备列表里找不到。"""

    def __init__(self, serial: str, available: str) -> None:
        super().__init__(
            f"找不到设备 {serial}。当前设备列表：{available}"
        )


class PackageNotFound(CliError):
    """launch 时 monkey 没找到任何 launcher activity。"""

    def __init__(self, pkg: str) -> None:
        super().__init__(
            f"设备上找不到包名 {pkg} 的启动 Activity。"
            "可能包未安装，或它没有 android.intent.category.LAUNCHER。"
        )


class ClipboardNotAvailable(CliError):
    """cmd clipboard 不可用——vivo/ColorOS/HyperOS 等定制 ROM 常见。"""

    def __init__(self, op: str, detail: str) -> None:
        super().__init__(
            f"剪贴板方案不可用（{op} 失败：{detail}）。"
            "常见于 vivo/ColorOS/HyperOS 等定制 ROM。"
            "请改用 ADBKeyboard：装好 APK → 切到 ADBKeyboard 输入法 → "
            "用 `adb shell am broadcast -a ADB_INPUT_TEXT --es msg '...'` 输入。"
        )


class ScreenSizeFailed(CliError):
    """adb shell wm size 拿不到 / 解析不了。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"获取屏幕尺寸失败：{detail}")


class ElementNotFound(CliError):
    """AI 视觉识别后回复 found=false：屏幕上找不到目标元素。"""

    def __init__(self, description: str) -> None:
        super().__init__(
            f"屏幕上找不到「{description}」。"
            "可能元素还没出现、已被遮挡、或描述不够准确。"
        )


class KeycodeAliasNotFound(CliError):
    """keycode 别名或数字键码解析失败。"""

    def __init__(self, token: str) -> None:
        super().__init__(
            f"未知的按键别名或键码：{token!r}。常见别名：back, home, recents, "
            f"menu, enter, delete, escape, volume_up/down, power, "
            f"up/down/left/right, dpad_* 等；也支持直接传数字键码（如 4 = back）。"
            f"完整别名清单见 src/shenle_android_cli/keyevent.py 的 KEYCODE_ALIASES。"
        )


class AppStateFailed(CliError):
    """dumpsys 解析当前前台 App 失败。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"获取当前前台应用失败：{detail}")


class BatchOpParseError(CliError):
    """batch 参数解析失败。"""

    def __init__(self, detail: str) -> None:
        super().__init__(
            f"batch 参数解析失败：{detail}"
        )


class DumpUiFailed(CliError):
    """uiautomator dump / pull 失败。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"dump-ui 失败：{detail}")


class AdbKeyboardUnavailable(CliError):
    """ADBKeyboard IME 不可用（没装 / 没启用 / 没切换）。"""

    def __init__(self) -> None:
        super().__init__(
            "ADBKeyboard 不可用。需要：\n"
            "  1. 装 APK：https://github.com/senzhk/ADBKeyBoard/releases\n"
            "     adb install ADBKeyboard.apk\n"
            "  2. 启用 IME：adb shell ime enable com.android.adbkeyboard/.AdbIME\n"
            "  3. 切到 ADBKeyboard：adb shell ime set com.android.adbkeyboard/.AdbIME\n"
            "  4. 重跑：shenle-android-cli input --input-method adbkeyboard ..."
        )
