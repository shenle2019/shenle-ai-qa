"""第 34 章测试：脚本加载、数据轮转、权重、思考时间、统计分桶。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from script_runner import DataSet, Script, Step, load_rows, load_script, run_script  # noqa: E402


def test_load_script_reads_steps() -> None:
    script = load_script(HERE / "script.yaml")
    assert script.name == "登录下单混合场景"
    assert [s.name for s in script.steps] == ["登录", "查列表", "下单"]
    assert script.steps[1].weight == 3
    assert script.users == 2 and script.loops == 3


def test_load_rows_csv() -> None:
    rows = load_rows(HERE / "users.csv")
    assert len(rows) == 3
    assert rows[0]["user"] == "alice"


def test_dataset_for_user_is_stable() -> None:
    data = DataSet([{"u": 1}, {"u": 2}])
    assert data.for_user(0) == {"u": 1}
    assert data.for_user(1) == {"u": 2}
    assert data.for_user(2) == {"u": 1}


def test_dataset_next_rotates() -> None:
    data = DataSet([{"u": 1}, {"u": 2}])
    assert [data.next()["u"] for _ in range(3)] == [1, 2, 1]


def test_dataset_rejects_empty() -> None:
    with pytest.raises(ValueError):
        DataSet([])


def test_pick_step_honours_weight() -> None:
    script = Script(name="w", steps=[Step("a", weight=1), Step("b", weight=9)])
    import random

    rng = random.Random(7)
    picks = [script.pick_step(rng).name for _ in range(200)]
    assert picks.count("b") > picks.count("a") * 3


def test_run_script_counts_per_step() -> None:
    calls: list[str] = []

    def make(name: str):
        def _call(row: dict) -> tuple[int, float]:
            calls.append(name)
            return 200, 10.0

        return _call

    script = Script(name="s", steps=[Step("x", weight=1, call=make("x"))], users=2, loops=2)
    stats = run_script(script, DataSet([{"u": 1}]))
    assert stats["x"].count == 4
    assert stats["x"].errors == 0
    assert len(calls) == 4


def test_run_script_records_assertion_failure() -> None:
    def bad(row: dict) -> tuple[int, float]:
        return 500, 5.0

    script = Script(name="bad", steps=[Step("x", call=bad, expect=lambda s: s == 200)], users=1, loops=1)
    stats = run_script(script, DataSet([{"u": 1}]))
    assert stats["x"].errors == 1


def test_step_without_call_raises() -> None:
    with pytest.raises(ValueError):
        Step("none").run({})


def test_summary_shape() -> None:
    script = Script(name="s", steps=[Step("x", call=lambda row: (200, 3.0))], users=1, loops=1)
    stats = run_script(script, DataSet([{"u": 1}]))
    row = stats["x"].summary()
    assert row == {"step": "x", "count": 1, "avg_ms": 3.0, "max_ms": 3.0, "errors": 0}
