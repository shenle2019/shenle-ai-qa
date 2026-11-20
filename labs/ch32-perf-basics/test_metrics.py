"""第 32 章的单测：先把「算法对不对」钉住，后面才敢拿它下结论。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for extra in (ROOT, ROOT / "labs" / "_shared"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

import requests  # noqa: E402

from mini_api import reset, serve  # noqa: E402
from perf import LoadGen, Stats, little_law, percentile  # noqa: E402


def test_percentile_linear_interpolation() -> None:
    values = [10, 20, 30, 40, 50]
    assert percentile(values, 50) == 30
    assert percentile(values, 0) == 10
    assert percentile(values, 100) == 50
    # 25% 落在 10 与 20 之间，插值后是 20
    assert percentile(values, 25) == pytest.approx(20.0)


def test_percentile_single_and_empty() -> None:
    assert percentile([7.5], 99) == 7.5
    assert percentile([], 90) == 0.0


def test_percentile_rejects_bad_p() -> None:
    with pytest.raises(ValueError):
        percentile([1, 2], 101)


def test_average_hides_tail() -> None:
    # 95 个 10ms + 5 个 200ms：平均值只有 19.5ms，但每 20 个请求就有 1 个要等 0.2 秒
    stats = Stats()
    for _ in range(95):
        stats.add(200, 10)
    for _ in range(5):
        stats.add(200, 200)
    assert stats.avg_ms == pytest.approx(19.5)
    assert stats.percentile(50) == pytest.approx(10.0)
    assert stats.percentile(99) == pytest.approx(200.0)


def test_error_rate_counts_non_2xx() -> None:
    stats = Stats()
    stats.add(200, 10)
    stats.add(500, 12)
    stats.add(404, 11)
    assert stats.count == 3
    assert stats.ok_count == 1
    assert stats.error_rate == pytest.approx(2 / 3, rel=1e-3)


def test_tps_uses_window() -> None:
    stats = Stats(window_s=2.0)
    for _ in range(10):
        stats.add(200, 5)
    assert stats.tps == pytest.approx(5.0)


def test_summary_shape() -> None:
    stats = Stats(window_s=1.0)
    stats.add(200, 12.345)
    summary = stats.summary()
    assert set(summary) >= {"count", "ok", "error_rate", "avg_ms", "p50_ms", "p90_ms", "p99_ms", "tps"}
    assert summary["avg_ms"] == pytest.approx(12.35, abs=0.01)


def test_little_law() -> None:
    assert little_law(10, 0.1) == pytest.approx(100.0)
    with pytest.raises(ValueError):
        little_law(10, 0)


def test_loadgen_rejects_bad_concurrency() -> None:
    with pytest.raises(ValueError):
        LoadGen(concurrency=0)


def test_loadgen_runs_function_target() -> None:
    calls = {"n": 0}

    def target() -> tuple[int, float]:
        calls["n"] += 1
        return 200, 1.0

    stats = LoadGen(concurrency=3).run(target, duration_s=0.3)
    assert stats.count > 0
    assert stats.error_rate == 0
    assert stats.tps > 0


def test_real_slow_endpoint_has_tail() -> None:
    reset()
    with serve() as base:
        session = requests.Session()
        session.mount("http://", requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=16))
        gen = LoadGen(concurrency=6)
        stats = gen.run(gen.http_target(session, f"{base}/slow/db"), duration_s=2.0)

    assert stats.count >= 20, "样本太少，说明压测没跑起来"
    assert stats.error_rate == 0
    assert stats.percentile(50) >= 140, "慢端点本身要 150ms，P50 应该接近它"
    assert stats.percentile(99) >= stats.percentile(50)
