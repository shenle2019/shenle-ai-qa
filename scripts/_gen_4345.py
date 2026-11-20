# -*- coding: utf-8 -*-
"""生成 43–45 章的 labs 代码与测试。"""

from pathlib import Path


def w(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + "\n", encoding="utf-8")


w("labs/ch43-executor/executor.py", r'''
"""第 43 章：用例与关键字执行器。

一条用例 = 一串步骤；每一步都是一个「关键字 + 参数」。
执行器负责：变量替换、按序执行、失败即停、把结果整理成可读结构。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

VAR = re.compile(r"\$\{([a-zA-Z0-9_.]+)\}")


class CaseError(AssertionError):
    pass


def render(value, ctx):
    """把 ${user} 换成 ctx 里的值；取不到就报错，不静默变空。"""
    if isinstance(value, str):
        def one(m):
            key = m.group(1)
            if key not in ctx:
                raise CaseError(f"变量 {key} 没有值")
            return str(ctx[key])
        return VAR.sub(one, value)
    if isinstance(value, dict):
        return {k: render(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [render(v, ctx) for v in value]
    return value


def pick(data, path):
    """支持 a.b.0.c 的取值；取不到返回 None。"""
    cur = data
    for part in str(path).split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


@dataclass
class StepResult:
    index: int
    keyword: str
    ok: bool
    detail: str = ""


@dataclass
class CaseResult:
    case_id: str
    ok: bool
    steps: list = field(default_factory=list)
    error: str = ""

    @property
    def failed_step(self):
        for item in self.steps:
            if not item.ok:
                return item
        return None


def kw_http(case_ctx, session, method, path, body=None, headers=None, expect=None):
    url = case_ctx["base_url"] + path
    resp = session.request(method, url, json=body, headers=headers, timeout=5)
    case_ctx["last_status"] = resp.status_code
    case_ctx["last_json"] = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
    if expect is not None and resp.status_code != expect:
        raise CaseError(f"状态码期望 {expect}，实际 {resp.status_code}")
    return f"{method} {path} -> {resp.status_code}"


def kw_status(case_ctx, expected):
    actual = case_ctx.get("last_status")
    if actual != expected:
        raise CaseError(f"状态码期望 {expected}，实际 {actual}")
    return f"status == {expected}"


def kw_json(case_ctx, path, equals=None, exists=True):
    value = pick(case_ctx.get("last_json"), path)
    if exists and value is None:
        raise CaseError(f"响应里没有 {path}")
    if equals is not None and value != equals:
        raise CaseError(f"{path} 期望 {equals}，实际 {value}")
    return f"{path} = {value!r}"


def kw_extract(case_ctx, path, name):
    value = pick(case_ctx.get("last_json"), path)
    if value is None:
        raise CaseError(f"提取失败：响应里没有 {path}")
    case_ctx[name] = value
    return f"ctx[{name}] = {value!r}"


def kw_sleep(case_ctx, seconds):
    return f"sleep {seconds}s（演示用，不真的睡）"


KEYWORDS = {"http": kw_http, "status": kw_status, "json": kw_json, "extract": kw_extract, "sleep": kw_sleep}


def run_case(case, session, base_url, ctx=None):
    """case: {'id', 'steps': [{'kw': 'http', ...}]}；失败即停，返回 CaseResult。"""
    local = {"base_url": base_url}
    local.update(ctx or {})
    results = []
    for index, raw in enumerate(case.get("steps") or []):
        kw = raw.get("kw")
        args = render({k: v for k, v in raw.items() if k != "kw"}, local)
        fn = KEYWORDS.get(kw)
        if fn is None:
            results.append(StepResult(index, kw or "?", False, f"未知关键字 {kw}"))
            return CaseResult(case.get("id", ""), False, results, f"未知关键字 {kw}")
        try:
            detail = fn(local, session, **args) if kw == "http" else fn(local, **args)
            results.append(StepResult(index, kw, True, detail))
        except Exception as exc:  # noqa: BLE001 - 单步失败要记录而不是炸掉整批
            results.append(StepResult(index, kw, False, str(exc)))
            return CaseResult(case.get("id", ""), False, results, str(exc))
    return CaseResult(case.get("id", ""), True, results)


def summarise(results):
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    return {"total": total, "passed": passed, "failed": total - passed}
''')

w("labs/ch43-executor/test_executor.py", r'''
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from executor import CaseResult, CaseError, pick, render, run_case, summarise  # noqa: E402


class FakeSession:
    def __init__(self, payload=None, status=200):
        self.payload = payload or {"code": 100, "data": {"id": 7, "name": "alice"}}
        self.status = status
        self.calls = []

    def request(self, method, url, json=None, headers=None, timeout=None):
        self.calls.append((method, url, json))

        class R:
            status_code = self.status
            headers = {"content-type": "application/json"}

            def json(self):
                return self.payload

        return R()


CASE = {
    "id": "login-and-read",
    "steps": [
        {"kw": "http", "method": "POST", "path": "/api/login", "body": {"user": "alice"}, "expect": 200},
        {"kw": "status", "expected": 200},
        {"kw": "extract", "path": "data.id", "name": "uid"},
        {"kw": "json", "path": "code", "equals": 100},
        {"kw": "json", "path": "data.name", "equals": "${who}"},
    ],
}


def test_render_substitutes_and_raises_on_missing():
    assert render("${a}-${b}", {"a": 1, "b": "x"}) == "1-x"
    with pytest.raises(CaseError, match="没有值"):
        render("${nope}", {})


def test_pick_walks_dict_and_list():
    assert pick({"a": {"b": [1, {"c": 2}]}}, "a.b.1.c") == 2
    assert pick({"a": 1}, "a.b") is None


def test_run_case_passes_and_records_steps():
    result = run_case(CASE, FakeSession(), "http://x", {"who": "alice"})
    assert isinstance(result, CaseResult) and result.ok
    assert [s.keyword for s in result.steps] == ["http", "status", "extract", "json", "json"]


def test_http_expectation_failure_stops_the_case():
    result = run_case({"id": "c", "steps": [{"kw": "http", "method": "GET", "path": "/a", "expect": 201}]}, FakeSession(), "http://x")
    assert not result.ok
    assert "期望 201" in result.error
    assert len(result.steps) == 1


def test_unknown_keyword_is_reported():
    result = run_case({"id": "c", "steps": [{"kw": "teleport"}]}, FakeSession(), "http://x")
    assert not result.ok and "未知关键字" in result.error


def test_json_missing_path_fails():
    result = run_case({"id": "c", "steps": [{"kw": "json", "path": "data.nope"}]}, FakeSession(), "http://x")
    assert not result.ok and "没有 data.nope" in result.error


def test_extract_feeds_next_step():
    case = {
        "id": "c",
        "steps": [
            {"kw": "http", "method": "GET", "path": "/u"},
            {"kw": "extract", "path": "data.id", "name": "uid"},
            {"kw": "http", "method": "GET", "path": "/u/${uid}", "expect": 200},
        ],
    }
    session = FakeSession()
    result = run_case(case, session, "http://x")
    assert result.ok
    assert session.calls[-1][1] == "http://x/u/7"


def test_summarise_counts():
    good = run_case(CASE, FakeSession(), "http://x", {"who": "alice"})
    bad = run_case({"id": "b", "steps": [{"kw": "teleport"}]}, FakeSession(), "http://x")
    assert summarise([good, bad]) == {"total": 2, "passed": 1, "failed": 1}
''')

print("ch43 written")
