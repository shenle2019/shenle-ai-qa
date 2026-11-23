"""shenle-api-cli: 命令行驱动的接口调用工具（requests）。

替代 curl 给 AI 跑 API 任务。统一中文路径 / 引号转义，请求/响应自动落盘到
系统 temp 目录的 shenle-api-results/ 供后续 extract/assert/call 命令复用。

0.2 新增 `call` 子命令：send + extract 一步到位，避免 Windows cmd.exe / bash 跨平台
shell 兼容问题（agentscope 的 Bash 工具在 Windows 上强制走 cmd.exe）。
"""

__version__ = "0.2.0"

__all__ = ["__version__"]
