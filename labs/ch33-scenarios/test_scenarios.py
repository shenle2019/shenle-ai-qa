"""第 33 章测试：分段加压的执行器与拐点判定（离线，用假 target）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for extra in (ROOT, ROOT / "labs" / "_shared", Path(__file__).resolve().parent):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from scenario import Scenario, StageResult, classify, find_knee, run_stages  # noqa: E402
from _shared.perf import Stats  # noqa: E402


def _stats(count: int, ok: int, elapsed: float, rt: float) -> Stats:
    stats = Stats()
    for i in range(count):
        stats.add(200 if i < ok else 503, rt)
    stats.window_s = elapsed
    return stats


def _stage(level: int, count: int, ok: int, elapsed: float, rt: float) -> StageResult:
    return StageResult(concurrency=level, stats=_stats(count, ok, elapsed, rt))


def test_stage_result_derives_fields() -> None:
    stage = _stage(4, 100, 100, 2.0, 100.0)
    assert stage.tps == 50.0
    assert stage.p95_ms == 100.0
    assert stage.error_rate == 0.0


def test_error_rate_counts_5xx_and_zero() -> None:
    stage = _stage(4, 10, 7, 1.0, 10.0)
    assert stage.error_rate == pytest.approx(0.3)


def test_run_stages_calls_each_level_once() -> None:
    seen: list[int] = []

    def factory(level: int):
        seen.append(level)

        def target():
            return 200, 12.0

        return target

    scenario = Scenario(name="smoke", levels=[1, 2], duration_s=0.2)
    run_stages(scenario, factory)
    assert seen == [1, 2]
    assert [r.concurrency for r in scenario.results] == [1, 2]


def test_run_stages_fires_callback() -> None:
    collected: list[int] = []
    scenario = Scenario(name="cb", levels=[1], duration_s=0.2)
    run_stages(scenario, lambda level: (lambda: (200, 5.0)), on_stage=lambda r: collected.append(r.concurrency))
    assert collected == [1]


def test_find_knee_detects_latency_jump() -> None:
    results = [_stage(2, 100, 100, 1.0, 50.0), _stage(4, 100, 100, 1.0, 60.0), _stage(8, 100, 100, 1.0, 200.0)]
    knee = find_knee(results)
    assert knee["reason"] == "latency"
    assert knee["concurrency"] == 8
    assert knee["value"] == pytest.approx(3.33, abs=0.05)


def test_find_knee_detects_error_rate_first() -> None:
    results = [_stage(2, 100, 100, 1.0, 40.0), _stage(4, 100, 80, 1.0, 60.0)]
    knee = find_knee(results)
    assert knee["reason"] == "error_rate"
    assert knee["concurrency"] == 4


def test_find_knee_reports_none_when_healthy() -> None:
    results = [_stage(2, 100, 100, 1.0, 40.0), _stage(4, 100, 100, 1.0, 45.0)]
    knee = find_knee(results)
    assert knee["reason"] == "none"
    assert knee["value"] == pytest.approx(100.0)


def test_find_knee_handles_empty() -> None:
    assert find_knee([]) == {"concurrency": 0, "reason": "empty", "value": 0}


def test_classify_wording() -> None:
    healthy = [_stage(2, 100, 100, 1.0, 40.0)]
    assert "未到拐点" in classify(healthy)

    latency = [_stage(2, 100, 100, 1.0, 40.0), _stage(8, 100, 100, 1.0, 200.0)]
    assert "P95 翻" in classify(latency)

    errors = [_stage(2, 100, 90, 1.0, 40.0)]
    assert "错误率超阈值" in classify(errors)


def test_scenario_summary_shape() -> None:
    scenario = Scenario(name="sum", levels=[1], duration_s=0.2)
    run_stages(scenario, lambda level: (lambda: (200, 8.0)))
    payload = scenario.summary()
    assert payload["name"] == "sum"
    assert payload["stages"][0]["concurrency"] == 1
