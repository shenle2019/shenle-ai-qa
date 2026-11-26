"""第 53 章用例：Agent 的规划、循环、记忆、不可逆操作。

Agent 测试的核心不是「它答得对不对」，而是「它会不会闯祸」：
1. 目标拆成步骤，顺序对不对（先查再改，最后验证）
2. 会不会在同一个动作上打转（死循环）
3. 记忆会不会串台、会不会过期还当有效
4. 不可逆动作（退款、导出）有没有确认闸门
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))

from agent_sim import Agent, Memory, make_plan  # noqa: E402
from mcp_sim import default_registry  # noqa: E402


def plan_actions(goal: str) -> list[str]:
    return [f"{s.action}:{s.target}" for s in make_plan(goal).steps]


def run_agent(goal: str, token: str | None = None, allow_scope: str = "admin") -> dict:
    reg = default_registry()
    reg.allow_scope = allow_scope
    agent = Agent(reg, max_steps=8, repeat_limit=2)
    result = agent.run(goal, confirm_token=token)
    return {
        "status": result.status,
        "trace": result.trace,
        "executed": [f"{s.action}:{s.target}" for s in result.executed],
        "blocked": [f"{s.action}:{s.target}" for s in result.blocked],
        "calls": len(reg.calls),
    }


def memory_roundtrip() -> dict:
    mem = Memory(short_limit=2)
    mem.remember("第一句")
    mem.remember("第二句")
    mem.remember("第三句")
    mem.put_long("user_pref", "中文", turn=0, ttl=2)
    return {
        "short": list(mem.short),
        "alive_at_1": mem.get_long("user_pref", turn=1),
        "alive_at_3": mem.get_long("user_pref", turn=3),
        "gc": mem.gc(turn=3),
    }


def demo() -> None:
    print("== 规划 ==")
    for goal in ("帮我退款", "把订单导出", "查一下订单", "帮我写首诗"):
        print(f"{goal}: {plan_actions(goal)}")

    print("\n== 无确认：不可逆操作被拦 ==")
    r = run_agent("帮我退款")
    print("status:", r["status"])
    print("trace:", r["trace"])
    print("blocked:", r["blocked"], "calls:", r["calls"])

    print("\n== 有确认：执行到底 ==")
    r2 = run_agent("帮我退款", token="confirm-refund")
    print("status:", r2["status"], "executed:", r2["executed"])

    print("\n== 记忆 ==")
    print(memory_roundtrip())

    print("\n== 死循环（构造一个重复步骤的计划）==")
    from agent_sim import Agent as A
    from agent_sim import Plan, Step

    class Stuck(A):
        def run(self, goal, confirm_token=None):  # noqa: ANN001
            plan = Plan(goal, [Step("query", "order", {"order_id": "A1001"})] * 5)
            seen, trace = {}, []
            for step in plan.steps:
                seen[step.key()] = seen.get(step.key(), 0) + 1
                if seen[step.key()] > self.repeat_limit:
                    trace.append("loop detected")
                    return type("R", (), {"status": "loop", "trace": trace})()
            return type("R", (), {"status": "done", "trace": trace})()

    stuck = Stuck(default_registry()).run("查订单")
    print("status:", stuck.status, "trace:", stuck.trace)


if __name__ == "__main__":
    demo()
