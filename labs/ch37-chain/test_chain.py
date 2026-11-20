"""第 37 章测试：流量打标、前缀隔离、计划校验（离线）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from chain import Plan, Traffic, check_isolation, is_shadow, isolated, make_prefix  # noqa: E402


def test_traffic_tag_carries_prefix_and_flag() -> None:
    tags = Traffic(shadow=True, prefix="qa_1_").tag()
    assert tags["X-Shadow"] == "1"
    assert tags["X-Data-Prefix"] == "qa_1_"


def test_traffic_trace_is_unique() -> None:
    assert Traffic().trace != Traffic().trace


def test_is_shadow_matches_any_header() -> None:
    assert is_shadow({"X-Shadow": "1"})
    assert is_shadow({"x-pressure-test": "1"})
    assert not is_shadow({"X-Shadow": "0"})


def test_make_prefix_requires_run_id() -> None:
    assert make_prefix(" 2025_11 ") == "qa_2025_11_"
    with pytest.raises(ValueError):
        make_prefix("   ")


def test_isolated_checks_prefix() -> None:
    prefix = make_prefix("r1")
    assert isolated("qa_r1_user_01", prefix)
    assert not isolated("alice", prefix)


def test_check_isolation_reports_leaks() -> None:
    prefix = make_prefix("r1")
    report = check_isolation(["qa_r1_a", "qa_r1_b", "alice"], prefix)
    assert report == {"total": 3, "isolated": 2, "leaked": ["alice"]}


def test_plan_validate_catches_missing_run_id_and_writes() -> None:
    plan = Plan(name="p", steps=[("查询", "read")], run_id="")
    problems = plan.validate()
    assert "缺少 run_id" in problems
    assert any("写步骤" in item for item in problems)


def test_plan_validate_ok() -> None:
    plan = Plan(name="p", steps=[("下单", "write")], run_id="20251120")
    assert plan.validate() == []
    assert plan.writes() == ["下单"]
