"""HTTP 客户端：单例 requests.Session + ResponseData。

封装 requests 库的调用细节：
  - 单例 Session（pool_connections=10, Retry total=2）
  - 响应编码探测（apparent_encoding 兜底 utf-8-sig）
  - 4xx/5xx 默认抛 HTTPStatusError；网络错 → HTTPRequestFailed
  - 响应 > 10MB 自动截断 body_text（meta.body_truncated=true）
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .errors import HTTPRequestFailed, HTTPStatusError


# CST 时区（与 shenle-test-runner 一致）
_CST = timezone(timedelta(hours=8))


# response body 超过这个长度就截断（避免内存爆）
MAX_BODY_TEXT_BYTES = 10 * 1024 * 1024  # 10 MB


_session: requests.Session | None = None


def make_session() -> requests.Session:
    """构造（或复用）单例 requests.Session。

    Retry: total=2, backoff_factor=0.2, 状态码 429/5xx 才重试。
    """
    global _session
    if _session is not None:
        return _session

    s = requests.Session()
    retry = Retry(
        total=2,
        backoff_factor=0.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"),
    )
    adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    _session = s
    return s


@dataclass
class ResponseData:
    """结构化响应数据。"""

    url: str
    status: int
    status_text: str
    headers: dict[str, str]
    body_text: str
    body_json: Any           # dict / list / None（解析失败时为 None）
    elapsed_ms: int
    called_at: str           # ISO 8601 字符串（CST）
    body_truncated: bool = False
    size_bytes: int = 0      # 原始响应 body 字节数（截断前的长度）


def _try_parse_json(text: str) -> Any:
    """尝试把 body_text 解析成 JSON。失败返 None。"""
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def _detect_encoding(resp: requests.Response) -> str:
    """优先用 apparent_encoding，兜底 utf-8-sig。"""
    try:
        enc = resp.apparent_encoding
    except Exception:
        enc = None
    if enc and enc.lower() not in ("ascii", "iso-8859-1", "windows-1252"):
        return enc
    return "utf-8-sig"


def send_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | str | None = None,
    json_body: Any | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 30.0,
    verify_ssl: bool = True,
    fail_on_status: bool = True,
) -> ResponseData:
    """发一次 HTTP 请求，返回结构化 ResponseData。

    Args:
        method: 大写方法名（GET / POST / ...）
        url: 完整 URL
        headers: 请求头 dict（已 merge 好）
        data: 原始 body（bytes 或 str），与 json_body 互斥
        json_body: JSON body（requests 会自动 json.dumps + 设 Content-Type）
        params: query string dict
        timeout: 超时秒数
        verify_ssl: 是否校验 HTTPS 证书
        fail_on_status: 4xx/5xx 是否抛 HTTPStatusError（默认 True）

    Raises:
        HTTPRequestFailed: 网络层错（DNS / 连接 / 读取）
        HTTPStatusError: 4xx/5xx（仅当 fail_on_status=True）
    """
    session = make_session()
    try:
        kwargs: dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers or {},
            "timeout": timeout,
            "verify": verify_ssl,
        }
        if data is not None and json_body is not None:
            raise HTTPRequestFailed("data 和 json_body 不能同时传")
        if json_body is not None:
            kwargs["json"] = json_body
        elif data is not None:
            kwargs["data"] = data
        if params:
            kwargs["params"] = params

        resp = session.request(**kwargs)
    except requests.exceptions.RequestException as e:
        raise HTTPRequestFailed(str(e)) from e

    # 编码探测 + body 读取
    encoding = _detect_encoding(resp)
    raw_bytes = resp.content or b""
    size_bytes = len(raw_bytes)

    if size_bytes > MAX_BODY_TEXT_BYTES:
        body_text = raw_bytes[:MAX_BODY_TEXT_BYTES].decode(encoding, errors="replace")
        body_truncated = True
    else:
        body_text = raw_bytes.decode(encoding, errors="replace")
        body_truncated = False

    # 解析 JSON（仅当 Content-Type 暗示是 JSON 时尝试，省时间）
    body_json: Any = None
    ct = (resp.headers.get("content-type") or "").lower()
    if "json" in ct or body_text.startswith(("{", "[")):
        body_json = _try_parse_json(body_text)

    elapsed_ms = int(resp.elapsed.total_seconds() * 1000)
    called_at = datetime.now(_CST).isoformat(timespec="milliseconds")

    # headers 转成 plain dict（去掉可能存在的伪 dict 类型）
    headers_dict = {k: v for k, v in resp.headers.items()}

    data_obj = ResponseData(
        url=resp.url,
        status=resp.status_code,
        status_text=resp.reason or "",
        headers=headers_dict,
        body_text=body_text,
        body_json=body_json,
        elapsed_ms=elapsed_ms,
        called_at=called_at,
        body_truncated=body_truncated,
        size_bytes=size_bytes,
    )

    if fail_on_status and resp.status_code >= 400:
        raise HTTPStatusError(resp.status_code, resp.url)

    return data_obj
