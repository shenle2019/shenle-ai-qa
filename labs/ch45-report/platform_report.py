"""第 45 章：平台收口——汇总执行结果、按门槛给结论、输出 Markdown 与 JUnit。"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape


@dataclass
class Outcome:
    case_id: str
    ok: bool
    duration_ms: float = 0.0
    error: str = ""

    @property
    def status(self) -> str:
        return "passed" if self.ok else "failed"


@dataclass
class Report:
    env: str
    outcomes: list = field(default_factory=list)
    thresholds: dict = field(default_factory=lambda: {"pass_rate": 0.95})

    @property
    def total(self) -> int:
        return len(self.outcomes)

    @property
    def passed(self) -> int:
        return sum(1 for item in self.outcomes if item.ok)

    @property
    def pass_rate(self) -> float:
        return 1.0 if self.total == 0 else round(self.passed / self.total, 4)

    @property
    def slowest(self) -> list:
        return sorted(self.outcomes, key=lambda item: item.duration_ms, reverse=True)[:3]

    def gate(self) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        limit = self.thresholds.get("pass_rate", 0)
        if self.pass_rate < limit:
            reasons.append(f"通过率 {self.pass_rate} 低于门槛 {limit}")
        max_ms = self.thresholds.get("max_duration_ms")
        if max_ms:
            slow = [item.case_id for item in self.outcomes if item.duration_ms > max_ms]
            if slow:
                reasons.append(f"超时用例：{', '.join(slow)}")
        return (not reasons, reasons)

    def to_markdown(self) -> str:
        lines = [
            f"# 执行报告（{self.env}）",
            "",
            f"- 用例数：{self.total}",
            f"- 通过：{self.passed}",
            f"- 通过率：{self.pass_rate}",
            "",
            "| 用例 | 结果 | 耗时(ms) | 说明 |",
            "| --- | --- | --- | --- |",
        ]
        lines += [f"| {item.case_id} | {item.status} | {item.duration_ms} | {item.error or '-'} |" for item in self.outcomes]
        ok, reasons = self.gate()
        lines += ["", "## 结论", "", "通过" if ok else "未通过"]
        if reasons:
            lines += ["", *[f"- {reason}" for reason in reasons]]
        return "\n".join(lines) + "\n"

    def to_junit(self) -> str:
        failures = sum(1 for item in self.outcomes if not item.ok)
        head = f'<testsuite name="{escape(self.env)}" tests="{self.total}" failures="{failures}">'
        body = []
        for item in self.outcomes:
            head_case = f'  <testcase name="{escape(item.case_id)}" time="{item.duration_ms / 1000:.3f}"'
            if item.ok:
                body.append(head_case + "/>")
            else:
                body.append(head_case + f'><failure message="{escape(item.error)}"/></testcase>')
        return "\n".join([head, *body, "</testsuite>"]) + "\n"
