"""第 35 章：把「数字难看」翻译成「谁在拖后腿」。

输入是两类数据：
- 各档的客户端统计（并发、TPS、P95、错误率）
- 各档的服务端快照（in_flight、pool_wait、5xx 数）
输出是一个结构化的结论：瓶颈在哪一层、依据是什么、下一步查什么。
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Stage", "Snapshot", "diagnose", "attribute", "suggest"]


@dataclass
class Stage:
    concurrency: int
    tps: float
    p95_ms: float
    error_rate: float


@dataclass
class Snapshot:
    concurrency: int
    in_flight: int = 0
    pool_wait_ms: float = 0.0
    server_5xx: int = 0
    total: int = 0

    @property
    def error_ratio(self) -> float:
        return round(self.server_5xx / self.total, 4) if self.total else 0.0


def diagnose(stages: list[Stage], snapshots: list[Snapshot]) -> dict[str, object]:
    """逐档对比，找出 TPS 停止增长的那一档。"""
    if not stages:
        raise ValueError("至少要有一档数据")
    grow = []
    for previous, current in zip(stages, stages[1:]):
        gain = (current.tps - previous.tps) / previous.tps if previous.tps else 0.0
        grow.append({"concurrency": current.concurrency, "gain": round(gain, 3)})
    plateau = next((item["concurrency"] for item in grow if item["gain"] < 0.1), None)
    return {
        "stages": [s.__dict__ for s in stages],
        "gain": grow,
        "plateau_at": plateau,
        "peak_tps": max(s.tps for s in stages),
        "worst_p95": max(s.p95_ms for s in stages),
        "max_error_rate": max(s.error_rate for s in stages),
        "snapshots": [s.__dict__ | {"error_ratio": s.error_ratio} for s in snapshots],
    }


def attribute(report: dict[str, object]) -> str:
    """按证据链给瓶颈归因：服务端拒绝 > 连接池排队 > 服务端处理慢 > 施压端受限。"""
    snaps: list[dict] = report["snapshots"]  # type: ignore[assignment]
    stage_map = {s["concurrency"]: s for s in report["stages"]}  # type: ignore[index]
    for snap in snaps:
        if snap["error_ratio"] > 0.01:
            return "server_error"
        if snap["pool_wait_ms"] > 0 and snap["in_flight"] >= snap["concurrency"]:
            return "pool_queue"
    peak = report["peak_tps"]
    plateau = report["plateau_at"]
    if plateau is not None:
        stage = stage_map[plateau]
        if stage["error_rate"] > 0.01:
            return "server_reject"
        return "server_slow"
    return "client_limited" if peak > 0 else "unknown"


def suggest(bottleneck: str) -> list[str]:
    table = {
        "server_error": ["先看 5xx 的具体错误码与日志", "确认是否触发了限流/熔断", "对比错误出现档位与资源曲线"],
        "server_reject": ["看限流阈值与连接池上限", "确认错误是 429/503 还是超时", "把并发退回上一档复测"],
        "pool_queue": ["看连接池上限与持有时长", "确认是否有慢 SQL 占着连接", "加连接前先查是否泄漏"],
        "server_slow": ["看 CPU/GC/锁等待", "抓该档的慢请求样本", "对比上一档的 RT 分布变化"],
        "client_limited": ["确认施压机 CPU 是否打满", "减少断言与日志开销", "把施压端与被测端分开"],
        "unknown": ["数据不足，补一档更高并发"],
    }
    return table.get(bottleneck, table["unknown"])
