"""第 36 章测试：日志解析、指标汇总、池排队、队列积压（离线）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from middleware import AccessLog, backlog_after, parse_line, pool_wait, summarise  # noqa: E402

SAMPLE = (
    '10.0.0.1 - - [20/Nov/2025:10:00:00 +0800] "GET /api/orders HTTP/1.1" 200 512 0.012 0.010\n'
    '10.0.0.2 - - [20/Nov/2025:10:00:00 +0800] "GET /api/orders HTTP/1.1" 503 0 0.500 0.480\n'
)


def test_parse_line_fields() -> None:
    parsed = parse_line(SAMPLE.splitlines()[0])
    assert parsed is not None
    assert parsed.path == "/api/orders"
    assert parsed.status == 200
    assert parsed.rt_ms == pytest.approx(12.0)
    assert parsed.upstream_ms == pytest.approx(10.0)


def test_parse_line_rejects_garbage() -> None:
    assert parse_line("not a log line") is None


def test_summarise_counts_and_errors() -> None:
    logs = [log for log in (parse_line(line) for line in SAMPLE.splitlines()) if log]
    report = summarise(logs, window_s=1.0)
    assert report["count"] == 2
    assert report["tps"] == 2.0
    assert report["error_rate"] == 0.5


def test_summarise_p95() -> None:
    logs = [AccessLog(path="/x", status=200, rt_ms=float(i), upstream_ms=0.0) for i in range(1, 101)]
    assert summarise(logs)["p95_ms"] == pytest.approx(95.0)


def test_summarise_empty() -> None:
    assert summarise([])["count"] == 0


def test_pool_wait_zero_below_capacity() -> None:
    assert pool_wait(concurrency=4, pool_size=5, hold_ms=200) == 0.0


def test_pool_wait_grows_with_concurrency() -> None:
    assert pool_wait(concurrency=10, pool_size=5, hold_ms=200) == pytest.approx(200.0)
    assert pool_wait(concurrency=20, pool_size=5, hold_ms=200) == pytest.approx(600.0)


def test_backlog_accumulates_only_when_produce_wins() -> None:
    assert backlog_after(produce_per_s=100, consume_per_s=80, seconds=10) == 200
    assert backlog_after(produce_per_s=80, consume_per_s=100, seconds=10) == 0
