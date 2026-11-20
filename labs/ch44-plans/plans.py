"""第 44 章：测试计划与异步执行。

计划 = 一批用例；执行器 = 队列 + worker 线程；关注点是状态机、重试与不阻塞调用方。
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass


class PlanError(ValueError):
    pass


@dataclass
class Plan:
    id: str
    name: str
    cases: list
    max_attempts: int = 2

    def __post_init__(self):
        if not self.cases:
            raise PlanError("计划里至少要有一条用例")


@dataclass
class Task:
    plan_id: str
    case_id: str
    status: str = "queued"
    attempts: int = 0
    error: str = ""


class Runner:
    """一个 worker 线程 + 队列；状态 queued -> running -> passed/failed（失败可重试）。"""

    def __init__(self, execute, notifier=None):
        self.execute = execute
        self.notifier = notifier or (lambda event, task: None)
        self.queue = queue.Queue()
        self.tasks = {}
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def submit(self, plan):
        created = []
        for case in plan.cases:
            case_id = case if isinstance(case, str) else case.get("id")
            task = Task(plan_id=plan.id, case_id=case_id)
            with self.lock:
                self.tasks[(plan.id, case_id)] = task
            self.queue.put((plan, task))
            created.append(task)
        return created

    def _loop(self):
        while True:
            item = self.queue.get()
            if item is None:
                return
            plan, task = item
            task.status = "running"
            self.notifier("start", task)
            try:
                self.execute(task.case_id)
                task.status = "passed"
                self.notifier("passed", task)
            except Exception as exc:  # noqa: BLE001 - 单条失败不拖垮队列
                task.attempts += 1
                if task.attempts < plan.max_attempts:
                    task.status = "queued"
                    self.queue.put((plan, task))
                    self.notifier("retry", task)
                else:
                    task.status = "failed"
                    task.error = str(exc)
                    self.notifier("failed", task)
            finally:
                self.queue.task_done()

    def wait_idle(self, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self.lock:
                done = all(t.status in ("passed", "failed") for t in self.tasks.values())
            if done:
                return True
            time.sleep(0.01)
        return False

    def summary(self):
        with self.lock:
            values = list(self.tasks.values())
        return {
            "total": len(values),
            "passed": sum(1 for t in values if t.status == "passed"),
            "failed": sum(1 for t in values if t.status == "failed"),
            "queued": sum(1 for t in values if t.status == "queued"),
        }

    def close(self):
        self.queue.put(None)
        self.thread.join(timeout=2)
