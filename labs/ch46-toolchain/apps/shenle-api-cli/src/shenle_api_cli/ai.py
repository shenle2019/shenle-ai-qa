"""AI 配置加载 + 纯文本 chat/completions 调用。

照搬 shenle-web-cli/ai.py 的模式：
  - load_config() 读 CWD/.env + 真实 env（env 优先）
  - ask_text() 调 chat/completions + 强制 response_format=json_object
  - 缺配置立刻 AIConfigError，不重试

env 前缀：API_AUTOMATION_AI_*（与 web-cli 的 WEB_AUTOMATION_AI_* 对齐防冲突）
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values

from .errors import AIConfigError, AIRuntimeError


_REQUIRED_ENV = (
    "API_AUTOMATION_AI_API_KEY",
    "API_AUTOMATION_AI_BASE_URL",
    "API_AUTOMATION_AI_MODEL",
)


# ---------------------------------------------------------------------------
# 配置


@dataclass(frozen=True)
class AIConfig:
    api_key: str
    base_url: str
    model: str

    def chat_url(self) -> str:
        """完整的 chat/completions URL。"""
        base = self.base_url.rstrip("/")
        # 如果用户已经填到 /v1 结尾，不再重复拼；否则按 OpenAI 标准拼 /v1/chat/completions
        if base.endswith("/chat/completions"):
            return base
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"


def load_config() -> AIConfig:
    """从 CWD/.env + 真实 env 加载 AI 配置。

    Returns:
        AIConfig 实例。

    Raises:
        AIConfigError: 任一必需 env var 缺失。
    """
    values: dict[str, str] = {}
    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.is_file():
        for k, v in dotenv_values(dotenv_path).items():
            if v is not None:
                values[k] = v
    # 真实 env 优先
    for k in _REQUIRED_ENV:
        env_val = os.environ.get(k)
        if env_val:
            values[k] = env_val

    missing = [k for k in _REQUIRED_ENV if not values.get(k)]
    if missing:
        raise AIConfigError(missing)

    base_url = values[_REQUIRED_ENV[1]]
    if not base_url.startswith(("http://", "https://")):
        # 兜底加 https://
        base_url = "https://" + base_url

    return AIConfig(
        api_key=values[_REQUIRED_ENV[0]],
        base_url=base_url,
        model=values[_REQUIRED_ENV[2]],
    )


# ---------------------------------------------------------------------------
# JSON 解析（容错掉 markdown 包裹 + 前后解释文字）


_JSON_OBJ_RE = re.compile(r"\{[\s\S]*\}")


def _try_parse_json_loose(text: str) -> dict[str, Any] | None:
    """容错解析 JSON dict。失败返 None。

    处理：
      - 直接是 JSON → json.loads
      - 被 ```json ... ``` 包裹 → 剥掉
      - 前后有解释文字 + 中间嵌 {...} → re.findall 找第一个 {...}
    """
    if not text:
        return None
    text = text.strip()
    # 剥 markdown 围栏
    fence = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fence:
        text = fence.group(1)
    # 直接 try
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except (ValueError, TypeError):
        pass
    # fallback：找第一个完整 {...}
    m = _JSON_OBJ_RE.search(text)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict):
                return obj
        except (ValueError, TypeError):
            pass
    return None


# ---------------------------------------------------------------------------
# chat/completions 调用


def ask_text(
    cfg: AIConfig,
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int = 512,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """调一次 chat/completions，强制 JSON 输出，返回解析后的 dict。

    Args:
        cfg: AIConfig 实例
        system_prompt: 系统提示
        user_prompt: 用户消息
        max_tokens: 最大输出 tokens（默认 512）
        timeout: 超时秒数

    Returns:
        解析后的 JSON dict。

    Raises:
        AIRuntimeError: 网络错 / 返回非 JSON / 解析失败
    """
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            cfg.chat_url(),
            headers=headers,
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise AIRuntimeError(f"网络错误：{e}") from e

    if resp.status_code >= 400:
        # 截前 500 字符 detail
        detail = (resp.text or "")[:500]
        raise AIRuntimeError(f"HTTP {resp.status_code}：{detail}")

    try:
        outer = resp.json()
    except (ValueError, TypeError) as e:
        raise AIRuntimeError(f"返回不是 JSON：{e}") from e

    try:
        content = outer["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise AIRuntimeError(f"返回结构不对（缺 choices[0].message.content）：{e}") from e

    parsed = _try_parse_json_loose(content)
    if parsed is None:
        snippet = (content or "")[:200]
        raise AIRuntimeError(f"返回 content 不是合法 JSON：{snippet}")
    return parsed


# ---------------------------------------------------------------------------
# Prompt 常量（专用 prompt）


PROMPT_EXTRACT_NL = """\
你是测试结果提取助手。看到一次接口调用的请求与响应，请按用户给定的"提取描述"列表，\
从响应体（通常是 JSON 字符串）中抽取对应字段的值。

要求：
- 严格按用户描述定位字段；找不到的字段值设为 null
- 返回 JSON：`{"<字段名>": "<值>"}`（字段名用用户给的；值保持原始类型，能转数字就转，\
  不能就当字符串）
- 不要解释、不要写多余文字

响应体（原始文本，可能是 JSON 也可能是 text/html）：
{response_body}

响应 Content-Type：
{content_type}

提取描述列表（每个一行，格式：- 字段名 = "<中文描述>"）：
{extraction_specs}
"""


PROMPT_ASSERT_NL = """\
你是接口响应断言助手。看到一次接口调用的请求与响应，请判断给定的断言描述是否成立。

要求：
- 严格按断言描述的语义判断（不要死磕某个字段名，要理解意思）
- 返回 JSON：`{{"passed": true|false, "reason": "<一句话中文原因>"}}`
- reason 要给出关键证据（如"状态码 200" / "data.token 缺失" / "msg 包含 SUCCESS"）

响应体（原始文本，可能是 JSON 也可能是 text/html）：
{response_body}

响应状态码：{status_code}
响应 Content-Type：{content_type}

断言描述：
{assertion}
"""
