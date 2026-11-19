"""第 30 章：用 logcat 判断「是应用崩了，还是用例错了」。

先把日志切成行，再按优先级挑出真正需要人看的几条。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

FATAL = re.compile(r"FATAL EXCEPTION|AndroidRuntime: Process: (?P<process>[\w.]+)")
ANR = re.compile(r"ANR in (?P<process>[\w.]+)")
CRASH_TYPE = re.compile(r"^\s*(?P<type>[A-Za-z0-9_.$]+(?:Exception|Error))(?::\s*(?P<message>.*))?$")


@dataclass
class Crash:
    kind: str
    process: str
    summary: str

    def as_line(self) -> str:
        return f"{self.kind} {self.process or '?'}：{self.summary}"


def lines_of(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def of_level(text: str, level: str = "E") -> list[str]:
    """取某一级别的日志（logcat 的行格式是 `时间 级别/标签: 内容`）。"""
    pattern = re.compile(rf"\s{level}/\w+\s*\(")
    return [line for line in lines_of(text) if pattern.search(line) or f" {level} " in line]


def find_crashes(text: str) -> list[Crash]:
    """找 FATAL EXCEPTION 与 ANR，顺带把异常类型和首行消息带上。"""
    found: list[Crash] = []
    rows = lines_of(text)
    for index, line in enumerate(rows):
        if "FATAL EXCEPTION" in line:
            process = ""
            for follow in rows[index : index + 6]:
                match = FATAL.search(follow)
                if match and match.group("process"):
                    process = match.group("process")
                    break
            summary = "未知异常"
            for follow in rows[index : index + 8]:
                match = CRASH_TYPE.match(follow.split("AndroidRuntime:")[-1].strip())
                if match:
                    summary = match.group("type")
                    if match.group("message"):
                        summary += f"：{match.group('message').strip()}"
                    break
            found.append(Crash("CRASH", process, summary))
        elif "ANR in" in line:
            match = ANR.search(line)
            found.append(Crash("ANR", match.group("process") if match else "", "主线程被阻塞"))
    return found


def errors_related_to(text: str, package: str) -> list[str]:
    """只看某个包的错误行，过滤掉系统噪声。"""
    return [line for line in of_level(text, "E") if package in line]


def digest(text: str, package: str = "", *, limit: int = 5) -> str:
    """给失败用例附一段人能读的日志摘要。"""
    parts: list[str] = []
    crashes = find_crashes(text)
    for crash in crashes[:limit]:
        parts.append(crash.as_line())
    if not crashes:
        noisy = errors_related_to(text, package) if package else []
        if not noisy:
            noisy = of_level(text, "E")
        parts.extend(noisy[:limit])
    return "\n".join(parts[:limit]) or "日志里没有异常"
