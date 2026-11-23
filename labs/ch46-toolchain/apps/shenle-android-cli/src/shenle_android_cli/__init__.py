"""shenle-android-cli: 命令行驱动的安卓 UI 自动化工具（adb shell input）。

Phase 1 只搭 CLI 骨架：devices / start / launch / close。
后续阶段会加入截图、UI 树抓取、AI 视觉定位、坐标点击、滑动等原子操作，
供大模型按自然语言指令调用。
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
