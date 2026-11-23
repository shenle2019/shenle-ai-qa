"""统一错误类型 + 面向用户的中文提示。

所有 CLI 子命令应当只抛出下面这些异常（或 `KeyboardInterrupt`），
由 `cli.main` 统一捕获并打印为一行可读消息，避免给用户呈现 Python 堆栈。
"""

from __future__ import annotations


class CliError(Exception):
    """所有 CLI 可见错误的基类。`main` 会把它打印成一行人类可读消息。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class RequestFileNotFound(CliError):
    """请求文件不存在。"""

    def __init__(self, path: str) -> None:
        super().__init__(f"请求文件不存在：{path}")


class RequestFileInvalid(CliError):
    """请求文件无法解析为 JSON / 缺字段 / 字段类型错。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"请求文件格式错误：{detail}")


class ResultFileNotFound(CliError):
    """结果文件不存在（send 没跑过，或路径写错）。"""

    def __init__(self, path: str) -> None:
        super().__init__(f"结果文件不存在：{path}（先跑 shenle-api-cli send 生成 result 文件）")


class ResultFileInvalid(CliError):
    """结果文件无法解析为 JSON / 缺 response 段。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"结果文件格式错误：{detail}")


class HTTPRequestFailed(CliError):
    """网络层错误（DNS 失败 / 连接拒绝 / 读取超时）。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"网络请求失败：{detail}")


class HTTPStatusError(CliError):
    """4xx / 5xx 响应（默认 raise；可用 --no-fail-on-status 关闭）。"""

    def __init__(self, status: int, url: str) -> None:
        super().__init__(f"HTTP {status} {url}")


class JSONPathSyntaxError(CliError):
    """JSONPath 语法不支持（递归 / 通配 / filter 表达式等）。"""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"不支持的 JSONPath 语法：{path!r}"
            "（当前支持点路径 + 数组下标，如 $.a.b[0].c；"
            "如需完整语法请用自然语言描述或安装 jsonpath-ng 库）"
        )


class AIConfigError(CliError):
    """AI 配置缺失（API_AUTOMATION_AI_API_KEY/BASE_URL/MODEL 任一缺失）。"""

    def __init__(self, missing: list[str]) -> None:
        names = "、".join(missing)
        super().__init__(
            f"AI 配置缺失：{names}。"
            "请在 CWD/.env 或环境变量里配置（自然语言提取 / 断言需要）。"
        )


class AIRuntimeError(CliError):
    """AI 模型调用失败（网络错 / 返回非 JSON / JSON 解析失败）。"""

    def __init__(self, detail: str) -> None:
        super().__init__(f"AI 调用失败：{detail}")


class AssertFailed(CliError):
    """assert 命令业务错（自然语言断言不通过）。"""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
