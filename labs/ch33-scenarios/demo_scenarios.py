"""第 33 章演示：阶梯加压找拐点（基准 / 负载 / 压力三段）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests

from _shared.mini_api import serve
from _shared.perf import LoadGen  # noqa: F401  (给读者看依赖)
from scenario import Scenario, classify, find_knee, run_stages


def main() -> None:
    with serve() as base:
        session = requests.Session()

        def factory(level: int):
            def target():
                started = __import__("time").perf_counter()
                try:
                    response = session.get(f"{base}/slow/pool", timeout=5)
                    code = response.status_code
                except requests.RequestException:
                    code = 0
                return code, (__import__("time").perf_counter() - started) * 1000

            return target

        scenario = Scenario(name="连接池按压", levels=[2, 4, 6, 8, 12], duration_s=1.5)
        run_stages(
            scenario,
            factory,
            on_stage=lambda r: print(
                f"并发 {r.concurrency:>2}  TPS {r.tps:>7.2f}  P95 {r.p95_ms:>7.2f}ms  错误率 {r.error_rate:.2%}"
            ),
        )

        knee = find_knee(scenario.results)
        print()
        print("拐点判定：", knee)
        print("结论：", classify(scenario.results))


if __name__ == "__main__":
    main()
