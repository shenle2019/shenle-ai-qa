"""可复现的假大模型：把「概率性、上下文窗口、流式延迟、记忆、护栏」变成可测的对象。

设计原则：确定性种子，同一 seed + 同一输入必得同一输出；所有可观测行为都能关掉，
这样测试里既能演示「不稳定」，也能在固定 seed 下断言。
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field


@dataclass
class Reply:
    """一次生成的结果，字段对齐真实 API 的可观测面。"""

    text: str
    tokens: list[str]
    ttft_ms: float
    tpot_ms: float
    total_ms: float
    truncated: bool = False
    refused: bool = False
    used_prompt_tokens: int = 0
    finish_reason: str = "stop"

    @property
    def token_count(self) -> int:
        return len(self.tokens)


def tokenize(text: str) -> list[str]:
    """按「单字 + 标点」切，接近中文分词的粒度，够用来算 TTFT/TPOT。"""
    out: list[str] = []
    for ch in text:
        if ch.strip():
            out.append(ch)
        elif out and out[-1] != " ":
            out.append(" ")
    return out or [""]


@dataclass
class FakeLLM:
    """假模型。

    - `context_limit`：prompt 超过它就按 `overflow_policy` 处理（truncate_head / error / silent）
    - `jitter`：每次输出选择的随机抖动幅度，0 表示完全确定
    - `latency_ms`：模拟 TTFT 与 TPOT 的基线，配合 `slow_factor` 做性能测试
    - `guardrails`：是否开启输入/输出护栏（注入检测、PII 打码）
    """

    model: str = "fake-llm-1"
    context_limit: int = 40
    overflow_policy: str = "truncate_head"
    jitter: float = 0.0
    latency_ms: float = 0.0
    tpot_ms: float = 0.0
    guardrails: bool = False
    memory_turns: int = 0
    _history: list[tuple[str, str]] = field(default_factory=list)
    _rng_counter: int = 0

    # ---- 上下文 ----
    def count_tokens(self, text: str) -> int:
        if not text or not text.strip():
            return 0
        return len(tokenize(text))

    def fit_context(self, prompt: str) -> tuple[str, bool]:
        """按策略把 prompt 塞进上下文窗口，返回（实际喂进去的 prompt, 是否截断）。"""
        tokens = tokenize(prompt)
        if len(tokens) <= self.context_limit:
            return prompt, False
        if self.overflow_policy == "error":
            raise ValueError(f"上下文溢出：{len(tokens)} > {self.context_limit}")
        if self.overflow_policy == "silent":
            # 静默丢弃，最危险的一种：调用方完全不知道头部被吃了
            kept = "".join(tokens[-self.context_limit :])
            return kept, True
        kept = "".join(tokens[: self.context_limit])
        return kept, True

    # ---- 生成 ----
    def _pick(self, candidates: list[str], prompt: str, seed: int) -> str:
        rng = random.Random(f"{seed}:{prompt}:{self._rng_counter}")
        self._rng_counter += 1
        if self.jitter <= 0:
            return candidates[0]
        idx = rng.randrange(len(candidates)) if rng.random() < self.jitter else 0
        return candidates[idx]

    def answer(self, prompt: str, seed: int = 0, max_tokens: int = 24) -> Reply:
        fitted, truncated = self.fit_context(prompt)
        if self.guardrails and looks_like_injection(fitted):
            return Reply(
                text="抱歉，我不能执行这条指令。",
                tokens=tokenize("抱歉，我不能执行这条指令。"),
                ttft_ms=self.latency_ms,
                tpot_ms=self.tpot_ms,
                total_ms=self.latency_ms,
                truncated=truncated,
                refused=True,
                used_prompt_tokens=self.count_tokens(fitted),
                finish_reason="refusal",
            )
        text = self._compose(fitted, seed=seed)
        if self.guardrails:
            text = mask_pii(text)
        tokens = tokenize(text)[:max_tokens]
        ttft = self.latency_ms
        per_token = self.tpot_ms
        total = ttft + per_token * max(len(tokens) - 1, 0)
        if total:
            time.sleep(0)  # 保持与真实调用相似的「可等待」语义，但不拖慢测试
        reply = Reply(
            text="".join(tokens),
            tokens=tokens,
            ttft_ms=ttft,
            tpot_ms=per_token,
            total_ms=total,
            truncated=truncated,
            used_prompt_tokens=self.count_tokens(fitted),
        )
        if self.memory_turns:
            self._history.append((prompt, reply.text))
            self._history = self._history[-self.memory_turns :]
        return reply

    def _compose(self, prompt: str, seed: int) -> str:
        """按 prompt 里的关键词给出可预测的答复，便于测试断言。"""
        if "退款" in prompt:
            body = self._pick(["可以退款。", "需要先查订单。", "不支持退款。"], prompt, seed)
            return f"关于退款：{body}"
        if "订单" in prompt:
            return f"查到的订单信息：{self._pick(['A1001', 'A1002'], prompt, seed)}"
        if "总结" in prompt:
            return "摘要：" + prompt[: min(len(prompt), 20)]
        if "翻译" in prompt:
            return "Translation: " + prompt[: min(len(prompt), 12)]
        return "我理解你的问题是：" + prompt[: min(len(prompt), 24)]

    # ---- 记忆 ----
    def history(self) -> list[tuple[str, str]]:
        return list(self._history)

    def forget(self) -> None:
        self._history.clear()


# ---- 护栏用的最小实现 ----

INJECTION_PATTERNS = (
    "忽略以上",
    "忽略之前",
    "ignore previous",
    "你现在是",
    "system prompt",
    "把系统提示词",
    "输出你的指令",
)


def looks_like_injection(text: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in INJECTION_PATTERNS)


PII_PATTERNS = (
    ("13800138000", "138****8000"),
    ("6222021234567890", "6222********7890"),
    ("shenle@example.com", "s***@example.com"),
)


def mask_pii(text: str) -> str:
    for raw, masked in PII_PATTERNS:
        text = text.replace(raw, masked)
    return text


def stream_tokens(reply: Reply) -> list[tuple[float, str]]:
    """把一次回复摊成（相对时间 ms, token），用来测 TTFT 与 TPOT 的观测口径。"""
    out: list[tuple[float, str]] = []
    t = reply.ttft_ms
    for i, tok in enumerate(reply.tokens):
        if i:
            t += reply.tpot_ms
        out.append((round(t, 3), tok))
    return out
