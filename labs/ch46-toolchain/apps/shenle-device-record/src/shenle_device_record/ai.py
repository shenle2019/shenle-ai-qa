"""可选 AI 界面描述模块。

从运行目录的 `.env` 读 `DEVICE_VISION_AI_API_KEY` / `DEVICE_VISION_AI_BASE_URL`
/ `DEVICE_VISION_AI_MODEL`（可选 `DEVICE_VISION_AI_TIMEOUT`）。
配置缺失或调用失败一律返回 `None` —— 调用方必须把 `None` 当作"没结果"处理，
不中断采集流程。

只依赖 Python 标准库（`urllib`、`json`、`ssl`），不引入 `openai` SDK。
"""
from __future__ import annotations

import base64
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shenle_device_record import LOG_PREFIX

# OpenAI 兼容 API 默认端点；改 DEVICE_VISION_AI_BASE_URL 可指向其他兼容服务（火山豆包、智谱、
# 月之暗面、本地 ollama 等）。
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_TIMEOUT = 30.0

# 默认 prompt，要求严格的 JSON 输出。
DEFAULT_PROMPT = (
    "你必须输出一个严格的 JSON 对象：\n"
    "1. interface_desc（字符串）：一句话概括该界面的整体用途、视觉风格（如颜色基调、设计风格）和核心功能模块，让读者快速了解页面全貌。\n"
    "2. layout_desc（字符串）：描述界面自顶向下的布局结构，需使用『顶部为...；主体区域依次为...；底部为...』等顺序性语言，明确各模块之间的相对位置和排版方式（如垂直排列、网格布局、固定底部等）。\n"
    "3. elements_desc（数组）：详细列出界面中的每一个可见元素或交互控件。数组中的每个元素可以是字符串或对象（二选一，但在同一输出中保持风格一致）：\n"
    "   若使用字符串：每个元素用一段简洁的文本描述，包含元素类型、位置、样式（颜色、图标、文字）、状态（选中/未选中、可点击提示等）及其功能。\n"
    "   若使用对象：每个对象必须包含 \"element_type\"（元素类别，如『状态栏』、『导航栏』、『输入框』、『按钮』、『卡片』等）和 \"description\"（详细描述，要求同上）两个键。\n"
    "只输出 JSON，不要其它文字、不要 Markdown 代码块标记。"
)

AI_PAYLOAD_KEYS = ("interface_desc", "layout_desc", "elements_desc")
# 字符串字段：必须是 str。列表字段：必须是 list[ str | dict ]。
AI_STRING_KEYS = ("interface_desc", "layout_desc")
AI_LIST_KEYS = ("elements_desc",)


@dataclass(frozen=True)
class AIConfig:
    api_key: str
    base_url: str
    model: str
    timeout: float = DEFAULT_TIMEOUT


def load_config(env_path: str | Path = ".env") -> AIConfig | None:
    """从 `.env` 读配置。`DEVICE_VISION_AI_API_KEY` 与 `DEVICE_VISION_AI_MODEL`
    缺一即返回 `None`。

    找不到 `.env` 文件也返回 `None`，调用方按"未启用 AI"处理。
    """
    env = _read_env(env_path)
    api_key = env.get("DEVICE_VISION_AI_API_KEY", "").strip()
    model = env.get("DEVICE_VISION_AI_MODEL", "").strip()
    if not api_key or not model:
        return None
    base_url = env.get("DEVICE_VISION_AI_BASE_URL", "").strip().rstrip("/")
    if not base_url:
        base_url = DEFAULT_BASE_URL
    timeout_raw = env.get("DEVICE_VISION_AI_TIMEOUT", "").strip()
    try:
        timeout = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT
    except ValueError:
        timeout = DEFAULT_TIMEOUT
    return AIConfig(api_key=api_key, base_url=base_url, model=model, timeout=timeout)


def _read_env(path: str | Path) -> dict[str, str]:
    """最小 .env 解析：每行 `KEY=VALUE`，空行 / `# 开头` 跳过，值去前后单/双引号。

    不依赖 python-dotenv。容错优先：解析失败返回 `{}` 而不是抛异常。
    """
    result: dict[str, str] = {}
    p = Path(path)
    if not p.is_file():
        return result
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return result
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        result[key] = value
    return result


def analyze_image(
    config: AIConfig,
    png_bytes: bytes,
    *,
    prompt: str = DEFAULT_PROMPT,
) -> dict[str, Any] | None:
    """调 OpenAI 兼容多模态 API，返回 `{interface_desc, layout_desc, elements_desc}`。

    成功 → dict（前两个字段是字符串；elements_desc 是字符串列表或对象列表）
    失败（网络错 / 超时 / 响应解析失败 / 字段缺失）→ 整个返回 `None`

    调用方收到 `None` 时不应中断采集，应把三个字段存为 `null`。
    """
    b64 = base64.b64encode(png_bytes).decode("ascii")
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            }
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1024,
    }
    url = f"{config.base_url}/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=config.timeout) as resp:
            raw = resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        _warn(f"AI 调用失败：{type(exc).__name__}: {exc}")
        return None

    return _parse_response(raw)


def _parse_response(raw: str) -> dict[str, Any] | None:
    """从 OpenAI 兼容响应里抠出三段描述。失败返回 None。

    - interface_desc / layout_desc：字符串（前后空白剥掉；空串 → None）
    - elements_desc：列表。每个元素是字符串或对象（element_type + description），
      不混用；混用 / 其他类型 → 该字段写 None（不算整体失败，其他字段仍能拿到）。
    """
    try:
        obj = json.loads(raw)
        content = obj["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            return None
        parsed = json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        _warn(f"AI 响应解析失败：{type(exc).__name__}: {exc}")
        return None

    if not isinstance(parsed, dict):
        return None
    result: dict[str, Any] = {}
    for key in AI_STRING_KEYS:
        value = parsed.get(key)
        if value is None:
            result[key] = None
        elif isinstance(value, str):
            stripped = value.strip()
            result[key] = stripped if stripped else None
        else:
            # 类型不对也接受（AI 偶发返回 int 等），强转字符串
            s = str(value).strip()
            result[key] = s if s else None
    for key in AI_LIST_KEYS:
        value = parsed.get(key)
        result[key] = _normalize_elements_list(value)
    return result


def _normalize_elements_list(value: Any) -> list[Any] | None:
    """校验 / 规范化 elements_desc 列表：全部是字符串或全部是 dict 才合法。

    混合 / 其它类型 → None。
    """
    if value is None:
        return None
    if not isinstance(value, list):
        return None
    if not value:
        return []  # 空列表合法
    if all(isinstance(e, str) for e in value):
        # 字符串列表：剥掉空串
        return [s.strip() for s in value if s.strip()]
    if all(isinstance(e, dict) for e in value):
        # 对象列表：原样保留（信任 AI 输出）
        return value
    return None  # 混合类型 → 失败


def _warn(msg: str) -> None:
    try:
        print(f"{LOG_PREFIX} {msg}", file=sys.stderr)
    except Exception:  # noqa: BLE001
        pass
