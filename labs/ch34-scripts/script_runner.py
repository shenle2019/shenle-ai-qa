"""第 34 章：把「压什么」和「用什么数据压」分开。

一个压测脚本 = 步骤列表 + 数据集 + 思考时间。
- 步骤：每个步骤有自己的权重、断言，统计也按步骤分开
- 数据集：从 yaml/csv 读，按 user 索引轮转，保证「同一个用户永远拿到同一行数据」
- 思考时间：模拟真实用户的停顿，避免把接口压成 CPU 跑分
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

__all__ = ["Step", "Script", "DataSet", "StepStats", "load_script", "run_script"]


@dataclass
class Step:
    """一个步骤：拿一行数据，发一次请求，可断言。"""

    name: str
    weight: int = 1
    think_s: float = 0.0
    pick: Callable[[dict], dict] | None = None
    call: Callable[[dict], tuple[int, float]] | None = None
    expect: Callable[[int], bool] | None = None

    def run(self, row: dict) -> tuple[int, float, bool]:
        """返回 (状态码, 耗时, 是否通过)。expect 给了就按它判，否则按 2xx/3xx 判。"""
        if self.call is None:
            raise ValueError(f"步骤 {self.name} 没有实现 call")
        payload = self.pick(row) if self.pick else row
        status, elapsed = self.call(payload)
        ok = self.expect(status) if self.expect else 200 <= status < 400
        if self.think_s > 0:
            time.sleep(self.think_s)
        return status, elapsed, ok


@dataclass
class DataSet:
    rows: list[dict]
    cursor: int = 0

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("数据集不能为空")

    def next(self) -> dict:
        row = self.rows[self.cursor % len(self.rows)]
        self.cursor += 1
        return row

    def for_user(self, user: int) -> dict:
        """同一个 user 永远取同一行：用 user 取模，不共享游标。"""
        return self.rows[user % len(self.rows)]


@dataclass
class StepStats:
    name: str
    samples: list[float] = field(default_factory=list)
    errors: int = 0

    def add(self, elapsed_ms: float, ok: bool) -> None:
        self.samples.append(elapsed_ms)
        if not ok:
            self.errors += 1

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def avg_ms(self) -> float:
        return round(sum(self.samples) / self.count, 2) if self.samples else 0.0

    @property
    def max_ms(self) -> float:
        return round(max(self.samples), 2) if self.samples else 0.0

    def summary(self) -> dict:
        return {"step": self.name, "count": self.count, "avg_ms": self.avg_ms, "max_ms": self.max_ms, "errors": self.errors}


@dataclass
class Script:
    name: str
    steps: list[Step]
    users: int = 1
    loops: int = 1
    seed: int = 20251120

    def pick_step(self, rng: random.Random) -> Step:
        weights = [s.weight for s in self.steps]
        return rng.choices(self.steps, weights=weights, k=1)[0]

    def summary(self) -> dict:
        return {"script": self.name, "users": self.users, "loops": self.loops, "steps": [s.name for s in self.steps]}


def load_script(path: str | Path) -> Script:
    """从 yaml 读脚本定义；call/pick/expect 由调用方注入（yaml 里只写名字与参数）。"""
    import yaml

    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    steps = [
        Step(name=item["name"], weight=int(item.get("weight", 1)), think_s=float(item.get("think_s", 0)))
        for item in raw.get("steps", [])
    ]
    if not steps:
        raise ValueError("脚本里至少要有一个步骤")
    return Script(name=raw.get("name", "script"), steps=steps, users=int(raw.get("users", 1)), loops=int(raw.get("loops", 1)))


def run_script(
    script: Script,
    dataset: DataSet,
    observer: Callable[[StepStats], None] | None = None,
) -> dict[str, StepStats]:
    """顺序跑 users × loops 次，每个 user 固定拿一行数据。"""
    rng = random.Random(script.seed)
    stats: dict[str, StepStats] = {s.name: StepStats(s.name) for s in script.steps}
    for user in range(script.users):
        row = dataset.for_user(user)
        for _ in range(script.loops):
            step = script.pick_step(rng)
            bucket = stats[step.name]
            try:
                _status, elapsed, ok = step.run(row)
                bucket.add(elapsed, ok)
            except Exception:
                bucket.add(0.0, False)
            if observer:
                observer(bucket)
    return stats


def load_rows(path: str | Path) -> list[dict]:
    """支持 csv 与 yaml 列表两种形状。"""
    path = Path(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return [dict(item) for item in (data or [])]
    import csv

    with path.open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]
