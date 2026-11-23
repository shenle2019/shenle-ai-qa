"""WebSocket 协议层：消息类型常量 + JSON 编解码。所有消息进出都过它。"""
from __future__ import annotations

import json
from typing import Any

# 服务端 → 客户端
HELLO = "hello"
FRAME = "frame"
MODE_CHANGED = "mode_changed"
CAPTURED = "captured"
ERROR = "error"
SHUTDOWN = "shutdown"

# 客户端 → 服务端
CAPTURE = "capture"
SET_MODE = "set_mode"
SET_FRAME_RATE = "set_frame_rate"
PONG = "pong"
# 心跳：客户端发 ping，服务端回 pong（spec "客户端 ping / 服务端 pong"）。
PING = "ping"

VALID_OUTBOUND_TYPES: frozenset[str] = frozenset(
    {HELLO, FRAME, MODE_CHANGED, CAPTURED, ERROR, SHUTDOWN, PONG}
)
VALID_INBOUND_TYPES: frozenset[str] = frozenset(
    {CAPTURE, SET_MODE, SET_FRAME_RATE, PING}
)


def encode(type_: str, **fields: Any) -> str:
    """构造一条协议消息，序列化为 JSON 字符串。"""
    payload = {"type": type_, **fields}
    return json.dumps(payload, ensure_ascii=False)


def decode(raw: str) -> dict[str, Any] | None:
    """解码 JSON 消息。返回 None 表示"这条消息不合法"，调用方应忽略不报错。

    非法情况：
    * 不是合法 JSON
    * 顶层不是 dict
    * 缺 `type` 字段（即便 dict 里没有 type，也没法走类型分发，直接返回 None）
    """
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    if "type" not in payload or not isinstance(payload["type"], str):
        return None
    return payload


def is_valid_outbound(payload: dict[str, Any]) -> bool:
    return payload.get("type") in VALID_OUTBOUND_TYPES


def is_valid_inbound(payload: dict[str, Any]) -> bool:
    return payload.get("type") in VALID_INBOUND_TYPES
