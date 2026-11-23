import json

import pytest

from shenle_device_record.server import protocol


def test_encode_includes_type_and_fields():
    out = protocol.encode("hello", platform="android", screen_width=720, screen_height=1280)
    payload = json.loads(out)
    assert payload == {"type": "hello", "platform": "android",
                       "screen_width": 720, "screen_height": 1280}


def test_encode_preserves_chinese_characters():
    """落盘 JSON 用 ensure_ascii=False，编出的字符串里中文不应被 \\uXXXX 转义。"""
    out = protocol.encode("error", message="中文消息：adb 找不到")
    assert "中文消息" in out
    assert "\\u" not in out


def test_decode_round_trip():
    raw = protocol.encode("frame", mime="image/png", data="abc=", seq=7, ts=123.4)
    payload = protocol.decode(raw)
    assert payload == {"type": "frame", "mime": "image/png",
                       "data": "abc=", "seq": 7, "ts": 123.4}


def test_decode_returns_none_for_invalid_json():
    assert protocol.decode("{not json") is None
    assert protocol.decode("") is None
    assert protocol.decode("plain text") is None


def test_decode_returns_none_when_payload_not_object():
    """JSON 是合法的列表 / 字符串 / 数字时，decode 应返回 None（不是 dict）。"""
    assert protocol.decode("[1,2,3]") is None
    assert protocol.decode('"hello"') is None
    assert protocol.decode("42") is None
    assert protocol.decode("null") is None


def test_decode_returns_none_when_missing_type():
    raw = json.dumps({"message": "no type"})
    assert protocol.decode(raw) is None


def test_valid_outbound_inbound_sets_partition():
    """出/入类型集合必须不相交——同一个 type 不能既是发出又是接收。"""
    assert protocol.VALID_OUTBOUND_TYPES & protocol.VALID_INBOUND_TYPES == frozenset()
    assert "hello" in protocol.VALID_OUTBOUND_TYPES
    assert "frame" in protocol.VALID_OUTBOUND_TYPES
    assert "mode_changed" in protocol.VALID_OUTBOUND_TYPES
    assert "captured" in protocol.VALID_OUTBOUND_TYPES
    assert "error" in protocol.VALID_OUTBOUND_TYPES
    assert "shutdown" in protocol.VALID_OUTBOUND_TYPES
    # pong 是服务端对客户端 ping 的响应；ping 才是客户端发的
    assert "pong" in protocol.VALID_OUTBOUND_TYPES
    assert "capture" in protocol.VALID_INBOUND_TYPES
    assert "set_mode" in protocol.VALID_INBOUND_TYPES
    assert "set_frame_rate" in protocol.VALID_INBOUND_TYPES
    assert "ping" in protocol.VALID_INBOUND_TYPES


def test_is_valid_outbound_accepts_known_types_only():
    assert protocol.is_valid_outbound({"type": "frame"}) is True
    assert protocol.is_valid_outbound({"type": "shutdown"}) is True
    assert protocol.is_valid_outbound({"type": "pong"}) is True
    assert protocol.is_valid_outbound({"type": "capture"}) is False  # 客户端 type
    assert protocol.is_valid_outbound({"type": "weird"}) is False
    assert protocol.is_valid_outbound({}) is False


def test_is_valid_inbound_accepts_known_types_only():
    assert protocol.is_valid_inbound({"type": "capture"}) is True
    assert protocol.is_valid_inbound({"type": "ping"}) is True
    assert protocol.is_valid_inbound({"type": "pong"}) is False  # 服务端 type
    assert protocol.is_valid_inbound({"type": "hello"}) is False  # 服务端 type
    assert protocol.is_valid_inbound({"type": "weird"}) is False
    assert protocol.is_valid_inbound({}) is False


@pytest.mark.parametrize(
    "raw, expected_type",
    [
        ('{"type":"unknown_type","x":1}', "unknown_type"),  # 未知 type 不抛，由上层决定
        ('[1,2,3]', None),  # 非 dict 返回 None
        ('not json', None),  # 坏 JSON 返回 None
    ],
)
def test_decode_never_raises(raw, expected_type):
    """decode 永远不应抛异常；未知 type 也要原样解出来（上层决定是否警告）。"""
    payload = protocol.decode(raw)
    if expected_type is None:
        assert payload is None
    else:
        assert payload.get("type") == expected_type
