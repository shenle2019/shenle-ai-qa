# apps/shenle-web-record/tests/test_dom_payload.py
import json

from shenle_web_record.paths import build_dom_payload


def test_basic_shape():
    payload = build_dom_payload("<html></html>", "img/screenshot_001.png")
    assert payload == {"content": "<html></html>", "img": "img/screenshot_001.png"}


def test_preserves_chinese_chars():
    payload = build_dom_payload("<p>你好世界</p>", "img/screenshot_002.png")
    dumped = json.dumps(payload, ensure_ascii=False)
    assert "你好世界" in dumped


def test_does_not_escape_html():
    raw = "<a href=\"https://x.com/?a=1&b=2\">q</a>"
    payload = build_dom_payload(raw, "img/screenshot_003.png")
    assert payload["content"] == raw