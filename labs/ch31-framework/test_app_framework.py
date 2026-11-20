"""第 31 章测试：配置校验、报告渲染、CLI 参数都在离线覆盖；真机跑一次完整入口。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "labs" / "ch28-data-driven"))
sys.path.insert(0, str(ROOT / "labs" / "ch26-page-object"))

from app_framework import ConfigError, Report, Result, load_config, main, run  # noqa: E402

CONFIG = HERE / "config.yaml"


def test_load_config_resolves_cases_path() -> None:
    config = load_config(CONFIG)
    assert config["package"] == "com.shenjiahang.logindemo"
    assert Path(config["cases"]).exists()
    assert config["device_timeout"] == 10


def test_load_config_rejects_missing_keys(tmp_path) -> None:
    bad = tmp_path / "c.yaml"
    bad.write_text("package: x\n", encoding="utf-8")
    with pytest.raises(ConfigError) as exc:
        load_config(bad)
    assert "activity" in str(exc.value)


def test_load_config_rejects_missing_cases_file(tmp_path) -> None:
    bad = tmp_path / "c.yaml"
    bad.write_text("package: p\nactivity: a\ncases: nope.yaml\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(bad)


def test_report_markdown_renders_rows() -> None:
    report = Report(
        results=[Result("a", "登录成功", True, "", 1.2), Result("b", "错误密码", False, "期望 x 实际 y", 0.8)],
        started_at="2026-11-19 12:00:00",
        device="FA7B11A03073",
    )
    text = report.to_markdown()
    assert report.total == 2 and report.passed == 1 and report.failed == 1
    assert "| a | 登录成功 | 通过 | 1.2s |" in text
    assert "期望 x 实际 y" in text
    assert "FA7B11A03073" in text


def test_report_escapes_pipe_in_detail() -> None:
    report = Report(results=[Result("a", "t", False, "x | y")])
    assert "x / y" in report.to_markdown()


def test_cli_returns_2_without_device(monkeypatch) -> None:
    import labs._shared.adb as adb_module

    def boom(*args, **kwargs):
        raise adb_module.AdbError("没有设备")

    monkeypatch.setattr(adb_module.Device, "first_online", staticmethod(boom))
    assert main(["--config", str(CONFIG)]) == 2


@pytest.mark.device
@pytest.fixture(scope="module")
def real_device():
    """CLI 类用例必须有真机才跑；没插手机就跳过，不影响离线单测。"""
    from labs._shared.adb import AdbError, Device

    try:
        return Device.first_online(timeout=1)
    except AdbError:
        pytest.skip("没有连接安卓设备")


@pytest.mark.device
def test_cli_runs_against_real_device(tmp_path, real_device) -> None:
    report_path = tmp_path / "report.md"
    code = main(["--config", str(CONFIG), "--report", str(report_path)])
    assert code == 0
    text = report_path.read_text(encoding="utf-8")
    assert "APP 自动化执行报告" in text
    assert "通过 4" in text


@pytest.mark.device
def test_cli_only_filter(tmp_path, real_device) -> None:
    """--only 只跑命中的用例，报告里就只有一条。"""
    report_path = tmp_path / "one.md"
    code = main(["--config", str(CONFIG), "--only", "login-correct", "--report", str(report_path)])
    assert code == 0
    text = report_path.read_text(encoding="utf-8")
    assert "共 1 条" in text
