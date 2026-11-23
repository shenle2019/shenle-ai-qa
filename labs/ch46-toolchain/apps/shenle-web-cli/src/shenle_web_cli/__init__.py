"""shenle-web-cli: 命令行驱动的浏览器自动化工具（Playwright + CDP）。

当前阶段只负责启动 / 关闭一个长生命周期的浏览器进程，后续阶段会
在此基础上提供 navigate / click / input / screenshot 等原子操作，
供大模型按自然语言指令调用。
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
