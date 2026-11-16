"""按维度矩阵生成接口用例，并统计覆盖。

设计原则：**维度是人定的，格子是固定要填的**。模型只负责把格子写具体。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass
class Case:
    cid: str
    endpoint: str
    dimension: str
    title: str
    priority: str
    request: dict[str, Any]
    expected: dict[str, Any]
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.cid,
            "endpoint": self.endpoint,
            "dimension": self.dimension,
            "title": self.title,
            "priority": self.priority,
            "request": self.request,
            "expected": self.expected,
            "note": self.note,
        }


def _base_request(ep: dict[str, Any]) -> dict[str, Any]:
    body = {p["name"]: f"v_{p['name']}" for p in ep["params"] if p["in"] == "body" and p.get("required")}
    for param in ep["params"]:
        if param["in"] == "body" and "default" in param:
            body[param["name"]] = param["default"]
    query = {p["name"]: p.get("default", 1) for p in ep["params"] if p["in"] == "query"}
    return {"method": ep["method"], "path": ep["path"], "query": query, "body": body, "headers": {}}


def generate(ep: dict[str, Any]) -> list[Case]:
    """一个接口 -> 一批用例。覆盖 7 个维度里适用的部分。"""
    cases: list[Case] = []
    base = _base_request(ep)
    key = f"{ep['method']} {ep['path']}"
    seq = 0

    def add(dimension: str, title: str, *, request: dict | None = None, status: int, check: dict | None = None,
            priority: str = "P1", note: str = "") -> None:
        nonlocal seq
        seq += 1
        cases.append(
            Case(
                cid=f"{ep['method']}-{ep['path'].replace('/', '-')}-{seq:02d}",
                endpoint=key,
                dimension=dimension,
                title=title,
                priority=priority,
                request=request or base,
                expected={"status": status, **(check or {})},
                note=note,
            )
        )

    # 1. 正常流
    success_codes = sorted(code for code in ep["responses"] if 200 <= code < 300)
    ok_status = success_codes[0] if success_codes else 200
    add("参数", "全部合法参数", status=ok_status, check={"has": list(ep["responses"].get(ok_status, []))}, priority="P0")

    # 2. 参数：必填缺失 / 类型错 / 越界 / 枚举非法 / 超长
    for param in ep["params"]:
        if param.get("required"):
            body = dict(base["body"])
            body.pop(param["name"], None)
            add("参数", f"缺少必填 {param['name']}", request={**base, "body": body}, status=422, priority="P0")
        if param["type"] == "int":
            add("参数", f"{param['name']} 传字符串", request={**base, "query": {**base["query"], param["name"]: "abc"}}, status=422)
            if "max" in param:
                add("参数", f"{param['name']} 超上限 {param['max'] + 1}",
                    request={**base, "query": {**base["query"], param["name"]: param["max"] + 1}}, status=422)
            if "min" in param:
                add("参数", f"{param['name']} 低于下限 {param['min'] - 1}",
                    request={**base, "query": {**base["query"], param["name"]: param["min"] - 1}}, status=422)
        if param["type"] == "enum":
            add("参数", f"{param['name']} 传非枚举值",
                request={**base, "body": {**base["body"], param["name"]: "not-a-role"}}, status=422)
        if "max_length" in param:
            add("参数", f"{param['name']} 超长",
                request={**base, "body": {**base["body"], param["name"]: "x" * (param["max_length"] + 1)}}, status=422)

    # 3. 位置：把 body 参数塞进 query
    body_params = [p["name"] for p in ep["params"] if p["in"] == "body"]
    if body_params:
        add("位置", f"{body_params[0]} 放到 query 而不是 body",
            request={**base, "body": {}, "query": {**base["query"], body_params[0]: "x"}}, status=422)

    # 4. 鉴权
    if ep.get("auth"):
        add("鉴权", "不带 token", request={**base, "headers": {}}, status=401, priority="P0")
        add("鉴权", "token 被篡改", request={**base, "headers": {"Authorization": "Bearer bad.token"}}, status=401)
        add("鉴权", "使用他人资源的 id", request={**base, "path": base["path"] + "/9999"}, status=404)

    # 5. 状态：只有创建类接口有状态机
    if ep["method"] == "POST" and "users" in ep["path"]:
        add("状态", "重名创建", request={**base, "body": {**base["body"], "name": "alice"}}, status=409, priority="P0")

    # 6. 数据量：分页接口
    if any(p["in"] == "query" and p["name"] == "size" for p in ep["params"]):
        add("数据量", "size=1 最小页", request={**base, "query": {**base["query"], "size": 1}}, status=200)
        add("数据量", "size=100 最大页", request={**base, "query": {**base["query"], "size": 100}}, status=200)
        add("数据量", "page 超出总页数", request={**base, "query": {**base["query"], "page": 99}}, status=200,
            check={"items_empty": True}, priority="P2")

    # 7. 兼容：多余字段不应报错（宽容解析）
    if body_params:
        add("兼容", "body 里带未知字段", request={**base, "body": {**base["body"], "__unknown__": 1}}, status=ok_status,
            priority="P2", note="若服务端 422，说明用了 strict 模式，需要确认是否有意")

    return cases


def coverage(cases: Iterable[Case], dimensions: list[str]) -> dict[str, dict[str, int]]:
    """按接口统计每个维度有几条用例，空格子一眼可见。"""
    table: dict[str, dict[str, int]] = {}
    for case in cases:
        row = table.setdefault(case.endpoint, {d: 0 for d in dimensions})
        row[case.dimension] = row.get(case.dimension, 0) + 1
    return table


def gaps(table: dict[str, dict[str, int]], dimensions: list[str]) -> list[tuple[str, str]]:
    return [(endpoint, dim) for endpoint, row in table.items() for dim in dimensions if row.get(dim, 0) == 0]
