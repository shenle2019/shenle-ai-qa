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
        load(bad, {"QA_TOKEN": "t"})


def test_variables_are_expanded_at_load_time():
    cfg = load(raw(), {"QA_TOKEN": "secret-token"})
    assert cfg.env("local").variables["token"] == "secret-token"


def test_unknown_env_raises():
    cfg = load(raw(), {"QA_TOKEN": "t"})
    with pytest.raises(ConfigError, match="不存在"):
        cfg.env("prod")
