"""统一错误类型 + 面向用户的中文提示。

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


class BrowserNotRunning(CliError):
    """某个需要浏览器的命令被调用，但后台浏览器没起来。"""

    def __init__(self) -> None:
        super().__init__("未连接到当前设备，请先运行 shenle-web-cli start")


class AlreadyRunning(CliError):
    """再调一次 start，但后台已经有浏览器实例。"""

    def __init__(self, port: int, pid: int) -> None:
        super().__init__(
            f"浏览器已在后台运行（端口 {port}，pid {pid}）。"
            "如需重启请先 shenle-web-cli close。"
        )


class PortInUse(CliError):
    """指定端口已被其他进程占用。"""

    def __init__(self, port: int) -> None:
        super().__init__(
            f"端口 {port} 已被占用。"
            f"请换一个端口（如 shenle-web-cli start --port 9223），"
            "或先关闭占用该端口的进程。"
        )


class DaemonStartFailed(CliError):
    """daemon 子进程没能成功启动浏览器。"""

    def __init__(self, detail: str = "") -> None:
        msg = "后台浏览器启动失败"
        if detail:
            msg += f"：{detail}"
        super().__init__(msg)
