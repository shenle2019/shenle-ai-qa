"""第 28 章：数据驱动。离线覆盖加载与分发，真机跑一遍全量。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "labs" / "ch26-page-object"))

from login_page import LoginDemoPage  # noqa: E402

from app_runner import Case, CaseError, load_cases, run_all, run_case, summary  # noqa: E402

CASES = Path(__file__).resolve().parent / "cases.yaml"


def test_load_cases_from_yaml() -> None:
    cases = load_cases(CASES)
    assert [c.id for c in cases] == ["login-correct", "login-wrong", "load-photo", "title-visible"]
    assert cases[0].action == "login_ok"


def test_load_cases_rejects_duplicate_id(tmp_path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "cases:\n  - {id: a, title: t, action: title, expect: x}\n  - {id: a, title: t, action: title, expect: x}\n",
        encoding="utf-8",
    )
    with pytest.raises(CaseError):
        load_cases(bad)


def test_load_cases_rejects_missing_field(tmp_path) -> None:
    bad = tmp_path / "bad2.yaml"
    bad.write_text("cases:\n  - {id: a, title: t}\n", encoding="utf-8")
    with pytest.raises(CaseError):
        load_cases(bad)


def test_run_case_unknown_action() -> None:
    case = Case("x", "t", "nope", "y")
    with pytest.raises(CaseError):
        run_case(case, page=None, table={"login_ok": lambda c: "ok"})


def test_run_case_captures_exception() -> None:
    def boom(case):
        raise RuntimeError("设备掉了")

    result = run_case(Case("x", "t", "boom", "y"), page=None, table={"boom": boom})
    assert result.ok is False
    assert "设备掉了" in result.detail


def test_run_case_reports_mismatch() -> None:
    result = run_case(
        Case("x", "t", "ok", "登录成功"),
        page=None,
        table={"ok": lambda c: "HTTP 500 服务器错误"},
    )
    assert result.ok is False
    assert "登录成功" in result.detail


def test_summary_counts() -> None:
    results = [
        run_case(Case("a", "t", "yes", "ok"), None, {"yes": lambda c: "ok"}),
        run_case(Case("b", "t", "no", "ok"), None, {"no": lambda c: "bad"}),
    ]
    assert summary(results) == {"total": 2, "passed": 1, "failed": 1}


@pytest.mark.device
def test_all_cases_pass_on_device(login_app) -> None:
    page = LoginDemoPage(login_app)
    results = run_all(load_cases(CASES), page)
    stats = summary(results)
    assert stats["failed"] == 0, [r.as_dict() for r in results if not r.ok]
    assert stats["total"] == 4
