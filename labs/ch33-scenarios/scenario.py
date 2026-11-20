"""第 33 章：四类场景怎么压、拐点怎么找。

核心是一个「分段加压」执行器：每一档并发跑固定时长，收集该档的统计，
然后按规则判定拐点（RT 突然翻倍 / 错误率越过阈值 / TPS 不再增长）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from _shared.perf import LoadGen, Stats

__all__ = ["Scenario", "StageResult", "run_stages", "find_knee", "classify"]


@dataclass
class StageResult:
    concurrency: int
    stats: Stats
    tps: float = 0.0
    p95_ms: float = 0.0
    error_rate: float = 0.0
    note: str = ""

    def __post_init__(self) -> None:
        self.tps = round(self.stats.tps, 2)
        self.p95_ms = round(self.stats.percentile(95), 2)
        self.error_rate = round(self.stats.error_rate, 4)


@dataclass
class Scenario:
    """一次场景 = 若干档并发，每档跑固定时长。"""

    name: str
    levels: list[int]
    duration_s: float = 2.0
    warmup_s: float = 0.5
    results: list[StageResult] = field(default_factory=list)

    def summary(self) -> dict[str, object]:
        return {
            "name": self.name,
            "levels": self.levels,
            "duration_s": self.duration_s,
            "stages": [
                {
                    "concurrency": r.concurrency,
                    "tps": r.tps,
                    "p95_ms": r.p95_ms,
                    "error_rate": r.error_rate,
                    "note": r.note,
                }
                for r in self.results
            ],
        }


def run_stages(
    scenario: Scenario,
    target_factory: Callable[[int], Callable[[], tuple[int, float]]],
    on_stage: Callable[[StageResult], None] | None = None,
) -> Scenario:
    """按档位依次加压。每档新建一个 target，避免上一档的连接被复用。"""
    scenario.results.clear()
    for level in scenario.levels:
        target = target_factory(level)
        stats = LoadGen(concurrency=level).run(target, duration_s=scenario.duration_s)
        result = StageResult(concurrency=level, stats=stats)
        scenario.results.append(result)
        if on_stage:
            on_stage(result)
    return scenario


def find_knee(results: list[StageResult], rt_ratio: float = 1.5, error_rate: float = 0.01) -> dict[str, object]:
    """找拐点：RT 相对上一档涨超 rt_ratio 倍，或错误率越过阈值。

    返回第一个越界的档位与原因；都没越界就报告「未见拐点」并给出最后一档数据。
    """
    previous: StageResult | None = None
    for current in results:
        if current.error_rate > error_rate:
            return {"concurrency": current.concurrency, "reason": "error_rate", "value": current.error_rate}
        if previous and previous.p95_ms > 0 and current.p95_ms / previous.p95_ms >= rt_ratio:
            return {
                "concurrency": current.concurrency,
                "reason": "latency",
                "value": round(current.p95_ms / previous.p95_ms, 2),
            }
        previous = current
    if not results:
        return {"concurrency": 0, "reason": "empty", "value": 0}
    last = results[-1]
    return {"concurrency": last.concurrency, "reason": "none", "value": last.tps}


def classify(results: list[StageResult]) -> str:
    """给场景一个结论：是「没压到」还是「压到了」。"""
    knee = find_knee(results)
    if knee["reason"] == "none":
        return "未到拐点：当前最高并发仍能维持，可继续加压"
    if knee["reason"] == "error_rate":
        return f"在并发 {knee['concurrency']} 时错误率超阈值（{knee['value']}），先查错误类型"
    return f"在并发 {knee['concurrency']} 时 P95 翻 {knee['value']} 倍，容量上限大约在这一档之前"
