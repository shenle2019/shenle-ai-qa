"""第 45 章测试：通过率、门槛、Markdown 与 JUnit 输出。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from platform_report import Outcome, Report  # noqa: E402


def build(*outcomes, thresholds=None):
    return Report(env="local", outcomes=list(outcomes), thresholds=thresholds or {"pass_rate": 0.95})


def test_totals_and_pass_rate():
    report = build(Outcome("a", True, 10), Outcome("b", False, 20, "boom"))
    assert (report.total, report.passed, report.pass_rate) == (2, 1, 0.5)


def test_gate_fails_below_threshold():
    ok, reasons = build(Outcome("a", True, 10), Outcome("b", False, 10, "x")).gate()
    assert not ok
    assert "低于门槛" in reasons[0]


def test_gate_passes_when_enough():
    ok, reasons = build(Outcome("a", True, 10), Outcome("b", True, 12)).gate()
    assert ok and reasons == []


def test_gate_flags_slow_cases():
    ok, reasons = build(Outcome("slow", True, 900), thresholds={"pass_rate": 0.5, "max_duration_ms": 500}).gate()
    assert not ok
    assert "超时用例：slow" in reasons[0]


def test_slowest_top_three():
    report = build(*[Outcome(str(i), True, i * 10) for i in range(5)])
    assert [item.case_id for item in report.slowest] == ["4", "3", "2"]


def test_markdown_has_table_and_verdict():
    text = build(Outcome("a", True, 10), Outcome("b", False, 20, "boom")).to_markdown()
    assert "| b | failed | 20 | boom |" in text
    assert "未通过" in text


def test_junit_escapes_and_counts_failures():
    xml = build(Outcome("a<b", False, 10, "x&y")).to_junit()
    assert 'failures="1"' in xml
    assert "a&lt;b" in xml
    assert "x&amp;y" in xml


def test_empty_report_passes():
    report = build()
    assert report.pass_rate == 1.0
    assert report.gate()[0] is True
