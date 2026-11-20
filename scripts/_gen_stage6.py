# -*- coding: utf-8 -*-
"""生成 41–43 章的 labs / notes / 站点页。"""

from pathlib import Path

ROOT = Path(".")


def w(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + "\n", encoding="utf-8")


CFG_PY = r'''
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
'''

w("labs/ch41-config/config.py", CFG_PY)

w("labs/ch41-config/test_config.py", r'''
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import ConfigError, expand, load, mask  # noqa: E402


def raw():
    return {
        "default_env": "local",
        "settings": {"timeout": 5},
        "envs": {
            "local": {"base_url": "http://127.0.0.1:8010", "variables": {"user": "alice", "token": "${QA_TOKEN}"}},
            "staging": {"base_url": "https://stg.example.com", "variables": {}},
        },
    }


def test_expand_replaces_placeholder():
    assert expand("${QA_TOKEN}", {"QA_TOKEN": "abc"}) == "abc"


def test_expand_missing_var_raises():
    with pytest.raises(ConfigError, match="未设置"):
        expand({"token": "${NOPE}"}, {})


def test_mask_hides_secrets_only():
    assert mask({"user": "alice", "token": "t"}) == {"user": "alice", "token": "***"}


def test_load_returns_env_by_name():
    cfg = load(raw(), {"QA_TOKEN": "t"})
    assert cfg.env("staging").base_url == "https://stg.example.com"
    assert cfg.env().name == "local"


def test_default_env_must_exist():
    bad = raw()
    bad["default_env"] = "prod"
    with pytest.raises(ConfigError, match="不在 envs"):
        load(bad, {})


def test_env_requires_base_url():
    bad = raw()
    bad["envs"]["staging"] = {}
    with pytest.raises(ConfigError, match="缺少 base_url"):
        load(bad, {})


def test_variables_are_expanded_at_load_time():
    cfg = load(raw(), {"QA_TOKEN": "secret-token"})
    assert cfg.env("local").variables["token"] == "secret-token"


def test_unknown_env_raises():
    cfg = load(raw(), {"QA_TOKEN": "t"})
    with pytest.raises(ConfigError, match="不存在"):
        cfg.env("prod")
''')

w("labs/ch42-assets/assets.py", r'''
"""第 42 章：接口资产。从精简 spec 生成可维护的接口清单，并做一次一致性校验。"""

from __future__ import annotations

from dataclasses import dataclass, field

METHODS = ("get", "post", "put", "patch", "delete")


@dataclass
class Endpoint:
    method: str
    path: str
    summary: str = ""
    params: list = field(default_factory=list)
    body_required: bool = False

    @property
    def key(self):
        return f"{self.method.upper()} {self.path}"


class SpecError(ValueError):
    pass


def parse_spec(spec):
    """spec 形如 {base_url, paths: {'/x': {'get': {...}}}}。"""
    if not isinstance(spec, dict) or "paths" not in spec:
        raise SpecError("spec 缺少 paths")
    base = spec.get("base_url", "")
    if not base.startswith(("http://", "https://")):
        raise SpecError("base_url 必须以 http 开头")
    out = []
    for path, item in (spec["paths"] or {}).items():
        if not path.startswith("/"):
            raise SpecError(f"路径必须以 / 开头：{path}")
        for method, op in (item or {}).items():
            if method.lower() not in METHODS:
                raise SpecError(f"不支持的方法：{method}")
            out.append(
                Endpoint(
                    method=method.upper(),
                    path=path,
                    summary=(op or {}).get("summary", ""),
                    params=list((op or {}).get("params") or []),
                    body_required=bool((op or {}).get("body")),
                )
            )
    return base, sorted(out, key=lambda e: (e.path, e.method))


def validate(endpoints):
    """返回问题清单；空列表代表通过。"""
    problems = []
    seen = {}
    for item in endpoints:
        key = item.key
        if key in seen:
            problems.append(f"重复接口：{key}")
        seen[key] = True
        if item.method in ("POST", "PUT", "PATCH") and not item.body_required:
            problems.append(f"{key} 是写接口但没有 body 定义")
        if "{" in item.path and not item.params:
            problems.append(f"{key} 路径带变量却没有声明 params")
        if item.summary == "":
            problems.append(f"{key} 缺少 summary")
    return problems


def to_markdown(endpoints, base=""):
    lines = [f"接口清单（{len(endpoints)} 个，base={base}）", "", "| 方法 | 路径 | 说明 |", "| --- | --- | --- |"]
    lines += [f"| {e.method} | `{e.path}` | {e.summary or '-'} |" for e in endpoints]
    return "\n".join(lines) + "\n"
''')

w("labs/ch42-assets/test_assets.py", r'''
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assets import SpecError, parse_spec, to_markdown, validate  # noqa: E402

SPEC = {
    "base_url": "http://127.0.0.1:8010",
    "paths": {
        "/api/users": {
            "get": {"summary": "用户列表", "params": ["page"]},
            "post": {"summary": "建用户", "body": {"name": "string"}},
        },
        "/api/users/{id}": {"get": {"summary": "用户详情", "params": ["id"]}},
    },
}


def test_parse_returns_sorted_endpoints():
    base, items = parse_spec(SPEC)
    assert base == "http://127.0.0.1:8010"
    assert [i.key for i in items] == ["GET /api/users", "POST /api/users", "GET /api/users/{id}"]


def test_parse_rejects_bad_base_url():
    with pytest.raises(SpecError, match="base_url"):
        parse_spec({"base_url": "127.0.0.1", "paths": {}})


def test_parse_rejects_unknown_method():
    with pytest.raises(SpecError, match="不支持的方法"):
        parse_spec({"base_url": "http://x", "paths": {"/a": {"fetch": {}}}})


def test_parse_rejects_relative_path():
    with pytest.raises(SpecError, match="必须"):
        parse_spec({"base_url": "http://x", "paths": {"api/a": {}}})


def test_validate_clean_spec_passes():
    _, items = parse_spec(SPEC)
    assert validate(items) == []


def test_validate_flags_missing_body_and_params():
    _, items = parse_spec(
        {
            "base_url": "http://x",
            "paths": {
                "/api/w": {"post": {"summary": "写"}},
                "/api/{id}": {"get": {"summary": "详情"}},
            },
        }
    )
    problems = validate(items)
    assert any("没有 body" in p for p in problems)
    assert any("没有声明 params" in p for p in problems)


def test_validate_flags_duplicate_and_missing_summary():
    _, items = parse_spec({"base_url": "http://x", "paths": {"/a": {"get": {}}}})
    items.append(items[0])
    problems = validate(items)
    assert any("重复接口" in p for p in problems)
    assert any("缺少 summary" in p for p in problems)


def test_markdown_lists_rows():
    base, items = parse_spec(SPEC)
    text = to_markdown(items, base)
    assert "| GET | `/api/users` | 用户列表 |" in text
    assert "接口清单（3 个" in text
''')

print("ch41-42 written")
