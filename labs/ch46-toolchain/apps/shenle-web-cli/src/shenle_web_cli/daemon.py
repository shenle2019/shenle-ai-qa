"""后台浏览器守护进程：`start` 命令会 fork 出本进程独享浏览器。

职责
----
1. 用 Playwright 的 *persistent context* 拉起 Chromium，并把
   `--remote-debugging-port=<port>` 加进参数，让外部 CDP 客户端
   （包括后续阶段的 `navigate` / `click` 等）能直接 `connect_over_cdp`。
2. 维护 state.json 的三态：`spawning` → `running` → 文件被删。
3. 监听 SIGTERM / SIGINT / Ctrl+Break，收到后优雅地关闭 context 再退出。

注意
----
- 本模块是被父进程用 `python -m shenle_web_cli.daemon ...` 拉起的，
  不要在 `__main__` 里跑复杂逻辑。
- 持久化的 user-data-dir 由 `--data-dir` 参数传入（per-port 独立：
  `cwd/user_data/<port>/`），跨 `start/close` 复用同一份，登录态 / Cookie
  不会丢。
"""

from __future__ import annotations

import argparse
import asyncio
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from playwright.async_api import async_playwright

from . import state


# ---------------------------------------------------------------------------
# 入口


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="shenle-web-cli-daemon",
        description=(
            "shenle-web-cli 的内部守护进程。不要直接调用，"
            "它由 `shenle-web-cli start` 自动拉起。"
        ),
    )
    p.add_argument("--port", type=int, default=9222, help="CDP 端口")
    p.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Chromium user-data-dir（必填，由 start 计算后传入）",
    )
    p.add_argument("--headless", action="store_true", help="无头模式")
    p.add_argument("--debug", action="store_true", help="启用调试日志")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    data_dir = Path(args.data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    state.app_dir().mkdir(parents=True, exist_ok=True)

    # 先写一个 spawning 占位（端口未定，因为浏览器还没起来，但端口已经知道）。
    # 父进程会读这个状态：status=running 才算"连上了"。
    state.write_state(args.port, {
        "version": 2,
        "status": "spawning",
        "pid": os.getpid(),
        "port": args.port,
        "data_dir": str(data_dir),
        "headless": bool(args.headless),
        "started_at": datetime.now(timezone.utc).isoformat(),
    })
    print(
        f"[shenle-daemon] started pid={os.getpid()} port={args.port} "
        f"headless={args.headless} data_dir={data_dir}",
        flush=True,
    )

    try:
        asyncio.run(_run(args.port, bool(args.headless), data_dir, bool(args.debug)))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # 把异常写到 state.json 里，方便父进程报给用户
        state.write_state(args.port, {
            "version": 2,
            "status": "failed",
            "pid": os.getpid(),
            "port": args.port,
            "error": f"{type(e).__name__}: {e}",
        })
        return 1
    finally:
        state.clear_state(args.port)
    return 0


# ---------------------------------------------------------------------------
# 异步主体


async def _run(port: int, headless: bool, data_dir: Path, debug: bool) -> None:
    args_list = [
        f"--remote-debugging-port={port}",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    if debug:
        print(
            f"[shenle-daemon] launching: headless={headless} port={port} "
            f"data_dir={data_dir}",
            flush=True,
        )

    stop = asyncio.Event()

    def _request_stop(*_a) -> None:
        if not stop.is_set():
            if debug:
                print("[shenle-daemon] stop signal received", flush=True)
            stop.set()

    # 跨平台信号监听
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_stop)
        except (NotImplementedError, RuntimeError):
            pass
    if sys.platform == "win32":
        try:
            signal.signal(signal.CTRL_BREAK_EVENT, _request_stop)
        except (ValueError, OSError):
            pass

    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(data_dir),
                headless=headless,
                args=args_list,
            )
        except Exception as e:
            # Playwright 的 EADDRINUSE / 浏览器下载失败 / 配置错误都走到这里
            raise

        # 浏览器起来了，升级 state 到 running
        state.write_state(port, {
            "version": 2,
            "status": "running",
            "pid": os.getpid(),
            "port": port,
            "data_dir": str(data_dir),
            "headless": headless,
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        if debug:
            print("[shenle-daemon] browser up, holding open...", flush=True)
        print("[shenle-daemon] browser up", flush=True)

        try:
            await stop.wait()
        finally:
            print("[shenle-daemon] stopping...", flush=True)
            try:
                await context.close()
            except Exception:
                pass
            print("[shenle-daemon] stopped", flush=True)


if __name__ == "__main__":
    sys.exit(main())
