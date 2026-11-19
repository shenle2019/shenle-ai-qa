"""把「设备」包成「界面」：dump 一次、找节点、点节点、等文本。

这一层是后面所有 APP 章节的地基，不依赖任何第三方库。
"""

from __future__ import annotations

import time
from typing import Callable

from labs._shared.adb import AdbError, Device
from labs._shared.ui_tree import Node, parse_dump


class AppError(RuntimeError):
    """找不到节点、等不到界面这类错误。"""


class App:
    def __init__(self, device: Device, *, poll: float = 0.4, dump_retries: int = 3):
        self.device = device
        self.poll = poll
        self.dump_retries = dump_retries

    # ---------- 读界面 ----------

    def tree(self) -> Node:
        """拿一帧窗口树。dump 偶尔会失败（界面正在动画），所以重试几次。"""
        last: Exception | None = None
        for _ in range(self.dump_retries):
            try:
                return parse_dump(self.device.dump_ui())
            except (AdbError, ValueError) as exc:  # 抖动一下再来
                last = exc
                time.sleep(self.poll)
        raise AppError(f"取窗口树失败：{last}")

    def find(self, **criteria) -> Node:
        return self.tree().find(**criteria)

    def maybe(self, **criteria) -> Node | None:
        try:
            return self.tree().find(**criteria)
        except LookupError:
            return None

    def text_of(self, *, id_short: str | None = None, timeout: float = 5) -> str:
        node = self.wait_for(lambda n: self._matches(n, id_short=id_short), timeout=timeout)
        return node.label

    # ---------- 等界面 ----------

    def wait_for(self, predicate: Callable[[Node], bool], *, timeout: float = 10) -> Node:
        """轮询直到树里出现满足条件的节点，超时抛 AppError 并附上最后一帧的关键节点。"""
        deadline = time.time() + timeout
        last: Node | None = None
        while time.time() < deadline:
            try:
                last = self.tree()
            except AppError:
                time.sleep(self.poll)
                continue
            for node in last.walk():
                if predicate(node):
                    return node
            time.sleep(self.poll)
        hint = ""
        if last is not None:
            labels = [n.label for n in last.walk() if n.label][:8]
            hint = "；当前界面：" + " / ".join(labels)
        raise AppError(f"等待 {timeout}s 仍未出现目标节点{hint}")

    def wait_text(self, text: str, *, timeout: float = 10, contains: bool = True) -> Node:
        def match(node: Node) -> bool:
            if contains:
                return text in node.text or text in node.content_desc
            return node.text == text or node.content_desc == text

        return self.wait_for(match, timeout=timeout)

    def wait_gone(self, text: str, *, timeout: float = 10) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                tree = self.tree()
            except AppError:
                time.sleep(self.poll)
                continue
            if not any(text in n.text or text in n.content_desc for n in tree.walk()):
                return
            time.sleep(self.poll)
        raise AppError(f"{timeout}s 内「{text}」一直没消失")

    # ---------- 动界面 ----------

    def tap(self, *, timeout: float = 10, **criteria) -> Node:
        node = self.wait_for(lambda n: self._matches(n, **criteria), timeout=timeout)
        x, y = node.center
        self.device.tap(x, y)
        return node

    def tap_text(self, text: str, *, timeout: float = 10) -> Node:
        return self.tap(text=text, timeout=timeout)

    def input_into(self, text: str, *, id_short: str | None = None, timeout: float = 10) -> Node:
        """点中输入框、清空、再输入。input text 不支持中文与空格，空格会转 %s。"""
        node = self.tap(id_short=id_short, timeout=timeout)
        self.device.keyevent("KEYCODE_MOVE_END")
        for _ in range(3):
            self.device.keyevent("KEYCODE_DEL")
        self.device.input_text(text)
        return node

    def swipe_up(self, *, steps: int = 1, duration: int = 300) -> None:
        width, height = self.device.size()
        x = width // 2
        for _ in range(steps):
            self.device.swipe(x, int(height * 0.75), x, int(height * 0.30), duration)

    # ---------- 留证 ----------

    def screenshot(self, path) -> str:
        return str(self.device.screenshot(path))

    def current_activity(self) -> str:
        return self.device.current_activity()

    # ---------- 内部 ----------

    @staticmethod
    def _matches(node: Node, **criteria) -> bool:
        try:
            return node.matches(**criteria)
        except TypeError:
            return False
