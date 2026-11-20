"""第 34 章演示：步骤拆分 + 数据参数化 + 思考时间，对着 mini_api 真压。"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[0]))
sys.path.insert(0, str(HERE))

import requests

from _shared.mini_api import serve
from script_runner import DataSet, Step, load_rows, load_script, run_script


def main() -> None:
    script = load_script(HERE / "script.yaml")
    rows = load_rows(HERE / "users.csv")
    dataset = DataSet(rows)

    with serve() as base:
        session = requests.Session()
        token = session.post(base + "/api/login", json={"username": "alice", "password": "secret"}, timeout=5).json().get("token", "")
        auth = {"Authorization": f"Bearer {token}"}

        def call(method: str, path: str, json=None, headers=None):
            def _do(payload: dict) -> tuple[int, float]:
                started = time.perf_counter()
                try:
                    response = session.request(
                        method,
                        base + path,
                        json=json(payload) if callable(json) else json,
                        headers=(headers(payload) if callable(headers) else headers) or auth,
                        timeout=5,
                    )
                    status = response.status_code
                except requests.RequestException:
                    status = 0
                return status, (time.perf_counter() - started) * 1000

            return _do

        script.steps[0].call = call("POST", "/api/login", json=lambda row: {"username": row["user"], "password": row["password"]})
        script.steps[0].expect = lambda status: status in (200, 401)
        script.steps[1].call = call("GET", "/api/health")
        script.steps[2].call = call("POST", "/api/orders", json=lambda row: {"items": [{"sku": row["sku"], "qty": 1}]})

        stats = run_script(script, dataset)

    print(f"脚本：{script.name}（{script.users} 用户 × {script.loops} 轮）")
    for bucket in stats.values():
        row = bucket.summary()
        print(f"  {row['step']:<6} 次数 {row['count']:>3}  平均 {row['avg_ms']:>6.2f}ms  最大 {row['max_ms']:>6.2f}ms  失败 {row['errors']}")


if __name__ == "__main__":
    main()
