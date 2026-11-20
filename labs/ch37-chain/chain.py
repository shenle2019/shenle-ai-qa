"""第 37 章：全链路压测的两件事——流量打标、数据隔离。

- 打标：压测流量带上标记（header/上下文），一路透传到下游，便于限流、隔离与清理
- 隔离：压测数据用统一前缀，避免污染真实数据；跑完按前缀批量清理
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

__all__ = ["Traffic", "is_shadow", "make_prefix", "isolated", "Plan", "check_isolation"]


@dataclass
class Traffic:
    """一条请求的上下文：打标 + 数据前缀，随调用链透传。"""

    shadow: bool = False
    prefix: str = ""
    trace: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    headers: dict[str, str] = field(default_factory=dict)

    def tag(self) -> dict[str, str]:
        return {**self.headers, "X-Shadow": "1" if self.shadow else "0", "X-Data-Prefix": self.prefix}


SHADOW_HEADERS = {"x-shadow": "1", "x-pressure-test": "1", "x-env": "perf"}


def is_shadow(headers: dict[str, str]) -> bool:
    """任一约定 header 命中即视为压测流量；大小写不敏感。"""
    lowered = {key.lower(): str(value) for key, value in headers.items()}
    return any(lowered.get(key) == value for key, value in SHADOW_HEADERS.items())


def make_prefix(run_id: str) -> str:
    if not run_id or not run_id.strip():
        raise ValueError("run_id 不能为空")
    return f"qa_{run_id.strip()}_"


def isolated(value: str, prefix: str) -> bool:
    if not prefix:
        raise ValueError("prefix 不能为空")
    return value.startswith(prefix)


@dataclass
class Plan:
    """一个压测计划：链路步骤 + 每步是否允许写。"""

    name: str
    steps: list[tuple[str, str]]  # (名称, 读/写)
    run_id: str
    shadow: bool = True

    def traffic(self) -> Traffic:
        return Traffic(shadow=self.shadow, prefix=make_prefix(self.run_id))

    def writes(self) -> list[str]:
        return [name for name, kind in self.steps if kind == "write"]

    def validate(self) -> list[str]:
        problems = []
        if not self.steps:
            problems.append("计划里没有步骤")
        if not self.run_id.strip():
            problems.append("缺少 run_id")
        if self.shadow and not self.writes():
            problems.append("影子流量没有写步骤，等于只读压测")
        return problems


def check_isolation(values: list[str], prefix: str) -> dict:
    """检查一批数据是否都带前缀，返回漏网清单。"""
    leaked = [value for value in values if not isolated(value, prefix)]
    return {"total": len(values), "isolated": len(values) - len(leaked), "leaked": leaked}
