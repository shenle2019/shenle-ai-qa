"""配置：命令行 > 环境变量 > 默认。"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    name: str
    base_url: str
    timeout: float = 5.0
    retries: int = 1


ENVS = {
    "local": Settings("local", "http://127.0.0.1:8000"),
    "staging": Settings("staging", "https://staging.example.com", retries=2),
    "ci": Settings("ci", "http://127.0.0.1:8000", retries=2),
}


def load(env: str | None = None) -> Settings:
    name = env or os.getenv("TEST_ENV") or "local"
    base = ENVS.get(name)
    if base is None:
        raise SystemExit(f"未知环境：{name}（可选 {', '.join(ENVS)}）")
    override = os.getenv("TEST_BASE_URL")
    return Settings(base.name, override, base.timeout, base.retries) if override else base
