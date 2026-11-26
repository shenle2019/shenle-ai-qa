"""第 49 章用例：Prompt 专项测试与回归。

四个可断言的点：
1. 明确 vs 模糊：同一功能，两种写法的通过率有差
2. 稳定性：同 prompt 重复 N 次的一致率
3. A/B：按用户分桶，两版各跑一半
4. 回归：改了 prompt 或换了模型，哪些用例会掉
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))

from llm_sim import FakeLLM  # noqa: E402

TEMPLATE = "你是{role}。用户问题：{question}。要求：{rule}"


def render(template: str, **kwargs) -> str:
    """极简模板渲染：缺变量要立刻报错，不能留 {question} 到线上去。"""
    class _Missing(dict):
        def __missing__(self, key):  # pragma: no cover - 直接抛
            raise KeyError(f"模板缺变量：{key}")

    return template.format_map(_Missing(**kwargs))


@dataclass
class PromptVersion:
    version: str
    body: str


def pass_rate(llm: FakeLLM, cases: list[tuple[str, str]], seed: int = 0) -> float:
    ok = 0
    for prompt, expect in cases:
        if expect in llm.answer(prompt, seed=seed).text:
            ok += 1
    return round(ok / len(cases), 2)


def stability(llm: FakeLLM, prompt: str, rounds: int = 6) -> float:
    outs = [llm.answer(prompt, seed=i).text for i in range(rounds)]
    return round(outs.count(max(set(outs), key=outs.count)) / rounds, 2)


def bucket(user_id: str, buckets: int = 2) -> int:
    """按 user_id 稳定分桶：同一用户永远落同一桶，避免「刷新就换版本」。"""
    h = int(hashlib.sha1(user_id.encode("utf-8")).hexdigest(), 16)
    return h % buckets


def ab_assign(user_ids: list[str], buckets: int = 2) -> dict[int, int]:
    counts = {i: 0 for i in range(buckets)}
    for uid in user_ids:
        counts[bucket(uid, buckets)] += 1
    return counts


def regression(old: dict[str, bool], new: dict[str, bool]) -> dict[str, list[str]]:
    """回归对比：变坏的、修好的、稳定通过的。"""
    broke = [k for k in old if old[k] and not new.get(k, False)]
    fixed = [k for k in old if not old[k] and new.get(k, False)]
    return {"broke": broke, "fixed": fixed, "passed": [k for k in old if old[k] and new.get(k, False)]}


def demo() -> None:
    print("== 模板渲染 ==")
    print(render(TEMPLATE, role="客服", question="怎么退款", rule="只答退款流程"))
    try:
        render(TEMPLATE, role="客服")
    except KeyError as exc:
        print("缺变量报错:", exc)

    clear = [("请用三句话说明退款流程，并列出需要的材料。", "退款")]
    vague = [("退款", "退款")]
    strict = FakeLLM(jitter=0.0)
    print("\n== 明确 vs 模糊（jitter=0）==", pass_rate(strict, clear), pass_rate(strict, vague))

    shaky = FakeLLM(jitter=0.5)
    print("== 稳定性（jitter=0.5）==", stability(shaky, "我要退款"))
    print("== 稳定性（jitter=0）==", stability(FakeLLM(), "我要退款"))

    ids = [f"user-{i}" for i in range(200)]
    print("\n== 分桶 ==", ab_assign(ids))

    print("\n== 回归 ==", regression({"a": True, "b": True, "c": False}, {"a": True, "b": False, "c": True}))


if __name__ == "__main__":
    demo()
