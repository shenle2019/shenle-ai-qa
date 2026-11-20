"""性能测试的公共件：统计口径 + 一个够用的施压器。

两个类：

- :class:`Stats` —— 把每次请求的耗时与状态码收进来，算 P50/P90/P99、TPS、错误率；
- :class:`LoadGen` —— 固定并发、固定时长的压测客户端，用 ``requests.Session`` 复用连接。

设计取舍：不追求极限 QPS，追求「数字可解释」。同一份样本能被反复算出同样的分位值，
才谈得上拿它做结论。
"""

from __future__ import annotations

import statistics
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

import requests

__all__ = ["Stats", "Sample", "LoadGen", "percentile", "little_law"]


def percentile(values: list[float], p: float) -> float:
    """线性插值分位值，p 取 0~100。空列表返回 0。"""
    if not values:
        return 0.0
    if not 0 <= p <= 100:
        raise ValueError("p 必须在 0~100 之间")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p / 100
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def little_law(concurrency: float, avg_rt_s: float) -> float:
    """排队论里最常用的一条：TPS = 并发 / 平均响应时间（秒）。"""
    if avg_rt_s <= 0:
        raise ValueError("平均响应时间必须大于 0")
    return concurrency / avg_rt_s


@dataclass
class Sample:
    status: int
    elapsed_ms: float
    ok: bool


@dataclass
class Stats:
    samples: list[Sample] = field(default_factory=list)
    window_s: float = 0.0

    def add(self, status: int, elapsed_ms: float, ok: bool | None = None) -> None:
        if ok is None:
            ok = 200 <= status < 400
        self.samples.append(Sample(status=status, elapsed_ms=elapsed_ms, ok=ok))

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def ok_count(self) -> int:
        return sum(1 for s in self.samples if s.ok)

    @property
    def error_rate(self) -> float:
        if not self.samples:
            return 0.0
        return 1 - self.ok_count / len(self.samples)

    @property
    def elapsed(self) -> list[float]:
        return [s.elapsed_ms for s in self.samples]

    @property
    def avg_ms(self) -> float:
        return statistics.fmean(self.elapsed) if self.samples else 0.0

    @property
    def tps(self) -> float:
        """按实际采样窗口算吞吐，窗口为 0 时退回样本数。"""
        span = self.window_s or (self.count / 1000 or 1)
        return self.count / span if span > 0 else 0.0

    def percentile(self, p: float) -> float:
        return percentile(self.elapsed, p)

    def summary(self) -> dict[str, float]:
        return {
            "count": self.count,
            "ok": self.ok_count,
            "error_rate": round(self.error_rate, 4),
            "avg_ms": round(self.avg_ms, 2),
            "p50_ms": round(self.percentile(50), 2),
            "p90_ms": round(self.percentile(90), 2),
            "p99_ms": round(self.percentile(99), 2),
            "max_ms": round(max(self.elapsed), 2) if self.samples else 0.0,
            "tps": round(self.tps, 2),
            "window_s": round(self.window_s, 2),
        }


class LoadGen:
    """固定并发 + 固定时长。

    ``target`` 是「一次完整请求」的回调，返回 ``(status, elapsed_ms)``；
    这样既能压 HTTP，也能压任意本地函数。
    """

    def __init__(self, concurrency: int = 10) -> None:
        if concurrency < 1:
            raise ValueError("concurrency 至少为 1")
        self.concurrency = concurrency

    def run(self, target: Callable[[], tuple[int, float]], duration_s: float = 3.0) -> Stats:
        stats = Stats()
        stop_at = time.perf_counter() + duration_s
        lock = threading.Lock()

        def worker() -> None:
            while time.perf_counter() < stop_at:
                status, ms = target()
                with lock:
                    stats.add(status, ms)

        threads = [threading.Thread(target=worker, daemon=True) for _ in range(self.concurrency)]
        started = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=duration_s + 30)
        stats.window_s = time.perf_counter() - started
        return stats

    def http_target(self, session: requests.Session, url: str, timeout: float = 5.0) -> Callable[[], tuple[int, float]]:
        """把一次 GET 包成 target，供 :meth:`run` 调用。"""

        def target() -> tuple[int, float]:
            begin = time.perf_counter()
            try:
                response = session.get(url, timeout=timeout)
                return response.status_code, (time.perf_counter() - begin) * 1000
            except requests.RequestException:
                return 0, (time.perf_counter() - begin) * 1000

        return target
