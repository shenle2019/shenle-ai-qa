"""生成结果的「落地执行」：把校验过的步骤在真浏览器里跑一遍。

只支持五个动作，跑完返回每条用例的结论。校验通过 ≠ 能跑通，所以这一步不能省。
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from validate import CaseError


def execute(page: Page, base_url: str, steps: list[dict]) -> None:
    for index, step in enumerate(steps, start=1):
        action = step["action"]
        if action == "goto":
            page.goto(base_url.rstrip("/") + step["path"])
        elif action == "fill":
            page.get_by_test_id(step["testid"]).fill(step["value"])
        elif action == "click":
            page.get_by_test_id(step["testid"]).click()
        elif action == "expect_text":
            expect(page.get_by_test_id(step["testid"])).to_contain_text(step["value"])
        elif action == "expect_visible":
            expect(page.get_by_test_id(step["testid"])).to_be_visible()
        else:  # pragma: no cover - 已经被 validate 拦住
            raise CaseError(f"第 {index} 步动作未知：{action}")


def run_cases(page: Page, base_url: str, cases: list[dict]) -> list[dict]:
    report = []
    for case in cases:
        try:
            execute(page, base_url, case["steps"])
            report.append({"title": case["title"], "ok": True, "detail": "通过"})
        except Exception as exc:  # noqa: BLE001
            report.append({"title": case["title"], "ok": False, "detail": f"{type(exc).__name__}: {exc}"})
        finally:
            page.context.clear_cookies()
    return report
