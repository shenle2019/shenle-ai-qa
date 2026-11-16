"""第 7 章实战：一行命令跑通「生成 → 校验 → 落盘 → 复读」。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from testkit import DataGen, dump_csv, dump_json, is_email, is_money, is_phone, load_json


def main() -> int:
    out = Path(__file__).resolve().parent / "_out"
    gen = DataGen(seed=20261116)
    orders = gen.orders(5)

    bad = [o for o in orders if not (is_phone(o["phone"]) and is_email(o["email"]))]
    if bad:
        print("生成的数据不合格：", bad)
        return 1

    json_path = dump_json(out / "orders.json", orders)
    csv_path = dump_csv(out / "orders.csv", orders)
    reread = load_json(json_path)

    total = sum(o["amount"] for o in reread)
    print(f"生成 {len(orders)} 条订单")
    print(f"JSON: {json_path.relative_to(Path.cwd())}（{json_path.stat().st_size} B）")
    print(f"CSV : {csv_path.relative_to(Path.cwd())}（{csv_path.stat().st_size} B）")
    print(f"复读条数 {len(reread)}，合计金额 {total:.2f}")
    print("样例：", reread[0])

    assert len(reread) == len(orders)
    assert all(is_money(f"{o['amount']:.2f}") for o in reread)
    print("自检通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
