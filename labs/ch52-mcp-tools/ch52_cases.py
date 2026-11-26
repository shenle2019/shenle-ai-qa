"""第 52 章用例：MCP 工具层的十一类故障。

工具层最容易出事的不是「模型不聪明」，而是：
参数类型错、必填缺失、多传字段、选错工具、并行互相覆盖、
工具挂了没兜住、超时中断、越权调用、返回值被污染。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))

from mcp_sim import (  # noqa: E402
    PermissionError_,
    SchemaError,
    ToolError,
    ToolSpec,
    default_registry,
    to_json,
)


def demo() -> None:
    reg = default_registry()
    print("== 正常调用 ==")
    print(to_json(reg.call("get_order", {"order_id": "A1001"})))

    print("\n== 参数类型错 ==")
    print(reg.call("get_order", {"order_id": 1001}).error)

    print("\n== 必填缺失 ==")
    print(reg.call("get_order", {}).error)

    print("\n== 多传未声明参数 ==")
    print(reg.call("get_order", {"order_id": "A1001", "debug": True}).error)

    print("\n== 选错工具 ==")
    print("用户说「把订单导出来」→ 选中:", reg.choose("把 订单 导出来"))

    print("\n== 越权（read 令牌调 admin）==")
    print(reg.call("export_all_orders", {"dst": "/tmp/a.csv"}).error)

    print("\n== 越权（read 令牌调 write，以前是漏洞）==")
    print(reg.call("refund_order", {"order_id": "A1001", "amount": 100}).error)

    print("\n== 金额范围（bool 曾能混进 int）==")
    reg.allow_scope = "write"
    print(reg.call("refund_order", {"order_id": "A1001", "amount": True}).error)
    print(reg.call("refund_order", {"order_id": "A1001", "amount": -1}).error)
    print(reg.call("refund_order", {"order_id": "A1001", "amount": 100}).error)

    print("\n== 工具故障注入 ==")
    reg.fail_tools["get_order"] = "上游 502"
    print(reg.call("get_order", {"order_id": "A1001"}).error)

    print("\n== 串行 vs 并行 ==")
    reg2 = default_registry()
    serial = reg2.call_many([("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"})], mode="serial")
    print("串行结果:", [c.result for c in serial])
    parallel = reg2.call_many([("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"})], mode="parallel")
    print("并行结果:", [c.result for c in parallel])
    print("审计日志条数（清空就会变 2）:", len(reg2.calls))

    print("\n== 工具超时（以前 ToolTimeout 从未被 raise）==")
    from mcp_sim import ToolRegistry, ToolSpec

    slow = ToolRegistry(latency_ms=10, timeout_ms=200)
    slow.register(
        ToolSpec(
            name="slow_query",
            description="慢查询 只读",
            params={"q": {"type": "str", "required": True}},
            handler=lambda q: {"q": q},
        )
    )
    slow.slow_tools["slow_query"] = 900
    timed_out = slow.call("slow_query", {"q": "orders"})
    print(timed_out.error, "| elapsed:", timed_out.elapsed_ms)

    print("\n== 返回值污染 ==")
    print(reg.poisoned("订单 A1001 已支付")[:80])


if __name__ == "__main__":
    demo()
