r"""第 23 章：把前面几章拼成一个能交给别人的框架。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch23-framework -q
    .\.venv\Scripts\python.exe labs/ch23-framework/run.py --base-url <站点>
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import yaml

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))

import fw_report as report_mod  # noqa: E402
from fw_runner import ConfigError, Result, Report, load_config, pick_env, run  # noqa: E402


def test_config_loads_and_validates():
    config = load_config(LAB / "config.yaml")
    assert config["default_env"] == "local"
    assert {case["id"] for case in config["cases"]} >= {"login-ok", "guard-anonymous"}


def test_config_rejects_bad_default_env(tmp_path):
    bad = yaml.safe_load((LAB / "config.yaml").read_text(encoding="utf-8"))
    bad["default_env"] = "nope"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ConfigError) as err:
        load_config(path)
    assert "default_env" in str(err.value)


def test_config_rejects_duplicate_ids(tmp_path):
    bad = yaml.safe_load((LAB / "config.yaml").read_text(encoding="utf-8"))
    bad["cases"].append(dict(bad["cases"][0]))
    path = tmp_path / "dup.yaml"
    path.write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ConfigError) as err:
        load_config(path)
    assert "重复" in str(err.value)


def test_pick_env_returns_config():
    config = load_config(LAB / "config.yaml")
    name, env = pick_env(config, "staging")
    assert name == "staging"
    assert env["base_url"].startswith("https://")


def test_only_filters_cases():
    config = load_config(LAB / "config.yaml")
    assert len([case for case in config["cases"] if "login" in case["id"]]) == 2


def test_full_run_passes_and_reports(page, site):
    config = load_config(LAB / "config.yaml")
    result = run(page, config, env="local", base_url=site)
    assert result.total == len(config["cases"])
    assert result.failed == 0, [item for item in result.results if not item.ok]
    assert result.ok


def test_failure_is_captured_and_does_not_stop_the_run(page, site):
    config = load_config(LAB / "config.yaml")
    broken = dict(config)
    broken["cases"] = [dict(case) for case in config["cases"]]
    broken["cases"][0] = dict(broken["cases"][0])
    broken["cases"][0]["expect"] = {"path": "/todos", "user": "nobody"}
    result = run(page, broken, env="local", base_url=site)
    assert result.total == len(broken["cases"])
    assert result.failed == 1
    assert result.results[0].ok is False
    assert result.ok is False


def test_markdown_and_junit_report(tmp_path):
    result = Report(
        env="local",
        base_url="http://127.0.0.1:1",
        results=[Result("login-ok", "登录", True, "通过", 12), Result("x", "坏的", False, "AssertionError: 不对", 30)],
    )
    md = report_mod.write(result, tmp_path / "r.md").read_text(encoding="utf-8")
    assert "| login-ok | 登录 | 通过 |" in md
    assert "失败 1" in md

    xml_path = report_mod.write(result, tmp_path / "r.xml")
    root = ET.fromstring(xml_path.read_text(encoding="utf-8"))
    assert root.attrib["tests"] == "2"
    assert root.attrib["failures"] == "1"
    assert root.find("testcase/failure") is not None


def test_cli_exit_codes(capsys):
    import run as cli

    code = cli.main(["--env", "nope"])
    assert code == 2
    assert "配置错误" in capsys.readouterr().err


def test_cli_happy_path(site):
    import os
    import subprocess

    ROOT = LAB.parents[1]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, str(LAB / "run.py"), "--base-url", site, "--only", "login-ok", "--report", str(LAB / "reports" / "ch23.md")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        cwd=str(ROOT),
        env=env,
    )
    assert result.returncode == 0, (result.stderr or "")[-800:]
    assert "合计 1 条" in result.stdout
    assert "报告已写入" in result.stdout
