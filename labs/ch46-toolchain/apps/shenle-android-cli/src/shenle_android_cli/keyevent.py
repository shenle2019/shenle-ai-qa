"""Android keycode 别名表，给 `keyevent` 子命令用。

keyevent 接受两种输入：
- 数字键码（如 4 = back）
- 别名（"back" / "home" / "recents" / ...）

常见 Android keycode 见：
https://developer.android.com/reference/android/view/KeyEvent
"""

from __future__ import annotations

from .errors import KeycodeAliasNotFound


KEYCODE_ALIASES: dict[str, int] = {
    # ---- navigation ----
    "back": 4,
    "home": 3,
    "menu": 82,
    "recents": 187, "app_switch": 187, "recent_apps": 187,
    "search": 84,

    # ---- text editing ----
    "enter": 66, "return": 66, "newline": 66,
    "delete": 67, "del": 67, "backspace": 67,
    "forward_delete": 112,
    "escape": 111, "esc": 111,
    "tab": 61,
    "space": 62,
    "insert": 124,

    # ---- d-pad ----
    "up": 19, "dpad_up": 19,
    "down": 20, "dpad_down": 20,
    "left": 21, "dpad_left": 21,
    "right": 22, "dpad_right": 22,
    "dpad_center": 23, "dpad_middle": 23,

    # ---- volume / power / camera ----
    "volume_up": 24, "vol_up": 24,
    "volume_down": 25, "vol_down": 25,
    "volume_mute": 164, "mute": 164,
    "power": 26,
    "camera": 27,

    # ---- call ----
    "call": 5,
    "endcall": 6, "end_call": 6,

    # ---- keypad 0-9 + star + pound ----
    "keypad_0": 7, "numpad_0": 7,
    "keypad_1": 8, "numpad_1": 8,
    "keypad_2": 9, "numpad_2": 9,
    "keypad_3": 10, "numpad_3": 10,
    "keypad_4": 11, "numpad_4": 11,
    "keypad_5": 12, "numpad_5": 12,
    "keypad_6": 13, "numpad_6": 13,
    "keypad_7": 14, "numpad_7": 14,
    "keypad_8": 15, "numpad_8": 15,
    "keypad_9": 16, "numpad_9": 16,
    "star": 17, "keypad_star": 17,
    "pound": 18, "keypad_pound": 18,

    # ---- modifiers ----
    "ctrl_left": 113,
    "shift_left": 59,
    "alt_left": 57,
    "meta_left": 117,

    # ---- page nav ----
    "page_up": 92, "pageup": 92,
    "page_down": 93, "pagedown": 93,

    # ---- function keys F1~F12 ----
    "f1": 131, "f2": 132, "f3": 133, "f4": 134,
    "f5": 135, "f6": 136, "f7": 137, "f8": 138,
    "f9": 139, "f10": 140, "f11": 141, "f12": 142,

    # ---- zoom ----
    "zoom_in": 168,
    "zoom_out": 169,

    # ---- lock keys ----
    "caps_lock": 115, "capslock": 115,
    "num_lock": 143, "numlock": 143,
    "scroll_lock": 116, "scrolllock": 116,

    # ---- media ----
    "media_play_pause": 85,
    "media_stop": 86,
    "media_next": 87,
    "media_previous": 88,
    "media_rewind": 89,
    "media_fast_forward": 90,
}


def resolve_keycode(token: str) -> int:
    """把别名或数字键码解析成 int。找不到抛 KeycodeAliasNotFound。"""
    s = (token or "").strip().lower()
    if not s:
        raise KeycodeAliasNotFound(token)
    if s in KEYCODE_ALIASES:
        return KEYCODE_ALIASES[s]
    try:
        return int(s, 0)  # 支持 0x 前缀的十六进制
    except ValueError:
        raise KeycodeAliasNotFound(token) from None
