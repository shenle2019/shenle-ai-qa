"""第 36 章：中间件层的三个常见瓶颈，用可算的模型说明白。

- 访问日志：把 nginx/网关日志算成 TPS、P95、5xx 占比、上游耗时
- 连接池：并发超过池上限后，排队时间随并发线性增长
- 消息队列：生产快于消费时，积压按「(速率差 × 时间)」累积
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = ["AccessLog", "parse_line", "summarise", "pool_wait", "backlog_after"]

LINE = re.compile(
    r'(?P<ip>\S+) .*?"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" (?P<status>\d{3}) (?P<size>\d+)[^ ]* '
    r"(?P<rt>[0-9.]+) (?P<upstream>[0-9.-]+)"
)


@dataclass
class AccessLog:
    path: str
    status: int
    rt_ms: float
    upstream_ms: float
    method: str = "GET"


def parse_line(line: str) -> AccessLog | None:
    match = LINE.search(line)
    if not match:
        return None
    return AccessLog(
        path=match.group("path"),
        status=int(match.group("status")),
        rt_ms=float(match.group("rt")) * 1000,
        upstream_ms=max(float(match.group("upstream")), 0.0) * 1000,
        method=match.group("method"),
    )


def summarise(logs: list[AccessLog], window_s: float = 1.0) -> dict:
    if not logs:
        return {"count": 0, "tps": 0.0, "p95_ms": 0.0, "error_rate": 0.0, "upstream_share": 0.0}
    rts = sorted(log.rt_ms for log in logs)
    index = max(int(len(rts) * 0.95) - 1, 0)
    errors = [log for log in logs if log.status >= 500]
    upstream = sum(log.upstream_ms for log in logs)
    total = sum(log.rt_ms for log in logs) or 1.0
    return {
        "count": len(logs),
        "tps": round(len(logs) / window_s, 2),
        "p95_ms": round(rts[index], 2),
        "error_rate": round(len(errors) / len(logs), 4),
        "upstream_share": round(upstream / total, 3),
    }


def pool_wait(concurrency: int, pool_size: int, hold_ms: float) -> float:
    """池满后，多出来的并发按「多出的倍数 × 持有时长」排队。"""
    if concurrency <= pool_size or pool_size <= 0:
        return 0.0
    return round((concurrency / pool_size - 1) * hold_ms, 2)


def backlog_after(produce_per_s: float, consume_per_s: float, seconds: float) -> int:
    """生产快于消费时，积压 = 速率差 × 时间；消费更快则积压归零。"""
    gap = produce_per_s - consume_per_s
    return int(max(gap, 0) * seconds)
