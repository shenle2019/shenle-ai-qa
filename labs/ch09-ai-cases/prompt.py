"""把契约 + 矩阵拼成提示词；顺便审一份「模型产出」的用例。

这里不调真实模型：
- :func:`build_prompt` 产出的提示词可以直接贴给任意 LLM；
- :func:`review` 审的是一份**故意写坏**的样例，用来演示五道审。
"""

from __future__ import annotations

import json
import re
from typing import Any

from matrix import Case

SYSTEM = "你是接口测试工程师。你只输出 JSON，不解释。"

TEMPLATE = """【角色】{role}

【接口契约】
{spec}

【用例矩阵】已由人确定，你只负责把每个格子写具体：
{matrix}

【任务】上面每个 (接口, 维度) 组合至少 1 条用例，缺失的格子必须补齐。

【输出】严格输出 JSON 数组，每个元素字段固定为：
{fields}

【硬约束】
1. expected 必须可判定：至少包含 status，其余用 "字段=值" 形式；
2. 禁止出现「返回正确」「功能正常」「验证稳定性」这类无法判定的描述；
3. 每条用例的 request 必须能独立执行（含 method/path/query/body/headers）；
4. 不确定的前置条件写进 note，并标注 "TODO:"。
"""

FIELDS = ["id", "endpoint", "dimension", "title", "priority", "request", "expected", "note"]


def build_prompt(spec: dict[str, Any], table: dict[str, dict[str, int]], cases: list[Case]) -> str:
    matrix_lines = []
    for endpoint, row in table.items():
        missing = [dim for dim, count in row.items() if count == 0]
        matrix_lines.append(f"- {endpoint}: 已覆盖 {sum(row.values())} 条；缺：{', '.join(missing) or '无'}")
    sample = json.dumps([c.to_dict() for c in cases[:2]], ensure_ascii=False, indent=2)
    return TEMPLATE.format(
        role=SYSTEM,
        spec=json.dumps(spec, ensure_ascii=False, indent=2),
        matrix="\n".join(matrix_lines),
        fields=", ".join(FIELDS),
    ) + f"\n\n【风格示例】\n{sample}\n"


VAGUE = ("返回正确", "功能正常", "验证稳定", "稳定运行", "无异常", "符合预期", "数据正确", "应当正常")
BAD_SAMPLE: list[dict[str, Any]] = [
    {
        "id": "BAD-1",
        "endpoint": "POST /api/users",
        "dimension": "参数",
        "title": "创建用户-正常",
        "priority": "P0",
        "request": {"method": "POST", "path": "/api/users", "body": {"name": "dave"}},
        "expected": {"status": 201, "msg": "返回正确"},
        "note": "",
    },
    {
        "id": "BAD-2",
        "endpoint": "GET /api/users",
        "dimension": "鉴权",
        "title": "验证系统稳定运行",
        "priority": "P1",
        "request": {"method": "GET", "path": "/api/users"},
        "expected": {"status": 200},
        "note": "",
    },
    {
        "id": "BAD-3",
        "endpoint": "GET /api/users",
        "dimension": "参数",
        "title": "size 越界",
        "priority": "P1",
        "request": "GET /api/users?size=101",
        "expected": {"status": 422},
        "note": "",
    },
    {
        "id": "GOOD-1",
        "endpoint": "POST /api/users",
        "dimension": "状态",
        "title": "重名创建返回 409",
        "priority": "P0",
        "request": {"method": "POST", "path": "/api/users", "body": {"name": "alice"}},
        "expected": {"status": 409, "error": "duplicate_name"},
        "note": "依赖 alice 已存在",
    },
]


def _is_vague(text: str) -> bool:
    return any(word in text for word in VAGUE)


def review(cases: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """五道审：可执行 / 可判定 / 前置清楚 / 数据可造 / 不重复。"""
    result: dict[str, list[dict[str, Any]]] = {"pass": [], "revise": [], "drop": []}
    seen: set[tuple] = set()

    for case in cases:
        problems: list[str] = []
        request = case.get("request")

        # 1. 可执行：request 必须结构化且带 method/path
        if not isinstance(request, dict) or not {"method", "path"} <= set(request):
            problems.append("request 不是可执行结构（缺 method/path）")

        # 2. 可判定：expected 必须有 status，且不能是模糊话
        expected = case.get("expected") or {}
        if "status" not in expected:
            problems.append("expected 缺 status")
        if any(_is_vague(str(v)) for v in expected.values()) or _is_vague(case.get("title", "")):
            problems.append("存在无法判定的描述")

        # 3. 前置清楚：note 里带 TODO 或依赖说明
        if "TODO" in (case.get("note") or ""):
            problems.append("前置条件未确认（TODO）")

        # 4. 不重复
        fingerprint = (case.get("endpoint"), case.get("dimension"), json.dumps(case.get("request"), sort_keys=True, default=str))
        if fingerprint in seen:
            problems.append("与已有用例重复")
        seen.add(fingerprint)

        if any("不是可执行结构" in p or "缺 status" in p for p in problems):
            result["drop"].append({**case, "problems": problems})
        elif problems:
            result["revise"].append({**case, "problems": problems})
        else:
            result["pass"].append(case)

    return result


def estimate_coverage(cases: list[dict[str, Any]]) -> dict[str, int]:
    """审完的用例按维度计数，用于和矩阵对比。"""
    counts: dict[str, int] = {}
    for case in cases:
        dim = case.get("dimension", "?")
        counts[dim] = counts.get(dim, 0) + 1
    return counts


def normalise_title(raw: str) -> str:
    """把「验证系统稳定运行」这类标题压成可读的形式，仅用于演示。"""
    text = re.sub(r"[，。；]", " ", raw).strip()
    return " ".join(text.split())[:40]
