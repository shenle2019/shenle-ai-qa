"""把用例当数据跑：一个处理器表 + 一个执行循环，新增用例只改 yaml。

设计取舍：
- 处理器只做「动作」，断言写在处理器里，返回结构化结果；
- 失败不抛异常，而是返回 `ok=False` + 原因，这样批量跑不会因为第一条挂掉就中断；
- 每条用例的执行结果都是可打印的，能直接拼成报告。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml
from playwright.sync_api import Page, expect

HERE = Path(__file__).resolve().parent
DEFAULT_CASES = HERE / "cases.yaml"


@dataclass
class Result:
    case_id: str
    title: str
    ok: bool
    detail: str = ""

    def __str__(self) -> str:
        mark = "PASS" if self.ok else "FAIL"
        return f"[{mark}] {self.case_id} {self.title} {self.detail}".rstrip()


def load_cases(path: Path | str = DEFAULT_CASES) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("用例文件最外层必须是列表")
    ids = [case.get("id") for case in data]
    if len(ids) != len(set(ids)):
        raise ValueError("用例 id 不能重复")
    return data


def _login(page: Page, site: str, username: str, password: str) -> None:
    page.goto(f"{site}/login")
    page.get_by_label("用户名").fill(username)
    page.get_by_label("密码").fill(password)
    page.get_by_role("button", name="登录").click()


def _ensure_login(page: Page, site: str) -> None:
    if "/login" in page.url or page.url in ("about:blank", ""):
        _login(page, site, "alice", "secret")
        page.wait_for_url("**/todos")


# --- 处理器：一个动作一个函数，签名统一 ---
def do_login(page: Page, site: str, params: dict, expect_spec: dict) -> str:
    _login(page, site, params["username"], params["password"])
    page.wait_for_load_state("load")
    if "path" in expect_spec:
        assert page.url.endswith(expect_spec["path"]), f"期望路径 {expect_spec['path']}，实际 {page.url}"
    if "error" in expect_spec:
        expect(page.get_by_test_id("error")).to_have_text(expect_spec["error"])
    if "current_user" in expect_spec:
        expect(page.get_by_test_id("current-user")).to_have_text(expect_spec["current_user"])
    return "登录流程符合预期"


def do_add_todo(page: Page, site: str, params: dict, expect_spec: dict) -> str:
    _ensure_login(page, site)
    page.goto(f"{site}/todos")
    before = page.get_by_test_id("todo-item").count()
    page.get_by_label("新任务").fill(params["title"])
    page.get_by_test_id("add-submit").click()
    page.wait_for_load_state("load")
    expect(page.get_by_test_id("todo-item")).to_have_count(before + 1)
    expect(page.get_by_test_id("todo-list")).to_contain_text(expect_spec["contains"])
    return f"条数 {before} -> {before + 1}"


def do_search(page: Page, site: str, params: dict, expect_spec: dict) -> str:
    _ensure_login(page, site)
    page.goto(f"{site}/search")
    page.get_by_label("关键词").fill(params["query"])
    page.get_by_test_id("search-submit").click()
    page.wait_for_load_state("load")
    expect(page.get_by_test_id("result-count")).to_have_text(f"共 {expect_spec['count']} 条")
    if expect_spec["count"] == 0:
        expect(page.get_by_test_id("empty")).to_have_text(expect_spec["empty_text"])
    else:
        expect(page.get_by_test_id("result-item")).to_have_count(expect_spec["count"])
    return f"命中 {expect_spec['count']} 条"


def do_pick_row(page: Page, site: str, params: dict, expect_spec: dict) -> str:
    _ensure_login(page, site)
    page.goto(f"{site}/table")
    box = page.get_by_test_id("pick").nth(params["index"])
    box.check()
    assert box.is_checked() is expect_spec["checked"], "勾选状态与期望不一致"
    return f"第 {params['index'] + 1} 行勾选成功"


def do_open_profile(page: Page, site: str, params: dict, expect_spec: dict) -> str:
    _ensure_login(page, site)
    page.goto(f"{site}/profile")
    expect(page.get_by_test_id("profile-name")).to_have_text(expect_spec["name"])
    expect(page.get_by_test_id("profile-role")).to_have_text(expect_spec["role"])
    return "资料字段正确"


def do_open_anonymous(page: Page, site: str, params: dict, expect_spec: dict) -> str:
    # 前面几条用例可能已经登录过，这里显式清掉 cookie 才是真正的「未登录」
    page.context.clear_cookies()
    page.goto(f"{site}/todos")
    page.wait_for_url("**/login")
    assert page.url.endswith(expect_spec["path"]), f"期望 {expect_spec['path']}，实际 {page.url}"
    return "未登录被拦截"


HANDLERS: dict[str, Callable[[Page, str, dict, dict], str]] = {
    "login": do_login,
    "add_todo": do_add_todo,
    "search": do_search,
    "pick_row": do_pick_row,
    "open_profile": do_open_profile,
    "open_anonymous": do_open_anonymous,
}


def run_case(page: Page, site: str, case: dict[str, Any]) -> Result:
    action = case.get("action")
    handler = HANDLERS.get(action)
    if handler is None:
        raise ValueError(f"用例 {case.get('id')!r} 的 action={action!r} 没有对应处理器，可选：{sorted(HANDLERS)}")
    try:
        detail = handler(page, site, case.get("params") or {}, case.get("expect") or {})
    except Exception as exc:  # noqa: BLE001 - 批量执行要把失败收进结果
        return Result(case["id"], case.get("title", ""), False, f"{type(exc).__name__}: {exc}")
    return Result(case["id"], case.get("title", ""), True, detail)


def run_all(page: Page, site: str, cases: list[dict[str, Any]]) -> list[Result]:
    results = []
    for case in cases:
        results.append(run_case(page, site, case))
    return results


def summary(results: list[Result]) -> dict[str, int]:
    passed = sum(1 for r in results if r.ok)
    return {"total": len(results), "passed": passed, "failed": len(results) - passed}
