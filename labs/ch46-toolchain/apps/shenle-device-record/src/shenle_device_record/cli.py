"""shenle-device-record：设备端界面采集命令行入口。"""
from __future__ import annotations

import argparse
import sys

from shenle_device_record import LOG_PREFIX, __version__

ALL_PLATFORMS = ("android", "ios", "harmony", "pc")
SUPPORTED_PLATFORMS = ("android",)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shenle-device-record",
        description="设备端界面采集：截当前屏幕 + 抓界面结构，按约定格式落盘。",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    record_cmd = subparsers.add_parser("record", help="采集一次当前屏幕")
    record_cmd.add_argument(
        "--platform",
        required=True,
        choices=ALL_PLATFORMS,
        help="目标平台（第一阶段仅实现 android）",
    )
    record_cmd.add_argument(
        "--device-id", default=None, help="设备序列号；不传则用第一台可用设备"
    )
    record_cmd.add_argument(
        "-o", "--output", default=".", help="批次根目录，默认当前目录"
    )

    # ---- serve 子命令 ----
    serve_cmd = subparsers.add_parser(
        "serve", help="起本地 HTTP+WebSocket 服务并自动开浏览器；网页实时画面 + 采集"
    )
    serve_cmd.add_argument(
        "--platform",
        required=True,
        choices=ALL_PLATFORMS,
        help="目标平台（第一/三阶段仅实现 android）",
    )
    serve_cmd.add_argument(
        "--device-id", default=None, help="设备序列号；不传则用第一台可用设备"
    )
    serve_cmd.add_argument(
        "-o", "--output", default=".", help="批次根目录，默认当前目录"
    )
    serve_cmd.add_argument(
        "--port", type=int, default=8765, help="HTTP / WebSocket 端口，默认 8765"
    )
    serve_cmd.add_argument(
        "--no-browser", action="store_true",
        help="不自动开浏览器（用于 headless / CI / 调试）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "record" and args.command != "serve":
        parser.print_help()
        return 1

    if args.command == "record":
        if args.platform not in SUPPORTED_PLATFORMS:
            print(
                f"{LOG_PREFIX} 暂未支持 {args.platform}，第一阶段仅 android。",
                file=sys.stderr,
            )
            return 2

        from shenle_device_record.recorder import record_once  # 延迟导入，加快 --help

        return record_once(args.platform, args.device_id, args.output)

    # ---- serve 分发 ----
    if args.platform not in SUPPORTED_PLATFORMS:
        print(
            f"{LOG_PREFIX} 暂未支持 {args.platform}，第一/三阶段仅 android。",
            file=sys.stderr,
        )
        return 2

    from shenle_device_record.server.lifecycle import LifecycleManager
    from shenle_device_record.server.ws_handler import WSHandler

    import os
    static_root = os.path.join(os.path.dirname(__file__), "static")

    async def factory(websocket):
        # 每个 WebSocket 连接 = 一个 WSHandler 实例；handler.serve() 内部
        # 完成 hello、发推流协程、收消息循环，函数返回即连接结束。
        handler = WSHandler(
            websocket=websocket,
            device_id=args.device_id or "",  # 空串时由 recorder 端选第一台
            output_root=args.output,
            platform=args.platform,
        )
        await handler.serve()

    manager = LifecycleManager(
        host="127.0.0.1",
        port=args.port,
        device_id=args.device_id or "",
        output_root=args.output,
        platform=args.platform,
        no_browser=args.no_browser,
        ws_handler_factory=factory,
        static_root=static_root,
    )
    return manager.start_and_wait()


if __name__ == "__main__":
    sys.exit(main())