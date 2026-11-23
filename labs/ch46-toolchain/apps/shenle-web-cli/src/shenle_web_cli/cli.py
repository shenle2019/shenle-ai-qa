"""CLI 入口：argparse 分发 + 统一异常处理。"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from dotenv import dotenv_values

from . import __version__, state
from .commands import (
    cmd_batch,
    cmd_click,
    cmd_click_at,
    cmd_get,
    cmd_input,
    cmd_input_at,
    cmd_navigate,
    cmd_scroll,
    cmd_screenshot,
    cmd_swipe_to,
    cmd_title,
    cmd_url,
)
from .errors import (
    AlreadyRunning,
    BrowserNotRunning,
    CliError,
    DaemonStartFailed,
    PortInUse,
)

# Windows 默认控制台是 GBK，argparse 拿到中文 description 会乱码。
# 在打印任何东西之前，把 stdout/stderr 强切到 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass


# ---------------------------------------------------------------------------
# parser


def build_parser() -> argparse.ArgumentParser:
    # 全局参数：可以出现在 <command> 之前（顶层）或之后（子命令）。
    # 关键：用 argparse.SUPPRESS 当默认值，这样顶层解析了 --port 之后，
    # 子解析器没看到 --port 就不会用 None 把顶层的值覆盖掉。
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--port", type=int, default=argparse.SUPPRESS,
        help="CDP 端口（start 默认 9222，其它命令读 state.json）",
    )
    shared.add_argument(
        "--headless", action="store_true", default=argparse.SUPPRESS,
        help="无头模式（仅 start 有意义）",
    )
    shared.add_argument(
        "--debug", action="store_true", default=argparse.SUPPRESS,
        help="调试模式：内部异常打印完整堆栈（默认仅一行提示）",
    )

    parser = argparse.ArgumentParser(
        prog="shenle-web-cli",
        description=(
            "命令行驱动的浏览器自动化工具（Playwright + CDP）。"
            "后续供 AI 按自然语言调用。"
        ),
        parents=[shared],
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # ---- start ----
    start_p = sub.add_parser(
        "start",
        help="启动一个后台浏览器（CDP 监听 --port），可被后续命令反复连接",
        description=(
            "拉起一个独立的 Chromium 进程，通过 CDP 监听在 --port 端口。"
            "Cookie / 登录态保存在固定的 user-data-dir，下次 start 自动复用。"
            "进程在后台常驻，用 `shenle-web-cli close` 关闭。"
        ),
        parents=[shared],
    )

    # ---- close ----
    sub.add_parser("close", help="关闭后台浏览器", parents=[shared])

    # ---- navigate ----
    navigate_p = sub.add_parser(
        "navigate",
        help="打开网址，并把 viewport 拉到 1440x900",
        description="打开 <url>，自动补全 https:// 前缀；viewport 设为 1440x900。",
        parents=[shared],
    )
    navigate_p.add_argument("url", help="要打开的网址（可省略 https://）")

    # ---- screenshot ----
    screenshot_p = sub.add_parser(
        "screenshot",
        help="把当前页面截图到文件",
        description="截当前 viewport（不是整页）到指定路径。",
        parents=[shared],
    )
    screenshot_p.add_argument("path", help="输出图片路径（.png）")

    # ---- click ----
    click_p = sub.add_parser(
        "click",
        help="AI 视觉定位并点击一个元素",
        description=(
            "先用 Playwright 截当前 viewport 发给视觉模型，让它返回"
            "待点击元素的像素坐标，再调用 page.mouse.click。"
        ),
        parents=[shared],
    )
    click_p.add_argument("description", help="元素的自然语言描述（如「登录按钮」）")
    click_p.add_argument(
        "--enhanced", "-e",
        help="追加描述（消歧用，如「右上角、蓝色」）",
    )
    click_p.add_argument(
        "--screenshot", "-s", dest="post_shot",
        help="操作完成后额外保存一张截图",
    )

    # ---- input ----
    input_p = sub.add_parser(
        "input",
        help="AI 视觉定位一个输入框并填入文本（中文 OK）",
        description=(
            "AI 视觉定位输入框坐标 → 鼠标点击 → keyboard.insert_text 整串填入。"
            "中文 / 长字符串都用 insert_text（不逐字符触发 keypress）。"
        ),
        parents=[shared],
    )
    input_p.add_argument("description", help="输入框的自然语言描述（如「用户名」）")
    input_p.add_argument("text", help="要输入的文本")
    input_p.add_argument("--enhanced", "-e", help="追加描述")
    input_p.add_argument(
        "--screenshot", "-s", dest="post_shot",
        help="操作完成后额外保存一张截图",
    )

    # ---- scroll ----
    scroll_p = sub.add_parser(
        "scroll",
        help="滚动页面（支持指定区域内滚动）",
        description=(
            "无 --region：用 mouse.wheel 滚整个页面。"
            "有 --region：先 AI 视觉定位区域 bbox，鼠标移到区域中心再滚，"
            "wheel 事件作用在该元素上（而不是页面）。"
        ),
        parents=[shared],
    )
    scroll_p.add_argument(
        "direction",
        choices=["up", "down", "left", "right"],
        help="滚动方向",
    )
    scroll_p.add_argument(
        "-c", "--count", type=int, default=1,
        help="滚动次数（默认 1）",
    )
    scroll_p.add_argument(
        "--region",
        help="区域描述（如「左侧菜单」）；指定后只滚该元素内的内容",
    )
    scroll_p.add_argument(
        "-s", "--screenshot", dest="post_shot",
        help="操作完成后额外保存一张截图",
    )

    # ---- get ----
    get_p = sub.add_parser(
        "get",
        help="AI 视觉描述页面某个区域的内容（4 段结构化文本）",
        description=(
            "截当前 viewport 发给视觉模型，按 ## 布局 / ## 图标 / ## 文字 / "
            "## 介绍 四节输出。"
            "状态行打 stderr，内容打 stdout，方便脚本直接 capture stdout。"
        ),
        parents=[shared],
    )
    get_p.add_argument("description", help="区域描述（如「顶部导航栏」「搜索结果列表」）")
    get_p.add_argument(
        "-s", "--screenshot", dest="post_shot",
        help="操作完成后额外保存一张截图",
    )

    # ---- url / title（只读断言） ----
    url_p = sub.add_parser(
        "url",
        help="输出当前页面 URL（默认纯文本，--format json 同时输出 title）",
        description="纯文本模式只打印 URL；--format json 输出 {url, title}。",
        parents=[shared],
    )
    url_p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="输出格式（默认 text）",
    )

    title_p = sub.add_parser(
        "title",
        help="输出当前页面 title（默认纯文本，--format json 同时输出 url）",
        description="纯文本模式只打印 title；--format json 输出 {url, title}。",
        parents=[shared],
    )
    title_p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="输出格式（默认 text）",
    )

    # ---- batch（一次截图 + 一次 AI 识别多个元素）----
    batch_p = sub.add_parser(
        "batch",
        help="批量执行多个操作（一次截图识别所有 AI 元素，性能优化）",
        description=(
            "把多个 click/input/click-at/input-at 串成一个 batch：\n"
            "  - AI 元素只截一次图、只调一次 AI\n"
            "  - 按给定顺序依次执行\n"
            "  - 每个元素描述一次到位\n\n"
            "语法（空格分隔，描述可含空格）：\n"
            "  click <描述>\n"
            '  input <描述>::<文本>      （描述与文本用 :: 分隔）\n'
            "  click-at <x> <y>\n"
            "  input-at <x> <y> <文本>\n\n"
            "示例：\n"
            '  shenle-web-cli batch input "用户名::admin" '
            'input "密码::123" click "登录"\n'
            "  shenle-web-cli batch click-at 100 200 click \"搜索框\""
        ),
        parents=[shared],
    )
    batch_p.add_argument(
        "ops", nargs="+",
        help="操作序列（按上面语法拼接）",
    )

    # ---- 原始坐标命令（无 AI）----
    click_at_p = sub.add_parser(
        "click-at", help="点击指定像素坐标（无 AI）", parents=[shared],
    )
    click_at_p.add_argument("x", type=int, help="目标像素 X")
    click_at_p.add_argument("y", type=int, help="目标像素 Y")

    input_at_p = sub.add_parser(
        "input-at", help="在指定坐标点击并输入文本（无 AI）", parents=[shared],
    )
    input_at_p.add_argument("x", type=int, help="目标像素 X")
    input_at_p.add_argument("y", type=int, help="目标像素 Y")
    input_at_p.add_argument("text", help="要输入的文本")

    swipe_p = sub.add_parser(
        "swipe-to",
        help="从 (x1,y1) 拖到 (x2,y2)（无 AI，模拟滑动/拖拽）",
        parents=[shared],
    )
    swipe_p.add_argument("x1", type=int, help="起点像素 X")
    swipe_p.add_argument("y1", type=int, help="起点像素 Y")
    swipe_p.add_argument("x2", type=int, help="终点像素 X")
    swipe_p.add_argument("y2", type=int, help="终点像素 Y")

    # 给 navigate / screenshot / click / input / scroll / get / batch /
    # 原始坐标命令都补 --on-dialog 和 --prompt-text
    for p in (
        navigate_p, screenshot_p,
        click_p, input_p, scroll_p, get_p, url_p, title_p,
        batch_p, click_at_p, input_at_p, swipe_p,
    ):
        p.add_argument(
            "--on-dialog", choices=["accept", "dismiss"], default=None,
            help="弹窗处理策略（alert/confirm/prompt）",
        )
        p.add_argument(
            "--prompt-text", default=None,
            help="prompt 弹窗填入文本（仅 --on-dialog accept 时有效）",
        )

    # screenshot 再补 --format / --quality
    screenshot_p.add_argument(
        "--format", choices=["auto", "png", "jpeg"], default="auto",
        help="输出格式；auto 按扩展名推断（默认）",
    )
    screenshot_p.add_argument(
        "--quality", type=int, default=85,
        help="JPEG 质量 1-100（默认 85）",
    )

    return parser


# ---------------------------------------------------------------------------
# 子命令实现（start / close）


def _precheck_port_free(port: int) -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        raise PortInUse(port)
    finally:
        s.close()


def _spawn_daemon(port: int, headless: bool, debug: bool, data_dir: Path) -> None:
    log_path = state.log_file()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_path, "ab", buffering=0)

    args = [
        sys.executable, "-m", "shenle_web_cli.daemon",
        "--port", str(port),
        "--data-dir", str(data_dir),
    ]
    if headless:
        args.append("--headless")
    if debug:
        args.append("--debug")

    # start 时强制把 CWD/.env 的变量同步到 daemon 子进程环境变量。
    # - 用 dotenv_values() 直接读文件，不污染当前 CLI 进程的环境
    # - 真实 shell 环境变量优先于 .env（if k not in env）
    # - 这样不管用户后面切到哪个目录跑 click/input，
    #   daemon 进程里看到的都是 start 时确定的 CWD/.env 那一份
    env = os.environ.copy()
    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.is_file():
        for k, v in dotenv_values(dotenv_path).items():
            if v is not None and k not in env:
                env[k] = v

    kwargs: dict = {
        "stdin": subprocess.DEVNULL,
        "stdout": log_fh,
        "stderr": log_fh,
        "close_fds": True,
        "env": env,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(args, **kwargs)
    log_fh.close()


def _cmd_start(args: argparse.Namespace) -> int:
    port = getattr(args, "port", None) or 9222
    headless = getattr(args, "headless", False)
    debug = getattr(args, "debug", False)

    if state.is_running(port):
        cur = state.inspect(port)
        raise AlreadyRunning(cur.port or port, cur.pid or 0)

    # 清掉这个端口的旧 state（spawning 但死了等）
    state.clear_state(port)

    _precheck_port_free(port)

    # per-port user_data 目录：cwd/user_data/<port>/
    # start 时的 cwd 会记到 state.json，后续命令读它（避免 cwd 漂移）
    data_dir = (Path.cwd() / "user_data" / str(port)).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    _spawn_daemon(port, headless, debug, data_dir)

    final = state.wait_for_running(port, timeout_s=30.0)
    if not final.running:
        if final.pid:
            state.kill(final.pid, grace_s=2.0)
        raise DaemonStartFailed(final.detail or "未知原因")

    headless_note = "（无头模式）" if headless else "（系统窗口可见）"
    print(
        f"[shenle] 浏览器已启动 {headless_note}："
        f"CDP 端口 {final.port}，pid {final.pid}"
    )
    print(f"[shenle] 数据目录：{data_dir}")
    if not headless:
        print("[shenle] 提示：用 shenle-web-cli close 关闭浏览器。")
    return 0


def _cmd_close(args: argparse.Namespace) -> int:
    """关掉后台浏览器。不带 --port 时关掉所有在跑的；带 --port 时只关那个。"""
    port = getattr(args, "port", None)

    if port is not None:
        if not state.is_running(port):
            raise BrowserNotRunning()
        cur = state.inspect(port)
        state.kill(cur.pid or 0, grace_s=5.0)
        print(f"[shenle] 浏览器已关闭（端口 {port}）")
        return 0

    # 不带 --port：关掉所有
    running = state.list_running_ports()
    if not running:
        raise BrowserNotRunning()
    for p in running:
        cur = state.inspect(p)
        state.kill(cur.pid or 0, grace_s=5.0)
        print(f"[shenle] 浏览器已关闭（端口 {p}）")
    return 0


# ---------------------------------------------------------------------------
# main


_HANDLERS = {
    "start": _cmd_start,
    "close": _cmd_close,
    "navigate": cmd_navigate,
    "screenshot": cmd_screenshot,
    "click": cmd_click,
    "input": cmd_input,
    "scroll": cmd_scroll,
    "get": cmd_get,
    "url": cmd_url,
    "title": cmd_title,
    "batch": cmd_batch,
    "click-at": cmd_click_at,
    "input-at": cmd_input_at,
    "swipe-to": cmd_swipe_to,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    handler = _HANDLERS[args.command]
    try:
        if inspect.iscoroutinefunction(handler):
            return asyncio.run(handler(args))
        return handler(args)
    except CliError as e:
        # 4 个原子操作命令统一走 [FAIL] <cmd>: <msg>；
        # 启停类 (start/close) 走旧的 [shenle] 错误：<msg>
        if args.command in ("start", "close"):
            print(f"[shenle] {e.message}", file=sys.stderr)
        else:
            print(f"[FAIL] {args.command}: {e.message}")
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        if args.debug:
            raise
        # 原子操作的未知异常也走 [FAIL] 格式
        if args.command in ("start", "close"):
            print(f"[shenle] 内部错误：{e}", file=sys.stderr)
            print("[shenle] 提示：用 --debug 重试可看到完整堆栈。", file=sys.stderr)
        else:
            print(f"[FAIL] {args.command}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
