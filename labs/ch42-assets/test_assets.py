import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assets import SpecError, parse_spec, to_markdown, validate  # noqa: E402

SPEC = {
    "base_url": "http://127.0.0.1:8010",
    "paths": {
        "/api/users": {
            "get": {"summary": "用户列表", "params": ["page"]},
            "post": {"summary": "建用户", "body": {"name": "string"}},
        },
        "/api/users/{id}": {"get": {"summary": "用户详情", "params": ["id"]}},
    },
}


def test_parse_returns_sorted_endpoints():
    base, items = parse_spec(SPEC)
    assert base == "http://127.0.0.1:8010"
    assert [i.key for i in items] == ["GET /api/users", "POST /api/users", "GET /api/users/{id}"]


def test_parse_rejects_bad_base_url():
    with pytest.raises(SpecError, match="base_url"):
        parse_spec({"base_url": "127.0.0.1", "paths": {}})


def test_parse_rejects_unknown_method():
    with pytest.raises(SpecError, match="不支持的方法"):
        parse_spec({"base_url": "http://x", "paths": {"/a": {"fetch": {}}}})


def test_parse_rejects_relative_path():
    with pytest.raises(SpecError, match="必须"):
        parse_spec({"base_url": "http://x", "paths": {"api/a": {}}})


def test_validate_clean_spec_passes():
    _, items = parse_spec(SPEC)
    assert validate(items) == []


def test_validate_flags_missing_body_and_params():
    _, items = parse_spec(
        {
            "base_url": "http://x",
            "paths": {
                "/api/w": {"post": {"summary": "写"}},
                "/api/{id}": {"get": {"summary": "详情"}},
            },
        }
    )
    problems = validate(items)
    assert any("没有 body" in p for p in problems)
    assert any("没有声明 params" in p for p in problems)


def test_validate_flags_duplicate_and_missing_summary():
    _, items = parse_spec({"base_url": "http://x", "paths": {"/a": {"get": {}}}})
    items.append(items[0])
    problems = validate(items)
    assert any("重复接口" in p for p in problems)
    assert any("缺少 summary" in p for p in problems)


def test_markdown_lists_rows():
    base, items = parse_spec(SPEC)
    text = to_markdown(items, base)
    assert "| GET | `/api/users` | 用户列表 |" in text
    assert "接口清单（3 个" in text
