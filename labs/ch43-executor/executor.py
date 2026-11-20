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
