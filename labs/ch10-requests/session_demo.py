"""第 10 章实验：会话复用、超时、重试、流式下载、异常收敛。

跑法：``.venv\\Scripts\\python.exe labs\\ch10-requests\\session_demo.py``
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from mini_api import serve  # noqa: E402

DEFAULT_TIMEOUT = (3.05, 10)


def new_session(base: str, username: str = "alice", password: str = "secret") -> requests.Session:
    """登录一次，之后所有请求复用它。"""
    session = requests.Session()
    resp = session.post(f"{base}/api/login", json={"username": username, "password": password}, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    token = resp.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}", "X-Client": "shenle-ai-qa/ch10"})
    return session


def list_users(session: requests.Session, base: str, page: int = 1, size: int = 10) -> tuple[dict, float]:
    """返回 (json, 耗时毫秒)。"""
    start = time.perf_counter()
    resp = session.get(f"{base}/api/users", params={"page": page, "size": size}, timeout=DEFAULT_TIMEOUT)
    elapsed = (time.perf_counter() - start) * 1000
    resp.raise_for_status()
    return resp.json(), round(elapsed, 2)


def get_with_retry(session: requests.Session, url: str, *, attempts: int = 3, backoff: float = 0.0) -> requests.Response:
    """只对 5xx / 连接错误重试；4xx 立刻返回（重试没意义）。"""
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            resp = session.get(url, timeout=DEFAULT_TIMEOUT)
        except (requests.ConnectionError, requests.Timeout) as exc:
            last = exc
            if attempt == attempts:
                raise
            time.sleep(backoff * attempt)
            continue
        if resp.status_code < 500:
            resp.raise_for_status() if resp.status_code >= 400 else None
            return resp
        if attempt == attempts:
            return resp
        time.sleep(backoff * attempt)
    raise RuntimeError("unreachable") from last


def download(session: requests.Session, url: str, chunk: int = 7) -> bytes:
    """流式下载，按块拼；验证不会一次性读进内存。"""
    parts: list[bytes] = []
    with session.get(url, stream=True, timeout=DEFAULT_TIMEOUT) as resp:
        resp.raise_for_status()
        for piece in resp.iter_content(chunk_size=chunk):
            if piece:
                parts.append(piece)
    return b"".join(parts)


def safe_call(func, *args, **kwargs) -> tuple[bool, object, str]:
    """把异常收敛成 (ok, payload, error)，让用例只关心业务。"""
    try:
        return True, func(*args, **kwargs), ""
    except requests.HTTPError as exc:
        return False, None, f"HTTP {exc.response.status_code}: {exc.response.text[:120]}"
    except requests.Timeout:
        return False, None, "timeout"
    except requests.ConnectionError as exc:
        return False, None, f"connection_error: {exc.__class__.__name__}"


def search_users(session: requests.Session, base: str, keyword: str) -> str:
    """中文参数会被 requests 自动编码，这里返回实际发出的 URL 供观察。"""
    resp = session.get(f"{base}/api/users", params={"q": keyword, "page": 1}, timeout=DEFAULT_TIMEOUT)
    return resp.request.url


def main() -> None:
    with serve() as base:
        print(f"SUT: {base}")

        # 1) 每次新建会话 vs 复用会话
        start = time.perf_counter()
        for _ in range(5):
            new_session(base).get(f"{base}/api/users", timeout=DEFAULT_TIMEOUT)
        fresh = (time.perf_counter() - start) * 1000

        session = new_session(base)
        start = time.perf_counter()
        for _ in range(5):
            list_users(session, base)
        reused = (time.perf_counter() - start) * 1000
        print(f"5 次新建会话 {fresh:.0f}ms | 复用会话 {reused:.0f}ms")

        # 2) 分页与耗时
        data, ms = list_users(session, base, page=1, size=2)
        print(f"第一页 {len(data['items'])} 条，耗时 {ms}ms，total={data['total']}")

        # 3) 重试穿透 503
        flaky = get_with_retry(session, f"{base}/api/flaky?key=demo-retry", attempts=4, backoff=0.01)
        print(f"flaky 最终状态 {flaky.status_code} body={flaky.json()}")

        # 4) 4xx 不重试
        bad = session.get(f"{base}/api/users/9999", timeout=DEFAULT_TIMEOUT)
        print(f"查不存在用户: {bad.status_code}（不会重试）")

        # 5) 上传 + 流式下载
        session.post(f"{base}/api/upload", files={"file": ("big.txt", b"0123456789" * 3)}, timeout=DEFAULT_TIMEOUT)
        raw = download(session, f"{base}/api/files/big.txt")
        print(f"流式下载 {len(raw)} 字节，校验 {raw == b'0123456789' * 3}")

        # 6) 异常收敛
        ok, payload, err = safe_call(list_users, session, base, 1, 1000)
        print(f"safe_call -> ok={ok} err={err[:60]}")

        # 7) 中文参数编码
        print("中文参数实际 URL:", search_users(session, base, "张三"))


if __name__ == "__main__":
    main()
