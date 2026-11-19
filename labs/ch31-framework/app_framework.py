"""第 31 章：把前面几章拼成一个能交给别人的 APP 自动化入口。

组成：配置（包名/Activity/用例文件）→ 用例表 → 执行 → 报告（Markdown）。
不引入 pytest 之外的新依赖，命令行只有 `--only` / `--report` 两个开关。
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for extra in (ROOT, ROOT / "labs" / "ch26-page-object", ROOT / "labs" / "ch28-data-driven"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))


class ConfigError(ValueError):
    pass


@dataclass
class Result:
    case_id: str
    title: str
    ok: bool
    detail: str = ""
    seconds: float = 0.0


@dataclass
class Report:
    results: list[Result] = field(default_factory=list)
    started_at: str = ""
    device: str = ""

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    def to_markdown(self) -> str:
        lines = [
            "# APP 自动化执行报告",
            "",
            f"- 设备：{self.device or '未知'}",
            f"- 开始时间：{self.started_at}",
            f"- 结果：共 {self.total} 条，通过 {self.passed}，失败 {self.failed}",
            "",
            "| 用例 | 标题 | 结果 | 耗时 | 说明 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for item in self.results:
            mark = "通过" if item.ok else "失败"
            detail = (item.detail or "").replace("|", "/")[:80]
            lines.append(f"| {item.case_id} | {item.title} | {mark} | {item.seconds:.1f}s | {detail} |")
        return "\n".join(lines) + "\n"


def load_config(path: str | Path) -> dict[str, Any]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    for key in ("package", "activity", "cases"):
        if not raw.get(key):
            raise ConfigError(f"配置缺少 {key}")
    cases_path = Path(raw["cases"])
    if not cases_path.is_absolute():
        cases_path = (Path(path).parent / cases_path).resolve()
    if not cases_path.exists():
        raise ConfigError(f"用例文件不存在：{cases_path}")
    raw["cases"] = str(cases_path)
    raw.setdefault("device_timeout", 10)
    return raw


def run(page, config: dict[str, Any], *, only: str | None = None) -> Report:
    """跑一遍用例，返回报告。page 是 ch26 的页面对象。"""
    from app_runner import handlers, load_cases, run_case

    table = handlers(page)
    report = Report(started_at=time.strftime("%Y-%m-%d %H:%M:%S"), device=page.app.device.serial)
    for case in load_cases(config["cases"]):
        if only and only not in case.id:
            continue
        started = time.time()
        result = run_case(case, page, table)
        report.results.append(
            Result(result.case_id, result.title, result.ok, result.detail, time.time() - started)
        )
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    from labs._shared.adb import AdbError, Device
    from labs._shared.app import App

    from login_page import LoginDemoPage
    from labs._shared.login_server import LoginServer

    parser = argparse.ArgumentParser(description="APP 自动化入口")
    parser.add_argument("--config", default=str(HERE / "config.yaml"))
    parser.add_argument("--only", default=None, help="只跑 id 含该子串的用例")
    parser.add_argument("--report", default=None, help="报告输出路径（.md）")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    try:
        device = Device.first_online(timeout=config["device_timeout"])
    except AdbError as exc:
        print(f"没有可用设备：{exc}")
        return 2

    # 入口自己起后端并反代，别人拿到这个目录就能直接跑
    with LoginServer(8080):
        device.reverse(8080)
        page = LoginDemoPage(App(device)).open()
        report = run(page, config, only=args.only)
    text = report.to_markdown()
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"报告已写入 {target}")
    print(f"共 {report.total} 条，通过 {report.passed}，失败 {report.failed}")
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
