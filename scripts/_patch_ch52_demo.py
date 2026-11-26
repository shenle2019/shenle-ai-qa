# -*- coding: utf-8 -*-
"""ch52 的演示脚本对齐修好之后的 mcp_sim：

- 「必填缺失」改用只读工具，否则会先撞上权限（那也对，但会误导读者）
- 新增「read 调 write」「工具超时」「金额范围」三段，都是修完才能演示的
- 并行段顺便打印审计日志条数，让「不清日志」这件事看得见
"""

from pathlib import Path

P = Path(__file__).resolve().parent.parent / "labs" / "ch52-mcp-tools" / "ch52_cases.py"
text = P.read_text(encoding="utf-8")

old = '''    print("\\n== 必填缺失 ==")
    print(reg.call("refund_order", {"order_id": "A1001"}).error)'''
new = '''    print("\\n== 必填缺失 ==")
    print(reg.call("get_order", {}).error)'''
assert old in text
text = text.replace(old, new)

old_perm = '''    print("\\n== 越权（read 令牌调 admin）==")
    print(reg.call("export_all_orders", {"dst": "/tmp/a.csv"}).error)'''
new_perm = '''    print("\\n== 越权（read 令牌调 admin）==")
    print(reg.call("export_all_orders", {"dst": "/tmp/a.csv"}).error)

    print("\\n== 越权（read 令牌调 write，以前是漏洞）==")
    print(reg.call("refund_order", {"order_id": "A1001", "amount": 100}).error)

    print("\\n== 金额范围（bool 曾能混进 int）==")
    print(reg.allow_scope := "write")
    print(reg.call("refund_order", {"order_id": "A1001", "amount": True}).error)
    print(reg.call("refund_order", {"order_id": "A1001", "amount": -1}).error)
    print(reg.call("refund_order", {"order_id": "A1001", "amount": 100}).error)'''
assert old_perm in text
text = text.replace(old_perm, new_perm)

old_par = '''    parallel = reg2.call_many([("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"})], mode="parallel")
    print("并行结果:", [c.result for c in parallel])'''
new_par = '''    parallel = reg2.call_many([("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"})], mode="parallel")
    print("并行结果:", [c.result for c in parallel])
    print("审计日志条数（清空就会变 2）:", len(reg2.calls))

    print("\\n== 工具超时（以前 ToolTimeout 从未被 raise）==")
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
    print(timed_out.error, "| elapsed:", timed_out.elapsed_ms)'''
assert old_par in text
text = text.replace(old_par, new_par)

P.write_text(text, encoding="utf-8")
print("ch52_cases.py demo patched")
