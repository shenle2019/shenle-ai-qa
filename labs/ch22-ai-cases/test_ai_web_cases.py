"""第 22 章：用 AI 生成 Web 用例（生成 → 校验 → 真跑）。

线上调用默认跳过：没有 `DEEPSEEK_API_KEY` 就不跑联网用例。
"""

from __future__ import annotations

import json

import pytest

from execute import run_cases
from llm import DeepSeekClient, FakeClient, LLMError
from web_prompt import build_messages, build_prompt
from snapshot import render, snapshot
from validate import CaseError, extract_json, known_testids, validate_cases, validate_steps


GOOD_REPLY = """好的，下面是生成的用例：
```json
{
  "cases": [
    {
      "title": "登录后能看到当前用户",
      "steps": [
        {"action": "goto", "path": "/login"},
        {"action": "fill", "testid": "username", "value": "alice"},
        {"action": "fill", "testid": "password", "value": "secret"},
        {"action": "click", "testid": "login-submit"},
        {"action": "expect_text", "testid": "current-user", "value": "alice"}
      ],
      "expected": "跳转到待办页并显示 alice"
    },
    {
      "title": "密码错误时停在登录页",
      "steps": [
        {"action": "goto", "path": "/login"},
        {"action": "fill", "testid": "username", "value": "alice"},
        {"action": "fill", "testid": "password", "value": "wrong"},
        {"action": "click", "testid": "login-submit"},
        {"action": "expect_visible", "testid": "error"}
      ],
      "expected": "显示用户名或密码错误"
    }
  ]
}
```
这两条覆盖了成功与失败路径。"""


def test_snapshot_lists_real_controls(page, site):
    page.goto(f"{site}/login")
    snap = snapshot(page)
    assert snap["url"].endswith("/login")
    testids = known_testids(snap)
    assert {"username", "password", "login-submit"} <= testids


def test_render_is_compact_and_readable(page, site):
    page.goto(f"{site}/login")
    text = render(snapshot(page))
    assert "testid=login-submit" in text
    assert len(text.splitlines()) < 30


def test_prompt_contains_contract_and_snapshot(page, site):
    page.goto(f"{site}/login")
    messages = build_messages(snapshot(page), "验证登录成功与失败")
    assert messages[0]["role"] == "system"
    assert "data-testid" in messages[0]["content"]
    prompt = build_prompt(snapshot(page), "验证登录成功与失败")
    assert '"cases"' in prompt and "goto / fill / click" in messages[0]["content"]


def test_parse_tolerates_fences_and_chatter():
    data = extract_json(GOOD_REPLY)
    assert len(data["cases"]) == 2


def test_validate_rejects_unknown_action(page, site):
    page.goto(f"{site}/login")
    snap = snapshot(page)
    bad = json.dumps({"cases": [{"title": "x", "steps": [{"action": "hover", "testid": "username"}], "expected": ""}]})
    with pytest.raises(CaseError) as err:
        validate_cases(bad, snap)
    assert "白名单" in str(err.value)


def test_validate_rejects_invented_testid(page, site):
    page.goto(f"{site}/login")
    snap = snapshot(page)
    bad = json.dumps({"cases": [{"title": "x", "steps": [{"action": "click", "testid": "not-here"}], "expected": ""}]})
    with pytest.raises(CaseError) as err:
        validate_cases(bad, snap)
    assert "没在页面快照里出现过" in str(err.value)


def test_validate_steps_requires_value():
    with pytest.raises(CaseError):
        validate_steps([{"action": "fill", "testid": "username"}], {"username"}, "t")


def test_fake_client_end_to_end_runs_on_real_page(page, site):
    page.goto(f"{site}/login")
    snap = snapshot(page)
    client = FakeClient([GOOD_REPLY])
    reply = client.complete(build_messages(snap, "验证登录"))
    cases = validate_cases(reply, snap)
    report = run_cases(page, site, cases)
    assert [item["ok"] for item in report] == [True, True], report
    assert client.calls and "控件" in client.calls[0][1]["content"]


def test_failed_generation_is_reported_not_raised(page, site):
    page.goto(f"{site}/login")
    snap = snapshot(page)
    broken = GOOD_REPLY.replace('"testid": "current-user"', '"testid": "error-banner"')
    cases = validate_cases(broken, snap)
    report = run_cases(page, site, cases)
    assert report[0]["ok"] is False
    assert "Timeout" in report[0]["detail"] or "locator" in report[0]["detail"].lower()


def test_deepseek_client_requires_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(LLMError):
        DeepSeekClient().complete([{"role": "user", "content": "hi"}])
