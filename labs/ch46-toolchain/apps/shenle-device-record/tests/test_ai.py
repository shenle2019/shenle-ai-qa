"""shenle_device_record.ai 模块测试。"""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from shenle_device_record import ai


# ---------- load_config ----------


def test_load_config_returns_none_when_env_missing(tmp_path):
    """.env 不存在 → None（采集照常落盘，AI 字段为 null）。"""
    assert ai.load_config(tmp_path / ".env") is None


def test_load_config_returns_none_when_api_key_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("DEVICE_VISION_AI_MODEL=gpt-4o\n", encoding="utf-8")
    assert ai.load_config(env) is None


def test_load_config_returns_none_when_model_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("DEVICE_VISION_AI_API_KEY=sk-test\n", encoding="utf-8")
    assert ai.load_config(env) is None


def test_load_config_returns_config_when_valid(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "DEVICE_VISION_AI_API_KEY=sk-test\n"
        "DEVICE_VISION_AI_BASE_URL=https://api.example.com/v1/\n"  # 末尾 / 应被去掉
        "DEVICE_VISION_AI_MODEL=gpt-4o\n"
        "DEVICE_VISION_AI_TIMEOUT=15\n",
        encoding="utf-8",
    )
    config = ai.load_config(env)
    assert config is not None
    assert config.api_key == "sk-test"
    assert config.base_url == "https://api.example.com/v1"
    assert config.model == "gpt-4o"
    assert config.timeout == 15.0


def test_load_config_defaults_base_url_and_timeout(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "DEVICE_VISION_AI_API_KEY=sk-test\nDEVICE_VISION_AI_MODEL=gpt-4o\n",
        encoding="utf-8",
    )
    config = ai.load_config(env)
    assert config is not None
    assert config.base_url == "https://api.openai.com/v1"
    assert config.timeout == 30.0


def test_load_config_ignores_blank_lines_and_comments(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "\n# comment\n"
        "DEVICE_VISION_AI_API_KEY=sk-test\n"
        "\n"
        "# another comment\n"
        "DEVICE_VISION_AI_MODEL=gpt-4o\n",
        encoding="utf-8",
    )
    config = ai.load_config(env)
    assert config is not None
    assert config.model == "gpt-4o"


def test_load_config_strips_quotes_around_value(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        'DEVICE_VISION_AI_API_KEY="sk-with-quotes"\n'
        "DEVICE_VISION_AI_MODEL='gpt-4o'\n",
        encoding="utf-8",
    )
    config = ai.load_config(env)
    assert config is not None
    assert config.api_key == "sk-with-quotes"
    assert config.model == "gpt-4o"


def test_load_config_invalid_timeout_falls_back_to_default(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "DEVICE_VISION_AI_API_KEY=sk\nDEVICE_VISION_AI_MODEL=gpt-4o\nDEVICE_VISION_AI_TIMEOUT=not-a-number\n",
        encoding="utf-8",
    )
    config = ai.load_config(env)
    assert config is not None
    assert config.timeout == 30.0


# ---------- analyze_image ----------


def _make_response(content_obj: object, status: int = 200) -> dict:
    """构造 OpenAI 兼容 API 的响应 JSON。"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(content_obj, ensure_ascii=False),
                },
                "finish_reason": "stop",
            }
        ],
    }


def test_analyze_image_returns_three_descs_on_success_string_list(tmp_path):
    """elements_desc 是字符串列表 —— 合法风格之一。"""
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    response = _make_response(
        {
            "interface_desc": "登录页",
            "layout_desc": "上下布局：顶部 logo，中部表单",
            "elements_desc": [
                "状态栏：白色背景，显示时间与电量",
                "顶部 logo：居中，黑色文字 'MyApp'",
                "账号输入框：圆角，灰色提示文字",
                "密码输入框：同上",
                "登录按钮：蓝色填充，白色文字 '登录'",
            ],
        }
    )

    class _Resp:
        def __init__(self, body: bytes):
            self._body = body
        def read(self) -> bytes:
            return self._body
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen",
                      return_value=_Resp(json.dumps(response).encode("utf-8"))):
        result = ai.analyze_image(config, b"\x89PNG" * 10)
    assert result == {
        "interface_desc": "登录页",
        "layout_desc": "上下布局：顶部 logo，中部表单",
        "elements_desc": [
            "状态栏：白色背景，显示时间与电量",
            "顶部 logo：居中，黑色文字 'MyApp'",
            "账号输入框：圆角，灰色提示文字",
            "密码输入框：同上",
            "登录按钮：蓝色填充，白色文字 '登录'",
        ],
    }


def test_analyze_image_returns_three_descs_on_success_object_list(tmp_path):
    """elements_desc 是对象列表（element_type + description）—— 合法风格之二。"""
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    response = _make_response(
        {
            "interface_desc": "首页",
            "layout_desc": "顶部 tab 栏；中部 grid 网格",
            "elements_desc": [
                {"element_type": "状态栏", "description": "白色背景，电量与时间"},
                {"element_type": "tab 栏", "description": "底部 4 个 tab，选中第一个"},
                {"element_type": "卡片", "description": "9 宫格，居中图片 + 标题"},
            ],
        }
    )

    class _Resp:
        def read(self) -> bytes:
            return json.dumps(response).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen", return_value=_Resp()):
        result = ai.analyze_image(config, b"\x89PNG" * 10)
    assert result["elements_desc"] == [
        {"element_type": "状态栏", "description": "白色背景，电量与时间"},
        {"element_type": "tab 栏", "description": "底部 4 个 tab，选中第一个"},
        {"element_type": "卡片", "description": "9 宫格，居中图片 + 标题"},
    ]
    assert isinstance(result["elements_desc"], list)
    assert all(isinstance(e, dict) for e in result["elements_desc"])


def test_analyze_image_returns_none_on_network_error():
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    with patch.object(ai.urllib.request, "urlopen", side_effect=ai.urllib.error.URLError("boom")):
        assert ai.analyze_image(config, b"\x89PNG" * 10) is None


def test_analyze_image_returns_none_on_timeout():
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    with patch.object(ai.urllib.request, "urlopen", side_effect=TimeoutError("slow")):
        assert ai.analyze_image(config, b"\x89PNG" * 10) is None


def test_analyze_image_returns_none_on_invalid_response_json():
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")

    class _Resp:
        def read(self): return b"not json"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen", return_value=_Resp()):
        assert ai.analyze_image(config, b"\x89PNG" * 10) is None


def test_analyze_image_returns_none_when_content_is_not_valid_json():
    """AI 返回的 content 不是合法 JSON → None（不能 parse 三段）。"""
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    response = {
        "choices": [
            {"message": {"role": "assistant", "content": "对不起，我看不到图片"}}
        ]
    }

    class _Resp:
        def read(self): return json.dumps(response).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen", return_value=_Resp()):
        assert ai.analyze_image(config, b"\x89PNG" * 10) is None


def test_analyze_image_returns_three_nones_when_fields_missing():
    """AI 返回的 JSON 缺字段 → 三个字段都是 None。"""
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    response = _make_response({"interface_desc": "only one"})

    class _Resp:
        def read(self): return json.dumps(response).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen", return_value=_Resp()):
        result = ai.analyze_image(config, b"\x89PNG" * 10)
    assert result == {
        "interface_desc": "only one",
        "layout_desc": None,
        "elements_desc": None,
    }


def test_analyze_image_returns_none_for_elements_desc_mixed_types():
    """elements_desc 列表里同时有 str 和 dict（混用风格）→ 该字段写 None。"""
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    response = _make_response(
        {
            "interface_desc": "x",
            "layout_desc": "y",
            "elements_desc": ["字符串元素", {"element_type": "按钮"}],  # 混用
        }
    )

    class _Resp:
        def read(self): return json.dumps(response).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen", return_value=_Resp()):
        result = ai.analyze_image(config, b"\x89PNG" * 10)
    assert result is not None
    assert result["interface_desc"] == "x"
    assert result["layout_desc"] == "y"
    assert result["elements_desc"] is None  # 混用 → None


def test_analyze_image_elements_desc_empty_list_legal():
    """elements_desc 空列表合法（保留 []）。"""
    config = ai.AIConfig(api_key="sk", base_url="https://x.com/v1", model="gpt-4o")
    response = _make_response(
        {
            "interface_desc": "x",
            "layout_desc": "y",
            "elements_desc": [],
        }
    )

    class _Resp:
        def read(self): return json.dumps(response).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with patch.object(ai.urllib.request, "urlopen", return_value=_Resp()):
        result = ai.analyze_image(config, b"\x89PNG" * 10)
    assert result["elements_desc"] == []


def test_analyze_image_sends_correct_request_structure():
    """检查发出去的 HTTP 请求包含正确的 url / headers / body。"""
    config = ai.AIConfig(api_key="sk-xyz", base_url="https://api.x.com/v1", model="gpt-4o")

    captured: dict = {}

    class _Resp:
        def read(self) -> bytes:
            return json.dumps(
                _make_response(
                    {"interface_desc": "x", "layout_desc": "y", "elements_desc": "z"}
                )
            ).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["body"] = json.loads(req.data)
        captured["timeout"] = timeout
        return _Resp()

    with patch.object(ai.urllib.request, "urlopen", side_effect=fake_urlopen):
        ai.analyze_image(config, b"\x89PNG" * 10)

    assert captured["url"] == "https://api.x.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-xyz"
    assert captured["headers"]["Content-type"] == "application/json"
    assert captured["body"]["model"] == "gpt-4o"
    assert captured["body"]["response_format"] == {"type": "json_object"}
    msg = captured["body"]["messages"][0]
    # content 应是 [text_prompt, image_url_with_data_uri]
    assert msg["role"] == "user"
    assert isinstance(msg["content"], list)
    assert msg["content"][0]["type"] == "text"
    assert msg["content"][1]["type"] == "image_url"
    assert msg["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert captured["timeout"] == config.timeout
