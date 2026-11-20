"""第 35 章测试：平台期识别、瓶颈归因、建议生成（纯离线）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from analyze import Snapshot, Stage, attribute, diagnose, suggest  # noqa: E402


def _stages() -> list[Stage]:
    return [
        Stage(concurrency=2, tps=10.0, p95_ms=50.0, error_rate=0.0),
        Stage(concurrency=4, tps=19.0, p95_ms=55.0, error_rate=0.0),
        Stage(concurrency=8, tps=19.5, p95_ms=120.0, error_rate=0.0),
    ]


def test_diagnose_finds_plateau() -> None:
    report = diagnose(_stages(), [])
    assert report["plateau_at"] == 8
    assert report["peak_tps"] == 19.5


def test_diagnose_reports_growth() -> None:
    report = diagnose(_stages(), [])
    assert report["gain"][0]["gain"] == pytest.approx(0.9)
    assert report["gain"][1]["gain"] == pytest.approx(0.026, abs=0.01)


def test_diagnose_rejects_empty() -> None:
    with pytest.raises(ValueError):
        diagnose([], [])


def test_attribute_server_error_first() -> None:
    report = diagnose(_stages(), [Snapshot(concurrency=8, server_5xx=20, total=100)])
    assert attribute(report) == "server_error"


def test_attribute_pool_queue() -> None:
    report = diagnose(_stages(), [Snapshot(concurrency=8, in_flight=8, pool_wait_ms=120)])
    assert attribute(report) == "pool_queue"


def test_attribute_server_slow_when_plateau_without_errors() -> None:
    report = diagnose(_stages(), [Snapshot(concurrency=8, in_flight=3, total=100)])
    assert attribute(report) == "server_slow"


def test_attribute_client_limited_when_still_growing() -> None:
    stages = [Stage(1, 5.0, 10.0, 0.0), Stage(2, 10.0, 10.0, 0.0)]
    report = diagnose(stages, [])
    assert attribute(report) == "client_limited"


def test_suggest_always_returns_steps() -> None:
    for name in ["server_error", "pool_queue", "server_slow", "client_limited", "unknown"]:
        steps = suggest(name)
        assert steps and all(isinstance(item, str) for item in steps)
