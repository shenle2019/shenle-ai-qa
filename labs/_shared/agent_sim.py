"""可复现的 Agent 模拟器：规划、循环检测、三类记忆、不可逆操作守卫、越权拦截。

每个失败模式都有独立的开关，所以「Agent 会不会卡死」「会不会把不可逆操作直接执行」
这类问题可以写成断言，而不是靠观察日志猜。
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Step:
    action: str
    target: str
    args: dict[str, Any] = field(default_factory=dict)

    def key(self) -> str:
        raw = f"{self.action}|{self.target}|{sorted(self.args.items())}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


@dataclass
class Plan:
    goal: str
    steps: list[Step]

    def describe(self) -> list[str]:
        return [f"{i + 1}. {s.action}({s.target})" for i, s in enumerate(self.steps)]


def make_plan(goal: str) -> Plan:
    """规则化规划器：把一句目标拆成「查 → 改 → 验证」。

    故意只覆盖几种目标，好处是拆错、顺序错都能被测试抓住。
    """
    if "退款" in goal:
        return Plan(
            goal,
            [
                Step("query", "order", {"order_id": "A1001"}),
                Step("write", "refund", {"order_id": "A1001", "amount": 199}),
                Step("verify", "order", {"order_id": "A1001"}),
            ],
        )
    if "导出" in goal:
        return Plan(
            goal,
            [
                Step("query", "order", {"order_id": "A1001"}),
                Step("write", "export", {"dst": "/tmp/all.csv"}),
            ],
        )
    if "查" in goal or "查询" in goal:
        return Plan(goal, [Step("query", "order", {"order_id": "A1001"})])
    # 无法规划：返回空计划，而不是瞎编一串步骤
    return Plan(goal, [])


@dataclass
class Memory:
    """三类记忆：working（本次任务）、short（会话内最近几轮）、long（跨会话的键值）。

    `ttl` 用「轮次」计数而不是真实时间，测试里才好精确过期。
    """

    working: dict[str, Any] = field(default_factory=dict)
    short: list[str] = field(default_factory=list)
    long: dict[str, tuple[Any, int]] = field(default_factory=dict)  # key -> (value, expire_at_turn)
    short_limit: int = 3

    def remember(self, text: str) -> None:
        self.short.append(text)
        if len(self.short) > self.short_limit:
            self.short = self.short[-self.short_limit :]

    def put_long(self, key: str, value: Any, turn: int, ttl: int = 3) -> None:
        self.long[key] = (value, turn + ttl)

    def get_long(self, key: str, turn: int) -> Any | None:
        item = self.long.get(key)
        if not item:
            return None
        value, expire_at = item
        if turn >= expire_at:
            self.long.pop(key, None)
            return None
        return value

    def gc(self, turn: int) -> int:
        dead = [k for k, (_, exp) in self.long.items() if turn >= exp]
        for k in dead:
            self.long.pop(k, None)
        return len(dead)


@dataclass
class AgentRun:
    trace: list[str]
    status: str
    executed: list[Step]
    loops: int = 0
    blocked: list[Step] = field(default_factory=list)
    confirmations: list[Step] = field(default_factory=list)


class Agent:
    """最小 Agent 循环。

    - `max_steps`：硬上限，防止某一步卡住无限重试
    - `loop_guard`：同一 step key 重复出现超过 `repeat_limit` 次就判定死循环
    - `require_confirm`：不可逆动作（side_effect 且 irreversible）必须拿到确认令牌
    """

    def __init__(self, tools: Any, memory: Memory | None = None, max_steps: int = 8, repeat_limit: int = 2) -> None:
        self.tools = tools
        self.memory = memory or Memory()
        self.max_steps = max_steps
        self.repeat_limit = repeat_limit
        self.pending: list[Step] = []

    def run(self, goal: str, confirm_token: str | None = None) -> AgentRun:
        plan = make_plan(goal)
        trace: list[str] = []
        executed: list[Step] = []
        blocked: list[Step] = []
        confirmations: list[Step] = []
        seen: dict[str, int] = {}
        loops = 0

        if not plan.steps:
            return AgentRun(trace=["无法把目标拆成步骤"], status="unplanned", executed=[])

        for idx, step in enumerate(plan.steps):
            if idx >= self.max_steps:
                trace.append("达到步数上限，停止")
                return AgentRun(trace, "max_steps", executed, loops, blocked, confirmations)
            seen[step.key()] = seen.get(step.key(), 0) + 1
            if seen[step.key()] > self.repeat_limit:
                loops += 1
                trace.append(f"检测到重复步骤，判定死循环：{step.action}({step.target})")
                return AgentRun(trace, "loop", executed, loops, blocked, confirmations)

            if step.action == "write" and step.target in {"refund", "export"}:
                if confirm_token != f"confirm-{step.target}":
                    blocked.append(step)
                    self.pending.append(step)
                    trace.append(f"不可逆操作被拦下，等待确认：{step.action}({step.target})")
                    continue
                confirmations.append(step)

            tool = {"query": "get_order", "write": None, "verify": "get_order"}[step.action]
            if tool is None:
                tool = "refund_order" if step.target == "refund" else "export_all_orders"
            call = self.tools.call(tool, step.args)
            trace.append(f"{step.action}({step.target}) -> {call.error or 'ok'}")
            if call.error:
                return AgentRun(trace, "tool_error", executed, loops, blocked, confirmations)
            self.memory.working[f"{step.action}:{step.target}"] = call.result
            executed.append(step)

        status = "blocked" if blocked else "done"
        return AgentRun(trace, status, executed, loops, blocked, confirmations)
