"""CLI 入口：argparse 分发 + 统一异常处理。

所有命令以单行 `[OK] ...` 或 `[FAIL] ...` + exit 0/1/2 结束，
方便上层（人 / AI / runner）parse。
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__
from .commands import cmd_assert, cmd_call, cmd_extract, cmd_send
from .errors import CliError


# Windows 默认控制台是 GBK，argparse 拿到中文 description 会乱码。
# 在打印任何东西之前，把 stdout/stderr 强切到 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass


def build_parser() -> argparse.ArgumentParser:
    """构造顶层 parser + 3 个子命令。"""
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--debug", action="store_true", default=False,
        help="调试模式：内部异常打印完整堆栈（默认仅一行提示）",
    )

    parser = argparse.ArgumentParser(
        prog="shenle-api-cli",
        description=(
            "命令行驱动的接口调用工具（requests），"
            "替代 curl 给 AI 跑 API 任务。"
        ),
        parents=[shared],
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # ---- send ----
    send_p = sub.add_parser(
        "send",
        help="发送一次 HTTP 请求并把 request/response 落盘到 result 文件",
        description=(
            "读取请求描述（文件路径或 stdin），发 HTTP，"
            "把 {request, response, meta} 写入系统 temp 目录的 shenle-api-results/。"
        ),
        parents=[shared],
    )
    send_p.add_argument(
        "req_path", nargs="?",
        help="请求 JSON 文件路径（不传则走 stdin）",
    )
    send_p.add_argument(
        "--input", "-i", default=None, metavar="PATH",
        help="同 req_path，等价写法",
    )
    send_p.add_argument(
        "--output-dir", "-o", default=None, metavar="DIR",
        help="结果文件输出目录（默认系统 temp / shenle-api-results/）",
    )
    send_p.add_argument(
        "--timeout", type=float, default=30.0, metavar="SECS",
        help="请求超时秒数（默认 30）",
    )
    send_p.add_argument(
        "--no-verify-ssl", action="store_true",
        help="不校验 HTTPS 证书（自签证书场景）",
    )
    send_p.add_argument(
        "--no-fail-on-status", action="store_true",
        help="4xx/5xx 不抛错（仍落盘，但返回 0）",
    )

    # ---- extract ----
    extract_p = sub.add_parser(
        "extract",
        help="从 send 生成的结果文件中提取变量（JSONPath 或自然语言）",
        description=(
            "field 以 $ 开头 → 走本地 JSONPath；"
            "否则走 AI 自然语言提取（需配置 API_AUTOMATION_AI_*）。"
        ),
        parents=[shared],
    )
    extract_p.add_argument("result_path", help="send 生成的结果 JSON 文件路径")
    extract_p.add_argument(
        "--field", "-f", required=True, metavar="FIELD",
        help="JSONPath（如 $.data.token）或自然语言描述（如 '登录返回的 token'）",
    )
    extract_p.add_argument(
        "--name", "-n", default=None,
        help="输出时的字段名（默认用 field 本身）",
    )

    # ---- call (0.2 新增：send + extract 一步到位) ----
    call_p = sub.add_parser(
        "call",
        help="【推荐】send + extract 一步到位：发请求并抽取字段，单次 bash 调用搞定",
        description=(
            "一步完成 send + extract，避免跨平台 shell 兼容问题。\n"
            "Windows 上 agentscope 的 Bash 工具走 cmd.exe，跟 bash 语法不兼容，\n"
            "所以需要把 send+extract 合并到一个命令里。\n"
            "输出单行：[OK] call: status=200 ... name=<字段名> value=<值>"
        ),
        parents=[shared],
    )
    call_p.add_argument(
        "req_path", nargs="?",
        help="请求 JSON 文件路径（不传则走 stdin）",
    )
    call_p.add_argument(
        "--input", "-i", default=None, metavar="PATH",
        help="同 req_path，等价写法",
    )
    call_p.add_argument(
        "--field", "-f", required=True, metavar="FIELD",
        help="JSONPath（如 $.data.token）或自然语言描述（如 '登录返回的 token'）",
    )
    call_p.add_argument(
        "--name", "-n", default=None,
        help="输出时的字段名（默认 'value'）",
    )
    call_p.add_argument(
        "--output-dir", "-o", default=None, metavar="DIR",
        help="结果文件输出目录（默认系统 temp / shenle-api-results/）",
    )
    call_p.add_argument(
        "--timeout", type=float, default=30.0, metavar="SECS",
        help="请求超时秒数（默认 30）",
    )
    call_p.add_argument(
        "--no-verify-ssl", action="store_true",
        help="不校验 HTTPS 证书（自签证书场景）",
    )
    call_p.add_argument(
        "--no-fail-on-status", action="store_true",
        help="4xx/5xx 不抛错（仍落盘 + 抽取字段，但返回 0）",
    )

    # ---- assert ----
    assert_p = sub.add_parser(
        "assert",
        help="用自然语言断言接口响应（需要 AI 配置）",
        description=(
            "把响应喂给 AI 判断断言是否成立。"
            "通过 → exit 0；不通过 → exit 1（打印 [FAIL]）。"
        ),
        parents=[shared],
    )
    assert_p.add_argument("result_path", help="send 生成的结果 JSON 文件路径")
    assert_p.add_argument(
        "assertion",
        help="中文自然语言断言（如 '响应状态码是 200 且 code=200'）",
    )

    return parser


_HANDLERS = {
    "send": cmd_send,
    "extract": cmd_extract,
    "call": cmd_call,
    "assert": cmd_assert,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    handler = _HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        return 0

    try:
        return handler(args)
    except CliError as e:
        print(f"[FAIL] {args.command}: {e.message}")
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        if getattr(args, "debug", False):
            raise
        print(f"[FAIL] {args.command}: {e}")
        print(f"[FAIL] 提示：用 --debug 重试可看到完整堆栈。")
        return 2


if __name__ == "__main__":
    sys.exit(main())
