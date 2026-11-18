"""用例执行器：读 YAML、按 action 分派、收集结果。

分层：config（环境与用例）→ runner（调度）→ pages（动作）→ 报告。
用例里不出现选择器，也不出现 URL 拼接，换环境只改 config。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from playwright.sync_api import expect

from fw_pages import LoginPage, SearchPage, TodoPage


class ConfigError(ValueError):
    """配置文件不合法。"""


@dataclass
class Result:
    case_id: str
    title: str
    ok: bool
    detail: str
    duration_ms: int = 0


@dataclass
class Report:
    env: str
    base_url: str
    results: list[Result] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for item in self.results if item.ok)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def ok(self) -> bool:
        return self.failed == 0


def load_config(path: Path | str) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError("配置文件必须是映射")
    envs = data.get("envs")
    if not isinstance(envs, dict) or not envs:
        raise ConfigError("envs 不能为空")
    default = data.get("default_env")
    if default not in envs:
        raise ConfigError(f"default_env {default!r} 不在 envs 里")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ConfigError("cases 不能为空")
    seen = set()
    for case in cases:
        case_id = case.get("id")
        if not case_id:
            raise ConfigError("每条用例都要有 id")
        if case_id in seen:
            raise ConfigError(f"用例 id 重复：{case_id}")
        seen.add(case_id)
        if case.get("action") not in ACTIONS:
            raise ConfigError(f"用例 {case_id} 的 action 未知：{case.get('action')!r}")
    return data


def pick_env(config: dict, env: str | None) -> tuple[str, dict]:
    name = env or config["default_env"]
    envs = config["envs"]
    if name not in envs:
        raise ConfigError(f"环境 {name!r} 不存在，可选：{sorted(envs)}")
    return name, envs[name]


def _ensure_login(page, base_url: str) -> None:
    page.goto(base_url.rstrip("/") + "/login")
    LoginPage(page, base_url).submit("alice", "secret")
    page.wait_for_url("**/todos")


def do_login(page, base_url: str, params: dict, expect_spec: dict) -> str:
    login = LoginPage(page, base_url).open()
    login.submit(params["username"], params["password"])
    expected_path = expect_spec.get("path")
    if expected_path:
        page.wait_for_url(f"**{expected_path}")
    error_text = expect_spec.get("error")
    if error_text:
        expect(login.error).to_contain_text(error_text)
        return "停在登录页并提示错误"
    TodoPage(page, base_url).expect_user(expect_spec["user"])
    return "登录成功"


def do_add_todo(page, base_url: str, params: dict, expect_spec: dict) -> str:
    if params.get("login"):
        _ensure_login(page, base_url)
    todo = TodoPage(page, base_url).open().add(params["title"])
    expect(todo.page.get_by_test_id("todo-list")).to_contain_text(expect_spec["contains"])
    return f"列表里有「{params['title']}」"


def do_search(page, base_url: str, params: dict, expect_spec: dict) -> str:
    if params.get("login"):
        _ensure_login(page, base_url)
    search = SearchPage(page, base_url).search(params["keyword"])
    count = search.count()
    if count < expect_spec.get("min_results", 0):
        raise AssertionError(f"只命中 {count} 条")
    return f"命中 {count} 条"


def do_guard(page, base_url: str, params: dict, expect_spec: dict) -> str:
    page.context.clear_cookies()
    page.goto(base_url.rstrip("/") + "/todos")
    page.wait_for_url(f"**{expect_spec['path']}")
    return "被拦截回登录页"


HANDLERS = {
    "login": do_login,
    "add_todo": do_add_todo,
    "search": do_search,
    "guard": do_guard,
}
ACTIONS = set(HANDLERS)


def run_case(page, base_url: str, case: dict) -> Result:
    from time import perf_counter

    start = perf_counter()
    try:
        detail = HANDLERS[case["action"]](page, base_url, case.get("params") or {}, case.get("expect") or {})
        ok = True
    except Exception as exc:  # noqa: BLE001
        ok = False
        detail = f"{type(exc).__name__}: {str(exc).splitlines()[0][:200]}"
    finally:
        page.context.clear_cookies()
    return Result(case["id"], case.get("title", ""), ok, detail, int((perf_counter() - start) * 1000))


def run(page, config: dict, env: str | None = None, only: list[str] | None = None, base_url: str | None = None) -> Report:
    name, env_conf = pick_env(config, env)
    url = base_url or env_conf["base_url"]
    cases = config["cases"]
    if only:
        cases = [case for case in cases if any(token in case["id"] for token in only)]
        if not cases:
            raise ConfigError(f"没有用例匹配 {only}")
    report = Report(env=name, base_url=url)
    for case in cases:
        report.results.append(run_case(page, url, case))
    return report
