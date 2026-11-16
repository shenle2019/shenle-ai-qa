"""第 11 章实验：封装之后的调用长这样。

跑法：``.venv\\Scripts\\python.exe labs\\ch11-httpclient\\demo.py``
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api import OrderApi, UserApi  # noqa: E402
from http_client import HttpClient  # noqa: E402
from mini_api import serve  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


def main() -> None:
    with serve() as base:
        client = HttpClient(base, timeout=5, retries=2)
        users = UserApi(client)
        token = users.login()
        users.with_token(token)

        print("列表:", users.list(page=1, size=2)["total"], "条")
        created = users.create("zoe", role="tester")
        print("创建:", created["id"], created["name"])
        print("详情:", users.get(created["id"])["name"])
        users.delete(created["id"])

        orders = OrderApi(client)
        order = orders.create([{"sku": "A-1", "qty": 2}], idempotency_key="demo-1")
        print("下单:", order["id"], order["amount"])
        print("支付:", orders.pay(order["id"])["status"])

        print("\n调用记录（方法, 路径, 状态码）:")
        for call in client.calls:
            print("  ", call)


if __name__ == "__main__":
    main()
