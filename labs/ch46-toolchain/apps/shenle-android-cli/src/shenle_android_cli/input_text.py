"""adb shell input 的封装：支持剪贴板 / ADBKeyboard 两种 IME 输入方式。

用 --input-method 或 INPUT_METHOD 环境变量切换：

1. **clipboard**（默认）—— cmd clipboard set-primary-clip + keyevent 279 粘贴。
   Android 10+ 标准方案；部分模拟器镜像 + vivo/ColorOS/HyperOS 定制 ROM 不支持。

2. **adbkeyboard** —— 走 ADBKeyboard 这个第三方 IME 的
   `am broadcast -a ADB_INPUT_B64`（base64 编码文本避免特殊字符转义）。
   需要先装 APK + `ime enable` + `ime set`。
   优点：跨设备一致性更好，包括模拟器。

为什么不直接 input text 兜底：
- adb shell input text 遇到非 ASCII 会丢字符 / 乱码
- "看似成功但内容是乱码" 比 "明确失败" 更危险（用例静默通过）
- 所以两种方式都明确报错，由用户显式选择
"""

from __future__ import annotations

import base64
import re
import time

from .adb import run_adb
from .errors import AdbKeyboardUnavailable, ClipboardNotAvailable, CliError


_NON_ASCII = re.compile(r"[^\x00-\x7F]")
_ASCII_DELAY_AFTER_TAP = 0.2
_CLIPBOARD_PASTE_DELAY = 0.2
_ADBKEYBOARD_DELAY = 0.15

# 有效输入方式
VALID_METHODS = ("clipboard", "adbkeyboard")


def input_text_at(
    serial: str,
    x: int,
    y: int,
    text: str,
    *,
    clear: bool = True,
    method: str = "clipboard",
) -> None:
    """tap (x, y) 后输入 text。

    clear=True（默认）：先按 MOVE_END + 50 次 DEL 把输入框里现有内容清空。
    method：'clipboard' 或 'adbkeyboard'。
    """
    if method not in VALID_METHODS:
        raise CliError(
            f"未知 input-method：{method!r}（应为 {', '.join(VALID_METHODS)}）"
        )

    run_adb(
        ["shell", "input", "tap", str(int(x)), str(int(y))],
        serial=serial,
    )
    time.sleep(_ASCII_DELAY_AFTER_TAP)

    if not text:
        return

    if method == "adbkeyboard":
        # ADBKeyboard 不区分 ASCII / 非 ASCII，统一走广播
        _input_via_adbkeyboard(serial, text, clear=clear)
        return

    # method == "clipboard"（默认）
    if _NON_ASCII.search(text):
        _input_via_clipboard(serial, text, clear=clear)
    else:
        if clear:
            _clear_field(serial)
        # adb shell input text 不支持裸空格——转义成 %s
        escaped = text.replace(" ", "%s")
        run_adb(["shell", "input", "text", escaped], serial=serial)


# ---------------------------------------------------------------------------
# 内部


def _clear_field(serial: str) -> None:
    """把当前输入框里的内容清空：MOVE_END + 50 次 DEL。

    50 次对常见输入框足够；不够时仍可继续 input 文字，旧内容会被覆盖（取决于 IME）。
    """
    run_adb(["shell", "input", "keyevent", "123"], serial=serial)  # MOVE_END
    time.sleep(0.05)
    run_adb(
        ["shell", "input", "keyevent", *(["67"] * 50)],
        serial=serial,
    )
    time.sleep(0.1)


def _input_via_clipboard(serial: str, text: str, *, clear: bool) -> None:
    """Android 10+ 标准剪贴板方案。失败抛 ClipboardNotAvailable。

    步骤：清空 → set-primary-clip → 读回校验 → keyevent 279 粘贴
    """
    if clear:
        _clear_field(serial)

    # 1. 设置剪贴板
    proc = run_adb(
        ["shell", "cmd", "clipboard", "set-primary-clip", "--user", "0", text],
        serial=serial,
    )
    stderr_text = (proc.stderr or "").strip()
    # vivo/ColorOS/HyperOS 等定制 ROM 的 cmd clipboard 经常不可用
    if stderr_text and (
        "No shell command" in stderr_text or "Exception" in stderr_text
    ):
        raise ClipboardNotAvailable("set-primary-clip", stderr_text)

    # 2. 读回校验（防止 set 静默失败）
    proc2 = run_adb(
        ["shell", "cmd", "clipboard", "get-primary-clip", "--user", "0"],
        serial=serial,
    )
    actual = (proc2.stdout or "").strip()
    if actual != text:
        raise ClipboardNotAvailable(
            "get-primary-clip",
            f"读回校验失败（期望 {text!r}，实际 {actual!r}）",
        )

    # 3. 触发粘贴
    time.sleep(0.1)
    run_adb(
        ["shell", "input", "keyevent", "279"],
        serial=serial,
    )
    time.sleep(_CLIPBOARD_PASTE_DELAY)


def _input_via_adbkeyboard(serial: str, text: str, *, clear: bool) -> None:
    """通过 ADBKeyboard 这个第三方 IME 输入文本。

    要求：设备装了 ADBKeyboard APK，并且 `ime list -s` 能看到它。

    流程：
      1. 检查 IME 列表里有 adbkeyboard（否则抛 AdbKeyboardUnavailable）
      2. 用 base64 编码文本（避免特殊字符转义问题），发广播
      3. ADBKeyboard 解码后用 IME 输入

    比剪贴板方案慢（多了 IME 检查 ~50ms），但跨设备一致性更好。
    """
    if clear:
        _clear_field(serial)

    # 1. IME 检查
    proc = run_adb(["shell", "ime", "list", "-s"], serial=serial)
    enabled = (proc.stdout or "").lower()
    if "adbkeyboard" not in enabled:
        raise AdbKeyboardUnavailable()

    # 2. base64 编码 → 广播
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    run_adb(
        [
            "shell", "am", "broadcast",
            "-a", "ADB_INPUT_B64",
            "--es", "msg", encoded,
        ],
        serial=serial,
    )
    time.sleep(_ADBKEYBOARD_DELAY)
