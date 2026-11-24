"""第 39 章测试：配置校验、门槛判定、报告渲染、CLI 退出码（离线）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from perf_platform import ConfigError, Report, Result, ScenarioSpec, gate, load_config, main, to_markdown  # noqa: E402


def _spec(name: str = "健康检查", p95: float = 200.0, err: float = 0.01) -> ScenarioSpec:
    return ScenarioSpec(name=name, levels=[2], p95_limit_ms=p95, error_limit=err)


def test_load_config_ok() -> None:
    raw = load_config(HERE / "config.yaml")
    assert raw["default_env"] == "local"
    assert len(raw["scenarios"]) == 2


def test_load_config_rejects_duplicate_names(tmp_path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("default_env: local\nenvs: {local: {}}\nscenarios:\n  - {name: a, levels: [1]}\n  - {name: a, levels: [2]}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="不能重复"):
        load_config(path)


def test_load_config_requires_scenarios(tmp_path) -> None:
    path = tmp_path / "empty.yaml"
    path.write_text("default_env: local\nenvs: {local: {}}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="至少要有一个场景"):
        load_config(path)


def test_result_passed_by_thresholds() -> None:
    assert Result("健康检查", 2, 10, 100, 0.0).passed(_spec())
    assert not Result("健康检查", 2, 10, 500, 0.0).passed(_spec())
    assert not Result("健康检查", 2, 10, 100, 0.5).passed(_spec())


def test_gate_collects_failures() -> None:
    report = Report(env="local", results=[Result("健康检查", 2, 10, 500, 0.0)])
    gate(report, {"健康检查": _spec()})
    assert len(report.failures) == 1
    assert "p95=500" in report.failures[0]
    assert not report.ok


def test_to_markdown_contains_table_and_failures() -> None:
    report = Report(env="local", results=[Result("健康检查", 2, 10, 500, 0.0)])
    gate(report, {"健康检查": _spec()})
    text = to_markdown(report, "local")
    assert "| 健康检查 | 2 | 10 | 500 | 0.0 |" in text
    assert "## 未达标" in text


def test_main_returns_zero_when_all_pass(tmp_path) -> None:
    config = tmp_path / "cfg.yaml"
    config.write_text("default_env: local\nenvs: {local: {}}\nscenarios:\n  - {name: 快, levels: [1], p95_limit_ms: 100}\n", encoding="utf-8")
    out = tmp_path / "report.md"
    code = main(["--config", str(config), "--report", str(out)], runner=lambda spec: Result(spec.name, 1, 10, 20, 0.0))
    assert code == 0
    assert out.exists()


def test_main_returns_one_when_gate_fails(tmp_path) -> None:
    config = tmp_path / "cfg.yaml"
    config.write_text("default_env: local\nenvs: {local: {}}\nscenarios:\n  - {name: 慢, levels: [1], p95_limit_ms: 100}\n", encoding="utf-8")
    code = main(["--config", str(config)], runner=lambda spec: Result(spec.name, 1, 10, 900, 0.0))
    assert code == 1


def test_main_rejects_unknown_env(tmp_path) -> None:
    config = tmp_path / "cfg.yaml"
    config.write_text("default_env: local\nenvs: {local: {}}\nscenarios:\n  - {name: a, levels: [1]}\n", encoding="utf-8")
    assert main(["--config", str(config), "--env", "prod"]) == 2

def test_passed_never_goes_negative() -> None:
    report = Report(env="local")
    report.failures.extend(["a: 没有可用的执行器", "b: 没有可用的执行器", "c: 没有可用的执行器"])
    assert report.total == 0
    assert report.passed == 0


def test_load_config_missing_file_raises_config_error(tmp_path) -> None:
    with pytest.raises(ConfigError, match="读不到配置文件"):
        load_config(tmp_path / "nope.yaml")
