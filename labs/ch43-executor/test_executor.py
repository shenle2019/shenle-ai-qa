import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from executor import CaseResult, CaseError, pick, render, run_case, summarise  # noqa: E402


class FakeSession:
    def __init__(self, payload=None, status=200):
        self.payload = payload or {"code": 100, "data": {"id": 7, "name": "alice"}}
        self.status = status
        self.calls = []

    def request(self, method, url, json=None, headers=None, timeout=None):
        self.calls.append((method, url, json))
        payload, status = self.payload, self.status

        class R:
            status_code = status
            headers = {"content-type": "application/json"}

            def json(self):
                return payload

        return R()


CASE = {
    "id": "login-and-read",
    "steps": [
        {"kw": "http", "method": "POST", "path": "/api/login", "body": {"user": "alice"}, "expect": 200},
        {"kw": "status", "expected": 200},
        {"kw": "extract", "path": "data.id", "name": "uid"},
        {"kw": "json", "path": "code", "equals": 100},
        {"kw": "json", "path": "data.name", "equals": "${who}"},
    ],
}


def test_render_substitutes_and_raises_on_missing():
    assert render("${a}-${b}", {"a": 1, "b": "x"}) == "1-x"
    with pytest.raises(CaseError, match="没有值"):
        render("${nope}", {})


def test_pick_walks_dict_and_list():
    assert pick({"a": {"b": [1, {"c": 2}]}}, "a.b.1.c") == 2
    assert pick({"a": 1}, "a.b") is None


def test_run_case_passes_and_records_steps():
    result = run_case(CASE, FakeSession(), "http://x", {"who": "alice"})
    assert isinstance(result, CaseResult) and result.ok
    assert [s.keyword for s in result.steps] == ["http", "status", "extract", "json", "json"]


def test_http_expectation_failure_stops_the_case():
    result = run_case({"id": "c", "steps": [{"kw": "http", "method": "GET", "path": "/a", "expect": 201}]}, FakeSession(), "http://x")
    assert not result.ok
    assert "期望 201" in result.error
    assert len(result.steps) == 1


def test_unknown_keyword_is_reported():
    result = run_case({"id": "c", "steps": [{"kw": "teleport"}]}, FakeSession(), "http://x")
    assert not result.ok and "未知关键字" in result.error


def test_json_missing_path_fails():
    result = run_case({"id": "c", "steps": [{"kw": "json", "path": "data.nope"}]}, FakeSession(), "http://x")
    assert not result.ok and "没有 data.nope" in result.error


def test_extract_feeds_next_step():
    case = {
        "id": "c",
        "steps": [
            {"kw": "http", "method": "GET", "path": "/u"},
            {"kw": "extract", "path": "data.id", "name": "uid"},
            {"kw": "http", "method": "GET", "path": "/u/${uid}", "expect": 200},
        ],
    }
    session = FakeSession()
    result = run_case(case, session, "http://x")
    assert result.ok
    assert session.calls[-1][1] == "http://x/u/7"


def test_summarise_counts():
    good = run_case(CASE, FakeSession(), "http://x", {"who": "alice"})
    bad = run_case({"id": "b", "steps": [{"kw": "teleport"}]}, FakeSession(), "http://x")
    assert summarise([good, bad]) == {"total": 2, "passed": 1, "failed": 1}
