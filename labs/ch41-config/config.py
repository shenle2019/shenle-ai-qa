"""第 41 章：配置与环境。yaml 管结构，环境变量管密钥，读的时候展开、打印的时候脱敏。"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

VAR = re.compile(r"\$\{([A-Z0-9_]+)\}")


class ConfigError(ValueError):
    pass


def expand(value, env=None):
    """把 ${VAR} 换成环境变量；取不到就抛错，绝不静默变空串。"""
    env = os.environ if env is None else env

    def one(match):
        key = match.group(1)
        if key not in env:
            raise ConfigError(f"环境变量 {key} 未设置")
        return env[key]

    if isinstance(value, str):
        return VAR.sub(one, value)
    if isinstance(value, dict):
        return {k: expand(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [expand(v, env) for v in value]
    return value


SECRET = ("token", "password", "secret", "api_key")


def mask(data):
    """打日志/返回接口时脱敏：键名含敏感词就换成 ***。"""
    if isinstance(data, dict):
        return {k: ("***" if any(s in k.lower() for s in SECRET) else mask(v)) for k, v in data.items()}
    if isinstance(data, list):
        return [mask(v) for v in data]
    return data


@dataclass
class Env:
    name: str
    base_url: str
    variables: dict = field(default_factory=dict)


@dataclass
class Config:
    default_env: str
    envs: dict
    settings: dict = field(default_factory=dict)

    def env(self, name=None):
        key = name or self.default_env
        if key not in self.envs:
            raise ConfigError(f"环境 {key} 不存在")
        return self.envs[key]


def load(raw, env=None):
    """raw 是 yaml.safe_load 的结果；这里不碰文件，便于单测。"""
    if not isinstance(raw, dict):
        raise ConfigError("配置必须是一个映射")
    default = raw.get("default_env")
    if not default:
        raise ConfigError("缺少 default_env")
    envs_raw = raw.get("envs") or {}
    if not envs_raw:
        raise ConfigError("至少要有一个环境")
    if default not in envs_raw:
        raise ConfigError(f"default_env {default} 不在 envs 里")
    envs = {}
    for name, item in envs_raw.items():
        base = (item or {}).get("base_url", "")
        if not base:
            raise ConfigError(f"环境 {name} 缺少 base_url")
        envs[name] = Env(name=name, base_url=base, variables=expand((item or {}).get("variables") or {}, env))
    return Config(default_env=default, envs=envs, settings=raw.get("settings") or {})
