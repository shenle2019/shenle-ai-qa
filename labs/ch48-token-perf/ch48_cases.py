"""第 48 章用例：AI 接口的性能不等于 QPS。

三件事要能算出来：
1. TTFT / TPOT / 总时长 的换算（用户在什么时候看到第一个字）
2. 并发超过服务能力后的排队（QPS 涨了但 P95 崩了）
3. 冷启动与长上下文对延迟的放大
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))

from eval_sim import p95, success_rate, tokens_cost  # noqa: E402
from llm_sim import FakeLLM  # noqa: E402


@dataclass
class LoadResult:
    latencies: list[float]
    ok: list[bool]

    @property
    def p95(self) -> float:
        return p95(self.latencies)

    @property
    def avg(self) -> float:
        return round(sum(self.latencies) / len(self.latencies), 2)

    @property
    def rate(self) -> float:
        return success_rate(self.ok)


def one_request(llm: FakeLLM, prompt: str, max_tokens: int = 20) -> dict:
    reply = llm.answer(prompt, max_tokens=max_tokens)
    return {
        "ttft": reply.ttft_ms,
        "tpot": reply.tpot_ms,
        "total": reply.total_ms,
        "tokens": reply.token_count,
    }


def simulate_load(
    n: int,
    capacity: int,
    ttft_ms: float = 120.0,
    tpot_ms: float = 18.0,
    tokens: int = 12,
    timeout_ms: float = 800.0,
) -> LoadResult:
    """把 n 个请求压到容量为 capacity 的服务上。

    排队模型：每批最多 capacity 个同时处理，后到的等前面的批次。
    单请求耗时 = ttft + tpot*(tokens-1)，超过 timeout 记失败。
    """
    service = ttft_ms + tpot_ms * (tokens - 1)
    latencies: list[float] = []
    ok: list[bool] = []
    batch_index = 0
    for i in range(n):
        batch_index = i // capacity
        wait = batch_index * service
        total = round(wait + service, 2)
        latencies.append(total)
        ok.append(total <= timeout_ms)
    return LoadResult(latencies, ok)


def degrade_curve(context_sizes: list[int], base_ttft: float = 100.0, per_1k: float = 25.0) -> list[tuple[int, float]]:
    """上下文越长，prefill 越久：TTFT 近似线性上涨（示例系数，不是厂商实测值）。"""
    return [(size, round(base_ttft + per_1k * size / 1000, 2)) for size in context_sizes]


def cold_start(first: float, warm: float) -> dict:
    return {"first": first, "warm": warm, "penalty": round(first - warm, 2)}


def demo() -> None:
    llm = FakeLLM(latency_ms=120, tpot_ms=18)
    r = one_request(llm, "把这段订单说明总结一下", max_tokens=12)
    print("== 单请求 ==", r)
    print("校验: total == ttft + tpot*(n-1) ->", round(r["ttft"] + r["tpot"] * (r["tokens"] - 1), 2))

    print("\n== 并发 8，容量 4 ==")
    load = simulate_load(n=8, capacity=4)
    print("latencies:", load.latencies)
    print("avg:", load.avg, "p95:", load.p95, "成功率:", load.rate)

    print("\n== 并发 16，容量 4（QPS 高但大量超时）==")
    heavy = simulate_load(n=16, capacity=4)
    print("p95:", heavy.p95, "成功率:", heavy.rate)

    print("\n== 上下文退化 ==")
    for size, ttft in degrade_curve([500, 4000, 32000, 128000]):
        print(f"{size:>7} tokens -> TTFT {ttft} ms")

    print("\n== 冷启动 ==", cold_start(950, 130))

    print("\n== 成本（示例价）==", tokens_cost(prompt_tokens=3200, completion_tokens=800), "元")


if __name__ == "__main__":
    demo()
