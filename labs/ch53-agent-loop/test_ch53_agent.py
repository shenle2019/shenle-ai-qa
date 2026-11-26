from ch53_cases import memory_roundtrip, plan_actions, run_agent  # noqa: F401

from agent_sim import Agent, Memory, Plan, Step, make_plan
from mcp_sim import default_registry


def test_refund_plan_queries_before_writing():
    plan = plan_actions("帮我退款")
    assert plan[0].startswith("query")
    assert plan[1].startswith("write")
    assert plan[2].startswith("verify")


def test_unknown_goal_yields_empty_plan():
    assert plan_actions("帮我写首诗") == []


def test_plan_steps_are_addressable_by_key():
    keys = [s.key() for s in make_plan("帮我退款").steps]
    assert len(set(keys)) == len(keys)


def test_irreversible_action_is_blocked_without_token():
    r = run_agent("帮我退款")
    assert r["status"] == "blocked"
    assert any(b.startswith("write") for b in r["blocked"])


def test_irreversible_action_runs_with_token():
    r = run_agent("帮我退款", token="confirm-refund")
    assert r["status"] == "done"
    assert any(e.startswith("write") for e in r["executed"])


def test_blocked_run_does_not_execute_write():
    r = run_agent("帮我退款")
    assert not any(e.startswith("write") for e in r["executed"])


def test_tool_error_stops_the_run():
    reg = default_registry()
    reg.allow_scope = "admin"
    reg.fail_tools["get_order"] = "上游 502"
    r = Agent(reg).run("查一下订单")
    assert r.status == "tool_error"


def test_loop_guard_stops_repeated_steps():
    class Stuck(Agent):
        def run(self, goal, confirm_token=None):  # noqa: ANN001
            plan = Plan(goal, [Step("query", "order", {"order_id": "A1"})] * 5)
            seen: dict[str, int] = {}
            for step in plan.steps:
                seen[step.key()] = seen.get(step.key(), 0) + 1
                if seen[step.key()] > self.repeat_limit:
                    return type("R", (), {"status": "loop"})()
            return type("R", (), {"status": "done"})()

    assert Stuck(default_registry()).run("查订单").status == "loop"


def test_max_steps_caps_execution():
    reg = default_registry()
    reg.allow_scope = "admin"
    agent = Agent(reg, max_steps=1)
    r = agent.run("帮我退款", confirm_token="confirm-refund")
    assert r.status == "max_steps"


def test_short_memory_keeps_recent_items():
    mem = Memory(short_limit=2)
    for s in ("a", "b", "c"):
        mem.remember(s)
    assert mem.short == ["b", "c"]


def test_long_memory_expires_after_ttl():
    out = memory_roundtrip()
    assert out["alive_at_1"] == "中文"
    assert out["alive_at_3"] is None
    assert out["gc"] == 0


def test_working_memory_records_step_results():
    reg = default_registry()
    reg.allow_scope = "admin"
    agent = Agent(reg)
    r = agent.run("查一下订单")
    assert r.status == "done"
    assert "query:order" in agent.memory.working
