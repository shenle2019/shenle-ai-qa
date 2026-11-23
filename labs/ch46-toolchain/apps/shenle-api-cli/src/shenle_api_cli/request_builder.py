"""把 case.request dict 转成 requests 调用参数。

case.request 实际结构（来自 AIQE case yaml，runner 渲染后）：
  {
    "url": "https://...",
    "method": "POST",
    "headers": [{"name": "...", "value": "...", "desc": "..."}],
    "urlParams": [{"name": "...", "value": "...", "desc": "..."}],
    "bodyParams": [{"name": "...", "value": "...", "desc": "..."}]
  }

`desc` 字段被忽略（仅给人类看）。
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode

from .errors import RequestFileInvalid


# Content-Length 让 requests 自己算；其它保留
_AUTO_HEADERS = {"content-length", "host"}


def _kv_list_to_dict(items: list[Any] | None) -> dict[str, str]:
    """把 [{name, value, ...}] 转成 dict，跳过 name/value 缺失项。"""
    if not items:
        return {}
    out: dict[str, str] = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        name = it.get("name")
        value = it.get("value", "")
        if name is None:
            continue
        out[str(name)] = "" if value is None else str(value)
    return out


def _strip_auto_headers(headers: dict[str, str]) -> dict[str, str]:
    """去掉 requests 自己会算的 header（content-length / host）。"""
    return {k: v for k, v in headers.items() if k.lower() not in _AUTO_HEADERS}


def _build_url_params(url: str, params: dict[str, str]) -> str:
    """把 query string 拼到 url（处理 url 已含 ? 的情况）。"""
    if not params:
        return url
    qs = urlencode(params, doseq=True)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{qs}"


def _detect_content_type(headers: dict[str, str]) -> str:
    """从 headers 拿 content-type，没设返空字符串。"""
    for k, v in headers.items():
        if k.lower() == "content-type":
            return v.lower()
    return ""


def _serialize_body(
    body_params: dict[str, str], content_type: str
) -> tuple[Any, bool]:
    """根据 content-type 序列化 bodyParams。

    Returns:
        (data_or_json_body, is_json)
        - (json.dumps({k:v}), True)        # 给 requests 的 json= 参数
        - ("k=v&k2=v2", False)             # 给 requests 的 data= 参数
        - ("", False)                      # 无 body
    """
    if not body_params:
        return ("", False)

    if "application/json" in content_type:
        return (json.dumps(body_params, ensure_ascii=False), True)

    # 默认 / urlencoded / 其他：urlencode
    return (urlencode(body_params, doseq=True), False)


def build_requests_args(
    request_dict: dict[str, Any],
    *,
    default_timeout: float = 30.0,
) -> dict[str, Any]:
    """把 case.request 转成可直接传给 session.request(**) 的 dict。

    Args:
        request_dict: 渲染后的 case.request（参见模块 docstring）
        default_timeout: 超时秒数（默认 30s；调用方可覆盖）

    Returns:
        {
            "method": "POST",
            "url": "https://...?k=v",
            "headers": {...},
            "data"|"json": ...,
            "params": {...},            # 仅当 urlParams 单独存在
            "timeout": 30.0,
        }

    Raises:
        RequestFileInvalid: request_dict 字段类型错 / 缺 url。
    """
    if not isinstance(request_dict, dict):
        raise RequestFileInvalid("request 必须是 dict")

    url = request_dict.get("url")
    if not isinstance(url, str) or not url.strip():
        raise RequestFileInvalid("缺少 url 或 url 不是字符串")
    url = url.strip()

    method_raw = request_dict.get("method", "GET")
    if not isinstance(method_raw, str):
        raise RequestFileInvalid("method 必须是字符串")
    method = method_raw.strip().upper() or "GET"

    headers_raw = request_dict.get("headers") or []
    headers = _strip_auto_headers(_kv_list_to_dict(headers_raw))

    url_params = _kv_list_to_dict(request_dict.get("urlParams") or [])
    body_params = _kv_list_to_dict(request_dict.get("bodyParams") or [])

    # 拼 url（如果 url 里已有 query string 且 urlParams 也有，用 & 拼上）
    full_url = _build_url_params(url, url_params)

    # body 序列化
    content_type = _detect_content_type(headers)
    body_data, is_json = _serialize_body(body_params, content_type)

    result: dict[str, Any] = {
        "method": method,
        "url": full_url,
        "headers": headers,
        "timeout": default_timeout,
    }
    if is_json:
        # 用 json_body 让 requests 自动处理 Content-Type 和编码
        try:
            result["json_body"] = json.loads(body_data)
        except (ValueError, TypeError):
            # 序列化失败就当原始 data
            result["data"] = body_data
    else:
        result["data"] = body_data if body_params else None

    return result
