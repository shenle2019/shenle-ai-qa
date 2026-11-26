# -*- coding: utf-8 -*-
"""修 mcp_sim 的四个真实缺陷（ch52 的审校子代理实测出来的）。

1. 权限：`spec.scope != allow_scope and spec.scope == "admin"` 只拦 admin，
   read 令牌能调 write 工具（退款）。改成等级比较 read < write < admin。
2. 并行：`call_many(mode="parallel")` 里 `self.calls = []` 会把已有审计日志清空。
   改成不清，只在返回值里标注顺序可能交错。
3. 超时：`ToolTimeout` 从来没有被 raise 过，`elapsed_ms` 是常量，
   「工具超时」这一类故障根本测不了。加 `slow_tools` + `timeout_ms`。
4. 校验：`amount=True` 能通过（bool 是 int 子类）、`amount=-1` 也能通过。
   改成 `type(value) is` 严格判断，并支持 min/max。
"""

from pathlib import Path

P = Path(__file__).resolve().parent.parent / "labs" / "_shared" / "mcp_sim.py"
text = P.read_text(encoding="utf-8")

# ---- 1. 严格类型 + 范围校验 ----
old_validate = """            value = args[key]
            expected = rule.get("type", "str")
            if expected == "int" and not isinstance(value, int):
                raise SchemaError(f"参数 {key} 期望 int，实际 {type(value).__name__}")
            if expected == "str" and not isinstance(value, str):
                raise SchemaError(f"参数 {key} 期望 str，实际 {type(value).__name__}")
            if expected == "bool" and not isinstance(value, bool):
                raise SchemaError(f"参数 {key} 期望 bool，实际 {type(value).__name__}")
            if "enum" in rule and value not in rule["enum"]:
                raise SchemaError(f"参数 {key} 必须是 {rule['enum']} 之一")"""
new_validate = """            value = args[key]
            expected = rule.get("type", "str")
            # 用 type() is 而不是 isinstance：bool 是 int 的子类，
            # isinstance(True, int) 为真，于是 amount=True 会静悄悄地过。
            type_ok = {
                "int": type(value) is int,
                "str": type(value) is str,
                "bool": type(value) is bool,
            }.get(expected, True)
            if not type_ok:
                raise SchemaError(f"参数 {key} 期望 {expected}，实际 {type(value).__name__}")
            if "enum" in rule and value not in rule["enum"]:
                raise SchemaError(f"参数 {key} 必须是 {rule['enum']} 之一")
            if expected == "int":
                low, high = rule.get("min"), rule.get("max")
                if low is not None and value < low:
                    raise SchemaError(f"参数 {key} 不能小于 {low}，实际 {value}")
                if high is not None and value > high:
                    raise SchemaError(f"参数 {key} 不能大于 {high}，实际 {value}")"""
assert old_validate in text
text = text.replace(old_validate, new_validate)

# ---- 2. 权限按等级比较 ----
old_perm = """        if spec.scope != self.allow_scope and spec.scope == "admin":
            call.error = f"越权：{name} 需要 admin"
            self.calls.append(call)
            return call"""
new_perm = """        if SCOPE_RANK.get(spec.scope, 99) > SCOPE_RANK.get(self.allow_scope, 0):
            call.error = f"越权：{name} 需要 {spec.scope} 权限，当前是 {self.allow_scope}"
            self.calls.append(call)
            return call"""
assert old_perm in text
text = text.replace(old_perm, new_perm)

# 等级表放在 ToolSpec 之前
old_marker = "@dataclass\nclass ToolSpec:"
new_marker = '''# 权限等级：read < write < admin。写成等级表才能一眼看出「read 调 write 也算越权」
SCOPE_RANK = {"read": 1, "write": 2, "admin": 3}


@dataclass
class ToolSpec:'''
assert old_marker in text
text = text.replace(old_marker, new_marker, 1)

# ---- 3. 并行不再清空审计日志 ----
old_many = '''    def call_many(self, requests: list[tuple[str, dict]], mode: str = "serial") -> list[Call]:
        """mode=serial 顺序执行；mode=parallel 并发执行（这里用交错顺序模拟）。"""
        if mode == "serial":
            return [self.call(n, a) for n, a in requests]
        self.calls = []  # 并行时日志容易乱序，先清空便于断言
        results = [self.call(n, a) for n, a in requests]
        return results'''
new_many = '''    def call_many(self, requests: list[tuple[str, dict]], mode: str = "serial") -> list[Call]:
        """mode=serial 顺序执行；mode=parallel 并发执行（这里用交错顺序模拟）。

        注意：并行时 self.calls 里的顺序不保证等于 requests 的顺序，
        但**绝不清空**已有日志——审计日志被清掉，事后就无法回答「谁在什么时候调了什么」。
        """
        if mode == "serial":
            return [self.call(n, a) for n, a in requests]
        results = [self.call(n, a) for n, a in requests]
        return results'''
assert old_many in text
text = text.replace(old_many, new_many)

# ---- 4. 超时：slow_tools + timeout_ms ----
old_fields = '''    latency_ms: float = 0.0
    fail_tools: dict[str, str] = field(default_factory=dict)  # 工具名 -> 抛什么错'''
new_fields = '''    latency_ms: float = 0.0
    fail_tools: dict[str, str] = field(default_factory=dict)  # 工具名 -> 抛什么错
    slow_tools: dict[str, float] = field(default_factory=dict)  # 工具名 -> 真实耗时 ms
    timeout_ms: float | None = None  # 超过它就抛 ToolTimeout'''
assert old_fields in text
text = text.replace(old_fields, new_fields)

old_call_tail = """        call.result = spec.handler(**cleaned)
        call.elapsed_ms = self.latency_ms
        self.calls.append(call)
        return call"""
new_call_tail = """        cost = self.slow_tools.get(name, self.latency_ms)
        if self.timeout_ms is not None and cost > self.timeout_ms:
            call.elapsed_ms = cost
            call.error = f"工具超时：{name} 用了 {cost}ms，上限 {self.timeout_ms}ms"
            self.calls.append(call)
            return call
        call.result = spec.handler(**cleaned)
        call.elapsed_ms = cost
        self.calls.append(call)
        return call"""
assert old_call_tail in text
text = text.replace(old_call_tail, new_call_tail)

# 退款金额加范围（模拟「不能退负数、不能退超过实付」）
old_refund = '''                "amount": {"type": "int", "required": True},'''
new_refund = '''                "amount": {"type": "int", "required": True, "min": 1, "max": 5000},'''
assert old_refund in text
text = text.replace(old_refund, new_refund)

P.write_text(text, encoding="utf-8")
print("mcp_sim.py patched")
