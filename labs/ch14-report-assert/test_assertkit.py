"""断言的测试：用坏数据证明工具箱会报错，用好数据证明它不误报。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from assertkit import (  # noqa: E402
    SoftAssert,
    assert_in_range,
    assert_iso8601,
    assert_schema,
    assert_subset,
    suggest_assertions,
)
from report import parse, render  # noqa: E402

BODY = {
    "id": 7,
    "name": "alice",
    "role": "tester",
    "created_at": "2026-11-16T08:00:00Z",
    "active": True,
}


def test_subset_accepts_extra_fields():
    assert_subset(BODY, {"id": 7, "name": "alice"})


def test_subset_reports_missing_key():
    with pytest.raises(AssertionError, match="缺少字段 email"):
        assert_subset(BODY, {"email": "a@b.c"})


def test_subset_reports_wrong_value_with_path():
    with pytest.raises(AssertionError, match="name 期望"):
        assert_subset(BODY, {"name": "bob"})


def test_subset_nested():
    payload = {"user": {"id": 1, "name": "x"}, "total": 3}
    assert_subset(payload, {"user": {"id": 1}})
    with pytest.raises(AssertionError, match=r"user\.name"):
        assert_subset(payload, {"user": {"name": "y"}})


def test_schema_types():
    assert_schema(BODY, {"id": int, "name": str, "active": bool})
    with pytest.raises(AssertionError, match="id 期望 str"):
        assert_schema(BODY, {"id": str})


def test_schema_required_flag():
    with pytest.raises(AssertionError, match="缺少必填字段 email"):
        assert_schema(BODY, {"email": str})
    assert_schema(BODY, {"email": str}, required=False)


def test_iso8601():
    assert_iso8601(BODY["created_at"])
    with pytest.raises(AssertionError):
        assert_iso8601("2026/11/16")


def test_in_range():
    assert_in_range(0.87, 0, 1, "pass_rate")
    with pytest.raises(AssertionError, match="pass_rate"):
        assert_in_range(1.2, 0, 1, "pass_rate")


def test_soft_assert_collects_all():
    soft = SoftAssert()
    soft.equal(BODY["id"], 8, "id")
    soft.equal(BODY["name"], "bob", "name")
    soft.check("role" in BODY, "缺少 role")
    assert len(soft.failures) == 2
    with pytest.raises(AssertionError) as exc:
        soft.ok()
    assert "id 期望" in str(exc.value) and "name 期望" in str(exc.value)


def test_suggest_assertions_covers_types():
    drafts = suggest_assertions(BODY)
    joined = "\n".join(drafts)
    assert "isinstance(data['id'], int)" in joined
    assert "isinstance(data['active'], bool)" in joined
    assert "assert_iso8601(data['created_at'])" in joined


XML = """<?xml version="1.0"?>
<testsuite name="pytest" tests="3" failures="1" time="1.25">
  <testcase classname="labs.t" name="a" time="0.10"/>
  <testcase classname="labs.t" name="b" time="0.90"><failure>boom</failure></testcase>
  <testcase classname="labs.t" name="c" time="0.25"/>
</testsuite>
"""


def test_report_counts_and_order(tmp_path):
    xml = tmp_path / "r.xml"
    xml.write_text(XML, encoding="utf-8")
    data = parse(xml)
    assert len(data["cases"]) == 3
    page = render(data, when="2026-11-16")
    assert "通过率" in page and "66.7%" in page
    assert page.index("labs.t::b") < page.index("labs.t::a"), "失败用例应排在最前"
