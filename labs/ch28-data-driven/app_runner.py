"""第 28 章：把用例写成数据，用一个小分发器跑。

`cases.yaml` 里的每条只描述「做什么 + 期望什么」，具体怎么点由 handlers 决定。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


@dataclass
class Case:
    id: str
    title: str
    action: str
    expect: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Result:
    case_id: str
    title: str
    ok: bool
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.case_id, "ok": self.ok, "detail": self.detail}


class CaseError(ValueError):
    pass


def load_cases(path: str | Path) -> list[Case]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    items = raw.get("cases")
    if not isinstance(items, list) or not items:
        raise CaseError("cases.yaml 里要有非空的 cases 列表")

    seen: set[str] = set()
    cases: list[Case] = []
    for index, item in enumerate(items):
        for key in ("id", "title", "action", "expect"):
            if not item.get(key):
                raise CaseError(f"第 {index + 1} 条缺少字段 {key}")
        if item["id"] in seen:
            raise CaseError(f"用例 id 重复：{item['id']}")
        seen.add(item["id"])
        cases.append(
            Case(
                id=str(item["id"]),
                title=str(item["title"]),
                action=str(item["action"]),
                expect=str(item["expect"]),
                params=dict(item.get("params") or {}),
            )
        )
    return cases


def handlers(page) -> dict[str, Callable[[Case], str]]:
    """把 action 名字映射到真正的操作。返回的字符串就是「实际看到的」。"""

    def login_ok(case: Case) -> str:
        page.tap_correct()
        return page.wait_result(case.expect, timeout=25)

    def login_bad(case: Case) -> str:
        page.tap_wrong()
        return page.wait_result(case.expect, timeout=25)

    def photo(case: Case) -> str:
        page.tap_photo()
        node = page.app.wait_for(lambda n: "网络图片" in (n.content_desc or ""), timeout=25)
        return f"{node.class_name} {node.bounds.width}x{node.bounds.height}"

    def title_visible(case: Case) -> str:
        return page.app.wait_text(case.expect, timeout=10).text

    return {"login_ok": login_ok, "login_bad": login_bad, "photo": photo, "title": title_visible}


def run_case(case: Case, page, table: dict[str, Callable[[Case], str]]) -> Result:
    handler = table.get(case.action)
    if handler is None:
        raise CaseError(f"未知 action：{case.action}")
    try:
        actual = handler(case)
    except Exception as exc:  # noqa: BLE001 - 失败要留在结果里，不能中断整批
        return Result(case.id, case.title, False, f"{type(exc).__name__}: {exc}")
    ok = case.expect in actual
    return Result(case.id, case.title, ok, "" if ok else f"期望包含 {case.expect!r}，实际 {actual[:80]!r}")


def run_all(cases: list[Case], page, table=None) -> list[Result]:
    table = table or handlers(page)
    return [run_case(case, page, table) for case in cases]


def summary(results: list[Result]) -> dict[str, Any]:
    passed = sum(1 for r in results if r.ok)
    return {"total": len(results), "passed": passed, "failed": len(results) - passed}
