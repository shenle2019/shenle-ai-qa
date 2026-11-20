"""第 38 章测试：z-score 异常、日志模板聚类、提示词与假模型（离线）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ai_analyze import FakeClient, build_prompt, cluster_logs, detect_anomalies, explain, normalise  # noqa: E402


def test_detect_spike() -> None:
    series = [100, 102, 99, 101, 100, 103, 100, 400]
    hits = detect_anomalies(series, window=5, threshold=3.0)
    assert hits and hits[-1].index == 7 and hits[-1].kind == "spike"


def test_detect_drop() -> None:
    series = [100, 101, 99, 100, 102, 100, 5]
    hits = detect_anomalies(series, window=5, threshold=3.0)
    assert hits and hits[-1].kind == "drop"


def test_detect_flat_series_has_no_anomaly() -> None:
    assert detect_anomalies([50.0] * 12) == []


def test_normalise_collapses_ids_and_numbers() -> None:
    line = "user 12345 order 9f8e7d6c-1111-2222-3333-444455556666 took 250ms"
    assert normalise(line) == "user <n> order <uuid> took <n>ms"


def test_cluster_groups_similar_lines() -> None:
    lines = [
        "GET /api/orders 200 12ms",
        "GET /api/orders 200 15ms",
        "GET /api/users 500 3ms",
    ]
    clusters = cluster_logs(lines, top=2)
    assert clusters[0]["count"] == 2
    assert "orders" in clusters[0]["template"]


def test_build_prompt_contains_numbers() -> None:
    prompt = build_prompt({"plateau_at": 8, "peak_tps": 19.5, "worst_p95": 120, "max_error_rate": 0.02})
    assert "平台期并发：8" in prompt
    assert "峰值 TPS：19.5" in prompt
    assert "不超过 120 字" in prompt


def test_explain_uses_fake_client() -> None:
    client = FakeClient(reply="结论：ok")
    assert explain({"plateau_at": 1}, client) == "结论：ok"
    assert len(client.calls) == 1


def test_explain_accepts_callable() -> None:
    assert explain({"plateau_at": 2}, lambda prompt: "结论：callable") == "结论：callable"
