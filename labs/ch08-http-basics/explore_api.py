"""第 8 章实验：用 requests 摸清一个接口的「形状」。

跑法：``.venv\\Scripts\\python.exe labs\\ch08-http-basics\\explore_api.py``

不需要外网：SUT 是 labs/_shared/mini_api.py，在后台线程里起。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from mini_api import serve  # noqa: E402


def login(base: str, username: str = "alice", password: str = "secret") -> dict:
    resp = requests.post(f"{base}/api/login", json={"username": username, "password": password}, timeout=5)
    resp.raise_for_status()
    return {"Authorization": f"Bearer {resp.json()['token']}"}


def show(title: str, resp: requests.Response) -> None:
    body = resp.text
    if len(body) > 220:
        body = body[:220] + "..."
    print(f"\n## {title}")
    print(f"{resp.status_code} {resp.reason} | content-type={resp.headers.get('Content-Type')}")
    for key in ("Location", "Content-Length"):
        if key in resp.headers:
            print(f"  {key}: {resp.headers[key]}")
    print(f"  body: {body}")


def main() -> None:
    with serve() as base:
        print(f"SUT: {base}")

        # 1. 健康检查：最简单的一个接口
        show("健康检查", requests.get(f"{base}/api/health", timeout=5))

        # 2. 登录：密码错 → 401；正确 → 200 + token
        show("登录（密码错）", requests.post(f"{base}/api/login", json={"username": "alice", "password": "nope"}, timeout=5))
        auth = login(base)
        print(f"\ntoken 头: {auth['Authorization'][:24]}...")

        # 3. 带 token 查列表；不带 → 401
        show("用户列表（带 token）", requests.get(f"{base}/api/users", headers=auth, timeout=5))
        show("用户列表（无 token）", requests.get(f"{base}/api/users", timeout=5))

        # 4. 分页边界：size 超过 100 → 422
        show("分页 size=101", requests.get(f"{base}/api/users?page=1&size=101", headers=auth, timeout=5))

        # 5. 创建：201 + Location；重名 → 409
        created = requests.post(f"{base}/api/users", json={"name": "dave", "role": "tester"}, timeout=5)
        show("创建用户", created)
        show("再建同名", requests.post(f"{base}/api/users", json={"name": "dave"}, timeout=5))

        # 6. 缺必填 → 422，且 message 指明字段
        show("缺 name", requests.post(f"{base}/api/users", json={"role": "tester"}, timeout=5))

        # 7. 不存在 → 404
        show("查不存在的用户", requests.get(f"{base}/api/users/9999", headers=auth, timeout=5))

        # 8. 幂等：同一个 Idempotency-Key 发两次，返回同一个订单
        payload = {"items": [{"sku": "A-1", "qty": 2}]}
        headers = {**auth, "Idempotency-Key": "demo-key-001"}
        first = requests.post(f"{base}/api/orders", json=payload, headers=headers, timeout=5)
        second = requests.post(f"{base}/api/orders", json=payload, headers=headers, timeout=5)
        show("下单（第一次）", first)
        show("下单（同 key 第二次）", second)
        print(f"  两次 id 相同: {first.json()['id'] == second.json()['id']}")

        # 9. 业务状态机：付两次，第二次 409
        oid = first.json()["id"]
        show("支付", requests.post(f"{base}/api/orders/{oid}/pay", headers=auth, timeout=5))
        show("再支付", requests.post(f"{base}/api/orders/{oid}/pay", headers=auth, timeout=5))

        # 10. 文件上传 + 下载
        up = requests.post(f"{base}/api/upload", files={"file": ("note.txt", b"hello sut")}, timeout=5)
        show("上传", up)
        got = requests.get(f"{base}/api/files/note.txt", timeout=5)
        print(f"\n## 下载\n{got.status_code} bytes={len(got.content)} body={got.content!r}")

        print("\n---- 接口画像 ----")
        print(json.dumps({"base": base, "auth": "Bearer", "version": got.headers.get("server")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
