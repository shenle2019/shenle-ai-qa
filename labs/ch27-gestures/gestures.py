"""第 27 章：输入、按键、滑动的常用组合。

这里有两条经验：能用 `input text` 就别用逐个按键；能按 keyevent 就别按坐标。
"""

from __future__ import annotations

from labs._shared.app import App


def clear_and_type(app: App, text: str, *, id_short: str) -> str:
    """点中输入框 → 移到末尾 → 连删 → 输入 → 读回。

    注意：读回的文字不一定等于输入的文字。用户名框会被输入法接管（拼音联想），
    密码框则统一显示掩码点，所以断言要按字段类型来写。
    """
    app.tap(id_short=id_short)
    device = app.device
    device.keyevent("KEYCODE_MOVE_END")
    for _ in range(20):
        device.keyevent("KEYCODE_DEL")
    device.input_text(text)
    return app.wait_for(lambda n: n.id_short == id_short, timeout=8).text or ""


def hide_keyboard(app: App) -> None:
    """输入完收起键盘，否则下面的按钮可能被键盘挡住点不到。"""
    app.device.shell("input", "keyevent", "KEYCODE_BACK")


def press_back(app: App) -> None:
    app.device.keyevent("KEYCODE_BACK")


def press_home(app: App) -> None:
    app.device.keyevent("KEYCODE_HOME")


def swipe_up(app: App, *, steps: int = 1) -> None:
    app.swipe_up(steps=steps)


def long_press_text(app: App, text: str, *, duration: int = 700) -> None:
    node = app.find(text=text)
    x, y = node.center
    app.device.long_press(x, y, duration)


def tap_coordinates(app: App, x_ratio: float, y_ratio: float) -> None:
    width, height = app.device.size()
    app.device.tap(int(width * x_ratio), int(height * y_ratio))


def foreground_package(app: App) -> str:
    activity = app.current_activity()
    return activity.split("/", 1)[0] if activity else ""
