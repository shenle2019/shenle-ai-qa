"""第 32 章：指标怎么算、怎么读。

跑两件事：

1. 用固定样本证明「平均值会骗人」——同样 100ms 平均，分位值差三倍；
2. 对本机慢端点做一次 10 并发、3 秒的小压测，把 TPS / 分位值 / 错误率打出来。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for extra in (ROOT, ROOT / "labs" / "_shared"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

import requests  # noqa: E402

from mini_api import serve  # noqa: E402
from perf import LoadGen, Stats, little_law, percentile  # noqa: E402


def demo_percentile() -> None:
    samples = [10, 10, 10, 10, 10, 10, 10, 10, 10, 200]
    print("样本(ms)：", samples)
    print(f"  平均 {sum(samples) / len(samples):.1f}  P50 {percentile(samples, 50):.1f}  P99 {percentile(samples, 99):.1f}")
    print("  结论：平均值 29ms 看起来还行，P99 却是 200ms——每 100 个用户就有 1 个要等 0.2 秒")


def demo_little_law() -> None:
    for concurrency in (5, 10, 20):
        print(f"  并发 {concurrency:>2}、平均 RT 100ms → 理论 TPS {little_law(concurrency, 0.1):.0f}")


def demo_load() -> None:
    with serve() as base:
        url = f"{base}/slow/db"
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=16)
        session.mount("http://", adapter)

        stats = LoadGen(concurrency=10).run(
            LoadGen(10).http_target(session, url), duration_s=3.0
        )
        summary = stats.summary()
        print("  压测结果：")
        for key, value in summary.items():
            print(f"    {key:<10} {value}")

        target = little_law(10, summary["avg_ms"] / 1000)
        print(f"  Little's Law 反推：并发 10 / 平均 {summary['avg_ms']}ms → 理论 TPS {target:.1f}，实测 {summary['tps']}")


def main() -> int:
    print("1) 平均值陷阱")
    demo_percentile()
    print("\n2) 并发、RT、TPS 三者换算")
    demo_little_law()
    print("\n3) 一次真实压测（本机慢端点 /slow/db）")
    demo_load()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
