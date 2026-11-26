# -*- coding: utf-8 -*-
"""把 ch52 的测试对齐到修好之后的 mcp_sim：

- 缺必填的用例改用只读工具（refund 现在会先被权限拦掉，那是对的）
- 补 4 条新断言：read 调 write 也越权、并行不清审计日志、工具超时、金额范围
"""

from pathlib import Path

P = Path(__file__).resolve().parent.parent / "labs" / "ch52-mcp-tools" / "test_ch52_mcp.py"
text = P.read_text(encoding="utf-8")

old_missing = '''def test_missing_required_is_rejected():
    reg = default_registry()
    call = reg.call("refund_order", {"order_id": "A1001"})
    assert "缺少必填参数" in call.error'''
new_missing = '''def test_missing_required_is_rejected():
    # 用只读工具测 Schema：refund_order 现在会先被权限挡住（见下面的越权用例）
    reg = default_registry()
    call = reg.call("get_order", {})
    assert "缺少必填参数 order_id" in call.error'''
assert old_missing in text
text = text.replace(old_missing, new_missing)

extra = '''

def test_write_tool_is_blocked_for_read_token():
    """read 令牌调 write 工具也算越权——这条以前是漏的，只拦了 admin。"""
    reg = default_registry()
    call = reg.call("refund_order", {"order_id": "A1001", "amount": 100})
    assert "越权" in call.error
    assert "需要 write" in call.error
    assert call.result is None


def test_parallel_does_not_wipe_audit_log():
    """并行不能清空已有日志，否则事后查不到「之前调过什么」。"""
    reg = default_registry()
    reg.call("get_order", {"order_id": "A1"})
    reg.call_many([("get_order", {"order_id": "A2"}), ("get_order", {"order_id": "A3"})], mode="parallel")
    assert len(reg.calls) == 3


def test_tool_timeout_is_testable():
    """超时以前根本触发不了（ToolTimeout 从未被 raise）。"""
    from mcp_sim import ToolRegistry

    reg = ToolRegistry(latency_ms=10, timeout_ms=200)
    reg.register(
        ToolSpec(
            name="slow_query",
            description="慢查询 只读",
            params={"q": {"type": "str", "required": True}},
            handler=lambda q: {"q": q},
        )
    )
    reg.slow_tools["slow_query"] = 900
    call = reg.call("slow_query", {"q": "orders"})
    assert "工具超时" in call.error
    assert call.result is None
    assert call.elapsed_ms == 900


def test_amount_range_and_bool_are_rejected():
    """bool 是 int 子类，isinstance 会放过 True；负数以前也没有下限。"""
    reg = default_registry()
    reg.allow_scope = "write"
    assert "期望 int" in reg.call("refund_order", {"order_id": "A1", "amount": True}).error
    assert "不能小于" in reg.call("refund_order", {"order_id": "A1", "amount": -1}).error
    assert "不能大于" in reg.call("refund_order", {"order_id": "A1", "amount": 999999}).error
    assert reg.call("refund_order", {"order_id": "A1", "amount": 100}).error is None
'''
P.write_text(text.rstrip() + extra, encoding="utf-8")
print("ch52 tests patched")
