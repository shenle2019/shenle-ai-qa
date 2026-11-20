"""第 42 章：接口资产。从精简 spec 生成可维护的接口清单，并做一次一致性校验。"""

from __future__ import annotations

from dataclasses import dataclass, field

METHODS = ("get", "post", "put", "patch", "delete")


@dataclass
class Endpoint:
    method: str
    path: str
    summary: str = ""
    params: list = field(default_factory=list)
    body_required: bool = False

    @property
    def key(self):
        return f"{self.method.upper()} {self.path}"


class SpecError(ValueError):
    pass


def parse_spec(spec):
    """spec 形如 {base_url, paths: {'/x': {'get': {...}}}}。"""
    if not isinstance(spec, dict) or "paths" not in spec:
        raise SpecError("spec 缺少 paths")
    base = spec.get("base_url", "")
    if not base.startswith(("http://", "https://")):
        raise SpecError("base_url 必须以 http 开头")
    out = []
    for path, item in (spec["paths"] or {}).items():
        if not path.startswith("/"):
            raise SpecError(f"路径必须以 / 开头：{path}")
        for method, op in (item or {}).items():
            if method.lower() not in METHODS:
                raise SpecError(f"不支持的方法：{method}")
            out.append(
                Endpoint(
                    method=method.upper(),
                    path=path,
                    summary=(op or {}).get("summary", ""),
                    params=list((op or {}).get("params") or []),
                    body_required=bool((op or {}).get("body")),
                )
            )
    return base, sorted(out, key=lambda e: (e.path, e.method))


def validate(endpoints):
    """返回问题清单；空列表代表通过。"""
    problems = []
    seen = {}
    for item in endpoints:
        key = item.key
        if key in seen:
            problems.append(f"重复接口：{key}")
        seen[key] = True
        if item.method in ("POST", "PUT", "PATCH") and not item.body_required:
            problems.append(f"{key} 是写接口但没有 body 定义")
        if "{" in item.path and not item.params:
            problems.append(f"{key} 路径带变量却没有声明 params")
        if item.summary == "":
            problems.append(f"{key} 缺少 summary")
    return problems


def to_markdown(endpoints, base=""):
    lines = [f"接口清单（{len(endpoints)} 个，base={base}）", "", "| 方法 | 路径 | 说明 |", "| --- | --- | --- |"]
    lines += [f"| {e.method} | `{e.path}` | {e.summary or '-'} |" for e in endpoints]
    return "\n".join(lines) + "\n"
