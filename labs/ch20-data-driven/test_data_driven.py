r"""第 20 章：数据驱动与多用例管理。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch20-data-driven -q

看点：8 条业务用例全部来自 `cases.yaml`，这个测试文件里没有一条 if/else 业务分支。
"""

from __future__ import annotations

import pytest

from runner import HANDLERS, load_cases, run_all, run_case, summary

CASES = load_cases()


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_case_from_yaml(page, site, case):
    result = run_case(page, site, case)
    assert result.ok, str(result)


def test_yaml_schema():
    for case in CASES:
        assert {"id", "title", "action", "expect"} <= set(case), f"{case} 缺字段"
        assert case["action"] in HANDLERS, f"{case['id']} 的 action 未注册"


def test_unknown_action_is_rejected(page, site):
    with pytest.raises(ValueError):
        run_case(page, site, {"id": "x", "title": "x", "action": "not-a-handler", "expect": {}})


def test_failure_is_captured_not_raised(page, site):
    bad = {"id": "bad", "title": "故意写错的期望", "action": "login",
           "params": {"username": "alice", "password": "secret"},
           "expect": {"current_user": "bob"}}
    result = run_case(page, site, bad)
    assert result.ok is False
    assert result.case_id == "bad" and result.detail


def test_batch_keeps_going_after_failure(page, site):
    bad = {"id": "bad", "title": "失败但不断批", "action": "search",
           "params": {"query": "测试"}, "expect": {"count": 99}}
    batch = [bad, CASES[0]]
    results = run_all(page, site, batch)
    assert [r.ok for r in results] == [False, True]


def test_summary_counts(page, site):
    results = run_all(page, site, CASES)
    stat = summary(results)
    assert stat["total"] == len(CASES)
    assert stat["failed"] == 0, "\n".join(str(r) for r in results if not r.ok)
