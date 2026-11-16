"""第 9 章的测试：矩阵生成规则 + 五道审的判定。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matrix import coverage, gaps, generate  # noqa: E402
from prompt import BAD_SAMPLE, build_prompt, estimate_coverage, review  # noqa: E402
from spec import DIMENSIONS, SPEC  # noqa: E402


def _ep(method: str, path: str) -> dict:
    return next(e for e in SPEC["endpoints"] if e["method"] == method and e["path"] == path)


def test_every_case_has_executable_request():
    for endpoint in SPEC["endpoints"]:
        for case in generate(endpoint):
            assert {"method", "path"} <= set(case.request)
            assert case.expected["status"] in endpoint["responses"] or case.expected["status"] in (401, 404, 409, 422)


def test_create_endpoint_covers_all_applicable_dimensions():
    cases = generate(_ep("POST", "/api/users"))
    dims = {c.dimension for c in cases}
    assert {"参数", "位置", "状态", "兼容"} <= dims
    table = coverage(cases, DIMENSIONS)
    row = table["POST /api/users"]
    assert row["参数"] >= 3


def test_list_endpoint_covers_pagination_and_auth():
    cases = generate(_ep("GET", "/api/users"))
    titles = " ".join(c.title for c in cases)
    assert "size" in titles and "page" in titles
    assert any(c.expected["status"] == 401 for c in cases)


def test_required_field_missing_is_p0():
    cases = generate(_ep("POST", "/api/login"))
    missing = [c for c in cases if "缺少必填" in c.title]
    assert missing and all(c.priority == "P0" for c in missing)


def test_gaps_reports_empty_cells():
    cases = generate(_ep("POST", "/api/login"))
    holes = gaps(coverage(cases, DIMENSIONS), DIMENSIONS)
    assert ("POST /api/login", "幂等") in holes


def test_prompt_contains_schema_and_constraints():
    cases = generate(_ep("GET", "/api/users"))
    text = build_prompt(SPEC, coverage(cases, DIMENSIONS), cases)
    for keyword in ("expected 必须可判定", "严格输出 JSON", '"id"', "硬约束"):
        assert keyword in text


def test_review_drops_unfixable_cases():
    verdict = review(BAD_SAMPLE)
    dropped = {c["id"] for c in verdict["drop"]}
    assert "BAD-3" in dropped  # request 是字符串，不可执行


def test_review_flags_vague_assertions():
    verdict = review(BAD_SAMPLE)
    revised = {c["id"] for c in verdict["revise"]}
    assert "BAD-1" in revised
    assert any("无法判定" in p for c in verdict["revise"] for p in c["problems"])


def test_review_passes_the_good_case():
    verdict = review(BAD_SAMPLE)
    assert [c["id"] for c in verdict["pass"]] == ["GOOD-1"]


def test_reviewed_coverage_only_counts_passed():
    verdict = review(BAD_SAMPLE)
    counts = estimate_coverage(verdict["pass"])
    assert counts == {"状态": 1}
