from ch52_cases import default_registry, to_json  # noqa: F401

from mcp_sim import SchemaError, ToolSpec


def test_normal_call_returns_result():
    reg = default_registry()
    call = reg.call("get_order", {"order_id": "A1001"})
    assert call.error is None
    assert call.result["status"] == "paid"


def test_wrong_type_is_rejected():
    reg = default_registry()
    call = reg.call("get_order", {"order_id": 1001})
    assert "期望 str" in call.error


def test_missing_required_is_rejected():
    # 用只读工具测 Schema：refund_order 现在会先被权限挡住（见下面的越权用例）
    reg = default_registry()
    call = reg.call("get_order", {})
    assert "缺少必填参数 order_id" in call.error


def test_undeclared_argument_is_rejected():
    reg = default_registry()
    call = reg.call("get_order", {"order_id": "A1001", "debug": True})
    assert "未声明参数" in call.error


def test_enum_is_enforced():
    reg = default_registry()
    reg.register(
        ToolSpec(
            name="set_status",
            description="状态 写",
            params={"status": {"type": "str", "required": True, "enum": ["paid", "refunded"]}},
            handler=lambda status: {"status": status},
            scope="read",
        )
    )
    assert reg.call("set_status", {"status": "unknown"}).error
    assert reg.call("set_status", {"status": "paid"}).error is None


def test_unknown_tool_is_reported_not_crashed():
    reg = default_registry()
    assert "没有这个工具" in reg.call("drop_database", {}).error


def test_admin_scope_is_blocked_for_read_token():
    reg = default_registry()
    assert "越权" in reg.call("export_all_orders", {"dst": "/tmp/a.csv"}).error


def test_tool_failure_is_captured():
    reg = default_registry()
    reg.fail_tools["get_order"] = "上游 502"
    call = reg.call("get_order", {"order_id": "A1001"})
    assert call.error == "上游 502"
    assert call.result is None


def test_serial_calls_keep_order():
    reg = default_registry()
    calls = reg.call_many([("get_order", {"order_id": "A1"}), ("get_order", {"order_id": "A2"})], mode="serial")
    assert [c.args["order_id"] for c in calls] == ["A1", "A2"]


def test_parallel_calls_all_succeed():
    reg = default_registry()
    calls = reg.call_many([("get_order", {"order_id": f"A{i}"}) for i in range(3)], mode="parallel")
    assert len(calls) == 3
    assert all(c.error is None for c in calls)


def test_audit_log_is_json_serialisable():
    reg = default_registry()
    call = reg.call("get_order", {"order_id": "A1001"})
    line = to_json(call)
    assert '"tool": "get_order"' in line


def test_choice_can_pick_wrong_tool():
    reg = default_registry()
    # 「导出」同时出现在 refund 与 export 的描述里，弱模型可能选错
    picked = reg.choose("导出 订单 退款")
    assert picked in {"export_all_orders", "refund_order"}


def test_poisoned_result_contains_injected_instruction():
    reg = default_registry()
    text = reg.poisoned("订单 A1001 已支付")
    assert "忽略以上" in text

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
