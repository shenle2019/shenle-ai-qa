"""第 39 章：把前面八章拼成一个能交给别人的性能平台。

三件事：读配置、跑场景、按门槛出报告与退出码。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

__all__ = ["ConfigError", "ScenarioSpec", "Result", "Report", "load_config", "gate", "to_markdown", "main"]


class ConfigError(ValueError):
    pass


@dataclass
class ScenarioSpec:
    name: str
    levels: list[int]
    duration_s: float = 1.0
    p95_limit_ms: float = 300.0
    error_limit: float = 0.01


@dataclass
class Result:
    name: str
    concurrency: int
    tps: float
    p95_ms: float
    error_rate: float

    @property
    def ok(self) -> bool:
        return self.error_rate <= 0.0 and self.p95_ms >= 0

    def passed(self, spec: ScenarioSpec) -> bool:
        return self.p95_ms <= spec.p95_limit_ms and self.error_rate <= spec.error_limit


@dataclass
class Report:
    env: str
    results: list[Result] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return self.total - len(self.failures)

    @property
    def ok(self) -> bool:
        return not self.failures


def load_config(path: str | Path) -> dict:
    import yaml

    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if "default_env" not in raw:
        raise ConfigError("缺少 default_env")
    envs = raw.get("envs") or {}
    if not envs:
        raise ConfigError("至少要有一个环境")
    scenarios = raw.get("scenarios") or []
    if not scenarios:
        raise ConfigError("至少要有一个场景")
    names = [item.get("name") for item in scenarios]
    if len(names) != len(set(names)):
        raise ConfigError("场景名不能重复")
    for item in scenarios:
        if not item.get("levels"):
            raise ConfigError(f"场景 {item.get('name')} 缺少 levels")
    return raw


def gate(report: Report, specs: dict[str, ScenarioSpec]) -> Report:
    for result in report.results:
        spec = specs[result.name]
        if not result.passed(spec):
            report.failures.append(f"{result.name}@{result.concurrency}: p95={result.p95_ms}ms 错误率={result.error_rate}")
    return report


def to_markdown(report: Report, env: str) -> str:
    lines = [f"# 性能测试报告（{env}）", "", f"- 场景数：{report.total}", f"- 通过：{report.passed}", f"- 失败：{len(report.failures)}", ""]
    lines.append("| 场景 | 并发 | TPS | P95(ms) | 错误率 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in report.results:
        lines.append(f"| {item.name} | {item.concurrency} | {item.tps} | {item.p95_ms} | {item.error_rate} |")
    if report.failures:
        lines += ["", "## 未达标", ""] + [f"- {item}" for item in report.failures]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None, runner: Callable[[ScenarioSpec], Result] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    config_path = "config.yaml"
    report_path = ""
    env = ""
    only = ""
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--config":
            config_path = argv[index + 1]
            index += 2
        elif token == "--report":
            report_path = argv[index + 1]
            index += 2
        elif token == "--env":
            env = argv[index + 1]
            index += 2
        elif token == "--only":
            only = argv[index + 1]
            index += 2
        else:
            print(f"未知参数：{token}", file=sys.stderr)
            return 2

    try:
        raw = load_config(config_path)
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    env = env or raw["default_env"]
    if env not in raw["envs"]:
        print(f"配置错误：环境 {env} 不存在", file=sys.stderr)
        return 2

    specs: dict[str, ScenarioSpec] = {}
    report = Report(env=env)
    for item in raw["scenarios"]:
        spec = ScenarioSpec(
            name=item["name"],
            levels=[int(level) for level in item["levels"]],
            duration_s=float(item.get("duration_s", 1.0)),
            p95_limit_ms=float(item.get("p95_limit_ms", 300)),
            error_limit=float(item.get("error_limit", 0.01)),
        )
        specs[spec.name] = spec
        if only and only not in spec.name:
            continue
        if runner is None:
            report.failures.append(f"{spec.name}: 没有可用的执行器")
            continue
        for level in spec.levels:
            report.results.append(runner(spec))

    gate(report, specs)
    markdown = to_markdown(report, env)
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
