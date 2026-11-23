"""极简 JSONPath walker：只支持点路径 + 数组下标。

支持语法：
  $.a.b.c          点路径
  $.a[0].b         数组下标（必须紧跟字段名）
  $.data.token     最常见
  $                根（返回整个 data）

不支持（明确抛 JSONPathSyntaxError）：
  $..token         递归
  $.*              通配
  $.[?(@.x==1)]    filter 表达式
  $.a:bc           切片

匹配不到返 None（不抛错，与自然语言 AI 提取的语义对齐）。
"""

from __future__ import annotations

import re
from typing import Any

from .errors import JSONPathSyntaxError


# token 类型：.key 或 [N]
# key 允许任意非 . [ ] 空白字符（覆盖中文 / Unicode 字段名）
_DOT_KEY = r"\.([^.\[\]\s]+)"
_BRACKET_IDX = r"\[(\d+)\]"
_TOKEN_RE = re.compile(f"{_DOT_KEY}|{_BRACKET_IDX}")


def _parse(path: str) -> list[tuple[str, Any]]:
    """把 JSONPath 解析成 token 列表：[("key", "字段名") | ("idx", N), ...]

    Raises:
        JSONPathSyntaxError: 语法不支持 / 含未知字符 / 数组下标非整数。
    """
    if path is None:
        raise JSONPathSyntaxError(str(path))
    body = path.strip()
    if not body:
        raise JSONPathSyntaxError(path)
    if not body.startswith("$"):
        raise JSONPathSyntaxError(path)
    body = body[1:]
    if body == "":
        return []

    tokens: list[tuple[str, Any]] = []
    pos = 0
    while pos < len(body):
        c = body[pos]
        if c == ".":
            m = _TOKEN_RE.match(body, pos)
            if not m or m.group(1) is None:
                raise JSONPathSyntaxError(path)
            tokens.append(("key", m.group(1)))
            pos = m.end()
            continue
        if c == "[":
            m = _TOKEN_RE.match(body, pos)
            if not m or m.group(2) is None:
                raise JSONPathSyntaxError(path)
            tokens.append(("idx", int(m.group(2))))
            pos = m.end()
            continue
        # 其它字符 → 不支持
        raise JSONPathSyntaxError(path)
    return tokens


def eval_path(data: Any, path: str) -> Any:
    """按 JSONPath 取 data 里的值。匹配不到返 None。

    Args:
        data: 任意 JSON-like 数据（dict / list / str / num / None）
        path: JSONPath 字符串（如 "$.data.token"）

    Returns:
        取到的值；路径不存在或中间不是 dict/list 返 None。
    """
    tokens = _parse(path)
    cur: Any = data
    for kind, val in tokens:
        if kind == "key":
            if not isinstance(cur, dict):
                return None
            if val not in cur:
                return None
            cur = cur[val]
        elif kind == "idx":
            if not isinstance(cur, list):
                return None
            if val < 0 or val >= len(cur):
                return None
            cur = cur[val]
        else:
            return None
    return cur


def is_jsonpath(field: str) -> bool:
    """判断字段描述是不是 JSONPath（以 $ 开头）。"""
    return bool(field) and field.strip().startswith("$")
