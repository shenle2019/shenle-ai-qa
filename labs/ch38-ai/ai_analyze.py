"""第 38 章：把 AI 用在该用的地方——异常检测 + 日志聚类 + 提示词。

不用模型也能做的：滚动 z-score 找毛刺、日志模板聚类。
用模型做的：把「结构化证据」写成自然语言结论（本章用 FakeClient 演示，真调用走 DeepSeek）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Callable

__all__ = ["Anomaly", "detect_anomalies", "normalise", "cluster_logs", "build_prompt", "explain", "FakeClient"]

DIGITS = re.compile(r"\d+")
HEX = re.compile(r"\b[0-9a-f]{8,}\b", re.I)
UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)


@dataclass
class Anomaly:
    index: int
    value: float
    score: float
    kind: str = "spike"


def detect_anomalies(series: list[float], window: int = 5, threshold: float = 3.0) -> list[Anomaly]:
    """滚动窗口 z-score；窗口内标准差为 0 时跳过（避免除零）。"""
    hits: list[Anomaly] = []
    for index, value in enumerate(series):
        if index < window:
            continue
        recent = series[index - window : index]
        sigma = pstdev(recent) if len(recent) > 1 else 0.0
        if sigma == 0:
            continue
        score = (value - mean(recent)) / sigma
        if abs(score) >= threshold:
            hits.append(Anomaly(index=index, value=value, score=round(score, 2), kind="spike" if score > 0 else "drop"))
    return hits


def normalise(line: str) -> str:
    """把一行日志压成模板：UUID/十六进制/数字都替换成占位符。"""
    text = UUID.sub("<uuid>", line)
    text = HEX.sub("<hex>", text)
    text = DIGITS.sub("<n>", text)
    return text.strip()


def cluster_logs(lines: list[str], top: int = 5) -> list[dict]:
    counts: dict[str, int] = {}
    samples: dict[str, str] = {}
    for line in lines:
        key = normalise(line)
        counts[key] = counts.get(key, 0) + 1
        samples.setdefault(key, line)
    ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:top]
    return [{"template": key, "count": count, "sample": samples[key]} for key, count in ordered]


def build_prompt(report: dict) -> str:
    return (
        "你是性能分析助手。下面是压测结果，请只用这些数据回答：\n"
        f"- 平台期并发：{report.get('plateau_at')}\n"
        f"- 峰值 TPS：{report.get('peak_tps')}\n"
        f"- 最差 P95：{report.get('worst_p95')}ms\n"
        f"- 最高错误率：{report.get('max_error_rate')}\n"
        f"- 异常点：{report.get('anomalies', [])}\n"
        "要求：先给一句结论，再给两条依据（引用具体数字），最后给一条下一步动作；不超过 120 字。"
    )


class FakeClient:
    """测试用：记录调用、返回固定文本，避免依赖网络与密钥。"""

    def __init__(self, reply: str = "结论：瓶颈在连接池。依据：in_flight 等于并发且 pool_wait 上升。下一步：扩容池并复测。") -> None:
        self.reply = reply
        self.calls: list[str] = []

    def complete(self, prompt: str, **_: object) -> str:
        self.calls.append(prompt)
        return self.reply


def explain(report: dict, client: Callable[..., str] | FakeClient) -> str:
    prompt = build_prompt(report)
    if isinstance(client, FakeClient):
        return client.complete(prompt)
    return client(prompt)  # type: ignore[operator]
