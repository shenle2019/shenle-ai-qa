r"""命令行入口。

    .\.venv\Scripts\python.exe labs/ch23-framework/run.py --env local
    .\.venv\Scripts\python.exe labs/ch23-framework/run.py --only login --report out.md
    .\.venv\Scripts\python.exe labs/ch23-framework/run.py --base-url http://127.0.0.1:9000 --report junit.xml

退出码：0 全通过，1 有用例失败，2 配置/环境错误。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

BROWSERS = ROOT / ".pw-browsers"
if BROWSERS.is_dir():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BROWSERS))

from playwright.sync_api import sync_playwright  # noqa: E402

import fw_report as report_mod  # noqa: E402
from fw_runner import ConfigError, load_config, pick_env, run  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="跑 Web 自动化的 YAML 用例")
    parser.add_argument("--config", default=str(HERE / "config.yaml"))
    parser.add_argument("--env", default=None, help="默认取 config 里的 default_env")
    parser.add_argument("--only", nargs="*", default=None, help="只跑 id 命中这些关键字的用例")
    parser.add_argument("--base-url", default=None, help="覆盖环境里的 base_url")
    parser.add_argument("--report", default=None, help="写报告，.xml 结尾写 JUnit，其它写 Markdown")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        env_name, env_conf = pick_env(config, args.env)
        url = args.base_url or env_conf["base_url"]
        cases = config["cases"]
        if args.only:
            cases = [case for case in cases if any(token in case["id"] for token in args.only)]
            if not cases:
                raise ConfigError(f"没有用例匹配 {args.only}")
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        result = run(page, config, env=env_name, only=args.only, base_url=url)
        context.close()
        browser.close()

    for item in result.results:
        flag = "PASS" if item.ok else "FAIL"
        print(f"[{flag}] {item.case_id:<22} {item.duration_ms:>5} ms  {item.detail}")
    print(f"\n合计 {result.total} 条，通过 {result.passed}，失败 {result.failed}（环境 {result.env} · {result.base_url}）")

    if args.report:
        path = report_mod.write(result, args.report)
        print(f"报告已写入：{path}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
