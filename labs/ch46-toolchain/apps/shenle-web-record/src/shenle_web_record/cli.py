"""shenle-web-record: minimal interactive web page recorder (screenshot + DOM)."""
from __future__ import annotations

import argparse
import sys

from shenle_web_record import __version__


def run_session(url: str, output: str) -> int:
    """Open headed Chromium with SNAP button; block until browser closes."""
    import asyncio
    from shenle_web_record.session import RecorderSession  # lazy import

    session = RecorderSession(url=url, output_root=output)
    return asyncio.run(session.run())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shenle-web-record",
        description="Record a web page interactively: click the SNAP button to capture viewport + DOM.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    record_cmd = subparsers.add_parser("record", help="open a URL in a headed browser with a SNAP button")
    record_cmd.add_argument("url", help="URL to record (e.g. https://example.com)")
    record_cmd.add_argument(
        "-o",
        "--output",
        default=".",
        help="batch root directory (default: current directory)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "record":
        return run_session(args.url, args.output)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())