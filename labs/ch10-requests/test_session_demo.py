"""第 10 章的测试：会话、重试、超时、编码、流式下载、异常收敛。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mini_api import serve  # noqa: E402
from session_demo import (  # noqa: E402
    DEFAULT_TIMEOUT,
    download,
    get_with_retry,
    list_users,
    new_session,
    safe_call,
    search_users,
)


@pytest.fixture(scope="module")
def base():
    with serve() as url:
        yield url


@pytest.fixture(scope="module")
def session(base):
    return new_session(base)


def test_session_carries_token_and_custom_header(base, session):
    resp = session.get(f"{base}/api/users", timeout=DEFAULT_TIMEOUT)
    assert resp.status_code == 200
    assert session.headers["X-Client"] == "shenle-ai-qa/ch10"


def test_fresh_session_without_token_gets_401(base):
    fresh = requests.Session()
    assert fresh.get(f"{base}/api/users", timeout=DEFAULT_TIMEOUT).status_code == 401


def test_list_users_returns_elapsed(session, base):
    data, ms = list_users(session, base, page=1, size=2)
    assert data["size"] == 2
    assert isinstance(ms, float) and ms >= 0


def test_retry_survives_503(session, base):
    resp = get_with_retry(session, f"{base}/api/flaky?key=test-retry", attempts=4, backoff=0.0)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_retry_gives_up_and_returns_last_5xx(session, base):
    resp = get_with_retry(session, f"{base}/api/flaky?key=give-up", attempts=1, backoff=0.0)
    assert resp.status_code == 503


def test_404_is_not_retried(session, base):
    with pytest.raises(requests.HTTPError):
        get_with_retry(session, f"{base}/api/users/9999", attempts=3, backoff=0.0)


def test_timeout_is_raised_as_timeout():
    # 10.255.255.1 是不可路由地址，连接会一直挂着，必然触发超时
    with pytest.raises(requests.Timeout):
        requests.get("http://10.255.255.1:81/api/health", timeout=(0.3, 0.3))


def test_chinese_params_are_url_encoded(session, base):
    url = search_users(session, base, "张三")
    assert "%E5%BC%A0%E4%B8%89" in url


def test_stream_download_matches_uploaded_bytes(session, base):
    payload = b"0123456789" * 3
    up = session.post(f"{base}/api/upload", files={"file": ("s.txt", payload)}, timeout=DEFAULT_TIMEOUT)
    assert up.status_code == 201
    assert download(session, f"{base}/api/files/s.txt") == payload


def test_safe_call_turns_http_error_into_tuple(session, base):
    ok, payload, err = safe_call(list_users, session, base, 1, 1000)
    assert ok is False
    assert payload is None
    assert "HTTP 422" in err


def test_safe_call_passes_through_success(session, base):
    ok, payload, err = safe_call(list_users, session, base, 1, 5)
    assert ok is True and err == ""
    data, _ms = payload
    assert data["size"] == 5
