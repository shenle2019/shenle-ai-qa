"""CLI 入口：选环境、跑用例、出报告。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from fw_config import ENVS

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="接口自动化框架入口")
    parser.add_argument("--env", default="local", choices=sorted(ENVS), help="目标环境")
    parser.add_argument("-m", "--marker", default="", help="pytest 标记，如 smoke")
    parser.add_argument("--report", action="store_true", help="生成 HTML 报告")
    args = parser.parse_args(argv)

    cmd = [sys.executable, "-m", "pytest", str(HERE), "-q"]
    if args.marker:
        cmd += ["-m", args.marker]
    xml = HERE / "report.xml"
    cmd.append(f"--junitxml={xml}")
    print("运行:", " ".join(cmd[3:]), "| 环境:", args.env)
    code = subprocess.call(cmd)

    if args.report and xml.exists():
        report = HERE.parent / "ch14-report-assert" / "report.py"
        subprocess.call([sys.executable, str(report), str(xml), str(HERE / "report.html")])
        print("报告:", HERE / "report.html")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
