"""断言工具箱：断言契约，不断言实现。"""

from __future__ import annotations

import re
from typing import Any

ISO8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def assert_subset(actual: dict, expected: dict, path: str = "") -> None:
    """只要求 actual 包含 expected 的键值，允许多余字段。"""
    for key, want in expected.items():
        here = f"{path}.{key}" if path else key
        assert key in actual, f"缺少字段 {here}"
        got = actual[key]
        if isinstance(want, dict):
            assert isinstance(got, dict), f"{here} 应该是对象，实际 {type(got).__name__}"
            assert_subset(got, want, here)
        else:
            assert got == want, f"{here} 期望 {want!r}，实际 {got!r}"


def assert_schema(obj: dict, schema: dict[str, type], *, required: bool = True) -> None:
    for key, typ in schema.items():
        if key not in obj:
            assert not required, f"缺少必填字段 {key}"
            continue
        assert isinstance(obj[key], typ), f"{key} 期望 {typ.__name__}，实际 {type(obj[key]).__name__}"


def assert_iso8601(value: str, field: str = "time") -> None:
    assert isinstance(value, str) and ISO8601.match(value), f"{field} 不是 ISO8601: {value!r}"


def assert_in_range(value: float, low: float, high: float, field: str = "value") -> None:
    assert low <= value <= high, f"{field} 期望在 [{low}, {high}]，实际 {value}"


class SoftAssert:
    """收集多条失败，最后一次性报出来。"""

    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, cond: bool, msg: str) -> None:
        if not cond:
            self.failures.append(msg)

    def equal(self, got: Any, want: Any, field: str) -> None:
        self.check(got == want, f"{field} 期望 {want!r}，实际 {got!r}")

    def ok(self) -> None:
        if self.failures:
            raise AssertionError("；".join(self.failures))


def suggest_assertions(body: dict) -> list[str]:
    """从一份真实响应体推断断言草稿——只是草稿，必须人审。"""
    out: list[str] = []
    for key, value in body.items():
        if isinstance(value, bool):
            out.append(f"assert isinstance(data[{key!r}], bool)")
        elif isinstance(value, int):
            out.append(f"assert isinstance(data[{key!r}], int)")
        elif isinstance(value, float):
            out.append(f"assert isinstance(data[{key!r}], float)")
        elif isinstance(value, str) and ISO8601.match(value):
            out.append(f"assert_iso8601(data[{key!r}])")
        elif isinstance(value, str):
            out.append(f"assert isinstance(data[{key!r}], str)")
        elif isinstance(value, list):
            out.append(f"assert isinstance(data[{key!r}], list)")
        elif isinstance(value, dict):
            out.append(f"assert isinstance(data[{key!r}], dict)")
    return out
