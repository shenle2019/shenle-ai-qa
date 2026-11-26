"""评测与部署模拟：分类/生成指标、偏置探针、漂移检测、可用性统计。

所有指标都手写实现，不引第三方库，保证「指标怎么算」这件事本身可测。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean


# ---------- 分类指标 ----------

def confusion(pairs: list[tuple[str, str]], positive: str) -> dict[str, int]:
    tp = sum(1 for gold, pred in pairs if gold == positive and pred == positive)
    fp = sum(1 for gold, pred in pairs if gold != positive and pred == positive)
    fn = sum(1 for gold, pred in pairs if gold == positive and pred != positive)
    tn = sum(1 for gold, pred in pairs if gold != positive and pred != positive)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall_f1(pairs: list[tuple[str, str]], positive: str) -> tuple[float, float, float]:
    c = confusion(pairs, positive)
    p = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) else 0.0
    r = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def accuracy(pairs: list[tuple[str, str]]) -> float:
    if not pairs:
        return 0.0
    return round(sum(1 for g, p in pairs if g == p) / len(pairs), 4)


# ---------- 生成指标（简化版，讲清「为什么 BLEU/ROUGE 不够」）----------

def _ngrams(text: str, n: int) -> list[tuple[str, ...]]:
    return [tuple(text[i : i + n]) for i in range(len(text) - n + 1)]


def bleu_like(candidate: str, reference: str, n: int = 2) -> float:
    """只算 n-gram 精确率，故意不做 brevity penalty，用来说明「短答案会虚高」。"""
    cand = _ngrams(candidate, n)
    ref = _ngrams(reference, n)
    if not cand or not ref:
        return 0.0
    hit = 0
    pool = list(ref)
    for g in cand:
        if g in pool:
            hit += 1
            pool.remove(g)
    return round(hit / len(cand), 4)


def rouge_l_like(candidate: str, reference: str) -> float:
    """最长公共子序列 / 参考长度，近似 ROUGE-L recall。"""
    a, b = candidate, reference
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return round(dp[len(a)][len(b)] / (len(b) or 1), 4)


# ---------- 偏置与公平 ----------

@dataclass
class Probe:
    texts: list[str]
    labels: list[str]

    def score_of(self, model) -> dict[str, float]:
        """每个分组上的平均分，用来发现「同一能力，不同人群给分不同」。"""
        buckets: dict[str, list[float]] = {}
        for text, label in zip(self.texts, self.labels):
            buckets.setdefault(label, []).append(model(text))
        return {k: round(mean(v), 4) for k, v in buckets.items()}

    def gap(self, model) -> float:
        scores = self.score_of(model)
        if not scores:
            return 0.0
        return round(max(scores.values()) - min(scores.values()), 4)


def gender_biased_scorer(text: str) -> float:
    """演示偏置：同一个能力描述，提到「她」就低 2 分。"""
    base = 8.0 if "熟练" in text else 5.0
    return base - (2.0 if "她" in text else 0.0)


def fair_scorer(text: str) -> float:
    return 8.0 if "熟练" in text else 5.0


# ---------- 漂移检测 ----------

def psi(expected: list[float], actual: list[float], bins: int = 5) -> float:
    """群体稳定性指数：<0.1 稳定，0.1–0.25 需关注，>0.25 显著漂移。"""
    if not expected or not actual:
        return 0.0
    lo = min(min(expected), min(actual))
    hi = max(max(expected), max(actual))
    if hi == lo:
        return 0.0
    width = (hi - lo) / bins
    total = 0.0
    for i in range(bins):
        low = lo + i * width
        high = low + width
        e = sum(1 for x in expected if low <= x < high or (i == bins - 1 and x == hi)) / len(expected)
        a = sum(1 for x in actual if low <= x < high or (i == bins - 1 and x == hi)) / len(actual)
        e = max(e, 1e-6)
        a = max(a, 1e-6)
        total += (a - e) * math.log(a / e)
    return round(total, 4)


# ---------- 可用性 ----------

def success_rate(results: list[bool]) -> float:
    if not results:
        return 0.0
    return round(sum(1 for r in results if r) / len(results), 4)


def p95(latencies: list[float]) -> float:
    if not latencies:
        return 0.0
    ordered = sorted(latencies)
    idx = max(math.ceil(0.95 * len(ordered)) - 1, 0)
    return round(ordered[min(idx, len(ordered) - 1)], 2)


def tokens_cost(prompt_tokens: int, completion_tokens: int, price_in: float = 0.002, price_out: float = 0.008) -> float:
    """按千 token 计价，返回元。价格是示例值，不是任何厂商的真实报价。"""
    return round(prompt_tokens / 1000 * price_in + completion_tokens / 1000 * price_out, 6)
