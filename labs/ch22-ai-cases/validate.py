"""把模型吐出来的东西变成「能跑或能报错」的步骤。

三条原则：
- 解析要宽松（模型爱加 ```json 围栏、爱在前后加一句客套话）；
- 校验要严格（动作白名单、字段必填、testid 必须在快照里出现过）；
- 报错要具体（哪条用例、第几步、哪个字段），否则调不动。
"""

from __future__ import annotations

import json
import re

ACTIONS = {"goto", "fill", "click", "expect_text", "expect_visible"}
# 操作类动作必须落在「当前页面上已经存在」的元素上
NEEDS_TESTID = {"fill", "click"}
# 断言类动作允许指向「操作之后才出现的元素」，只要求写了 testid
EXPECT_TESTID = {"expect_text", "expect_visible"}
NEEDS_VALUE = {"fill", "expect_text"}


class CaseError(ValueError):
    """生成的用例不合法。"""


FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def extract_json(text: str) -> dict:
    match = FENCE.search(text)
    payload = match.group(1) if match else text
    payload = payload.strip()
    start = payload.find("{")
    end = payload.rfind("}")
    if start == -1 or end == -1:
        raise CaseError("响应里没有 JSON 对象")
    try:
        data = json.loads(payload[start : end + 1])
    except json.JSONDecodeError as exc:
        raise CaseError(f"JSON 解析失败：{exc}") from exc
    if not isinstance(data, dict) or "cases" not in data:
        raise CaseError("缺少 cases 字段")
    return data


def known_testids(snap: dict) -> set[str]:
    return {item["testid"] for item in snap.get("controls", []) if item.get("testid")}


def validate_steps(steps: list, allowed_testids: set[str], case_title: str = "") -> list[dict]:
    if not isinstance(steps, list) or not steps:
        raise CaseError(f"「{case_title}」没有 steps")
    cleaned: list[dict] = []
    for index, raw in enumerate(steps, start=1):
        where = f"「{case_title}」第 {index} 步"
        if not isinstance(raw, dict):
            raise CaseError(f"{where} 不是对象")
        action = raw.get("action")
        if action not in ACTIONS:
            raise CaseError(f"{where} 动作 {action!r} 不在白名单 {sorted(ACTIONS)}")
        step = {"action": action}
        if action == "goto":
            path = raw.get("path")
            if not isinstance(path, str) or not path.startswith("/"):
                raise CaseError(f"{where} goto 需要以 / 开头的 path")
            step["path"] = path
        if action in NEEDS_TESTID:
            testid = raw.get("testid")
            if not isinstance(testid, str) or not testid:
                raise CaseError(f"{where} 缺少 testid")
            if testid not in allowed_testids:
                raise CaseError(f"{where} 的 testid {testid!r} 没在页面快照里出现过")
            step["testid"] = testid
        if action in EXPECT_TESTID:
            testid = raw.get("testid")
            if not isinstance(testid, str) or not testid:
                raise CaseError(f"{where} 缺少 testid")
            step["testid"] = testid
            step["unverified"] = testid not in allowed_testids
        if action in NEEDS_VALUE:
            if "value" not in raw:
                raise CaseError(f"{where} 缺少 value")
            step["value"] = str(raw["value"])
        cleaned.append(step)
    return cleaned


def validate_cases(text: str, snap: dict) -> list[dict]:
    data = extract_json(text)
    allowed = known_testids(snap)
    cases = data["cases"]
    if not isinstance(cases, list) or not cases:
        raise CaseError("cases 必须是非空数组")
    result = []
    for case in cases:
        if not isinstance(case, dict):
            raise CaseError("case 不是对象")
        title = str(case.get("title") or "").strip()
        if not title:
            raise CaseError("case 缺少 title")
        result.append(
            {
                "title": title,
                "steps": validate_steps(case.get("steps"), allowed, title),
                "expected": str(case.get("expected") or ""),
            }
        )
    return result
