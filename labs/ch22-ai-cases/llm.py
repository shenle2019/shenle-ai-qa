"""模型客户端：一个真调 DeepSeek，一个假答复供离线测试。

两者接口一致：`complete(messages) -> str`。测试永远用 FakeClient，
所以 `pytest labs -q` 不需要 key、不需要网。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass


class LLMError(RuntimeError):
    """调用模型失败。"""


@dataclass
class DeepSeekClient:
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    timeout: float = 60.0

    def complete(self, messages: list[dict[str, str]]) -> str:
        import requests

        key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not key:
            raise LLMError("没有配置 DEEPSEEK_API_KEY，改用 FakeClient 或先设置环境变量")
        response = requests.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": self.model, "messages": messages, "temperature": 0.2, "response_format": {"type": "json_object"}},
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise LLMError(f"HTTP {response.status_code}: {response.text[:300]}")
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"响应结构不符合预期：{json.dumps(data)[:300]}") from exc


class FakeClient:
    """把预设回复排队返回，并记录收到的提示词。"""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        if not self.replies:
            raise LLMError("FakeClient 没有更多预设回复")
        return self.replies.pop(0)
