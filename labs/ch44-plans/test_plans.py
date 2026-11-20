"""第 44 章测试：计划校验、队列执行、失败重试、状态汇总。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plans import Plan, PlanError, Runner  # noqa: E402


def make_runner(fail=()):
    events = []

    def execute(case_id):
        if case_id in fail:
            raise AssertionError(f"{case_id} 坏了")
        return True

    return Runner(execute, notifier=lambda event, task: events.append((event, task.case_id))), events


def test_plan_requires_cases():
    with pytest.raises(PlanError, match="至少要有一条"):
        Plan(id="p0", name="空计划", cases=[])


def test_submit_creates_task_per_case():
    runner, _ = make_runner()
    tasks = runner.submit(Plan(id="p1", name="冒烟", cases=["a", "b", "c"]))
    assert len(tasks) == 3
    assert runner.wait_idle()
    runner.close()


def test_all_pass_summary():
    runner, events = make_runner()
    runner.submit(Plan(id="p2", name="冒烟", cases=["a", "b"]))
    assert runner.wait_idle()
    assert runner.summary()["passed"] == 2
    assert ("passed", "a") in events
    runner.close()


def test_failure_retries_then_fails():
    runner, events = make_runner(fail={"x"})
    runner.submit(Plan(id="p3", name="重试", cases=["x"], max_attempts=2))
    assert runner.wait_idle()
    assert [e for e, _ in events] == ["start", "retry", "start", "failed"]
    assert runner.summary()["failed"] == 1
    runner.close()


def test_single_attempt_fails_immediately():
    runner, events = make_runner(fail={"y"})
    runner.submit(Plan(id="p4", name="不重试", cases=["y"], max_attempts=1))
    assert runner.wait_idle()
    assert [e for e, _ in events] == ["start", "failed"]
    runner.close()


def test_close_stops_thread():
    runner, _ = make_runner()
    runner.submit(Plan(id="p5", name="a", cases=["a"]))
    assert runner.wait_idle()
    runner.close()
    assert not runner.thread.is_alive()


def test_two_plans_keep_separate_results():
    runner, _ = make_runner(fail={"b"})
    runner.submit(Plan(id="p6", name="ok", cases=["a"]))
    runner.submit(Plan(id="p7", name="bad", cases=["b"], max_attempts=1))
    assert runner.wait_idle()
    summary = runner.summary()
    assert summary["passed"] == 1 and summary["failed"] == 1
    runner.close()


def test_wait_idle_without_tasks_returns_true():
    runner, _ = make_runner()
    assert runner.wait_idle(timeout=0.05) is True
    runner.close()
