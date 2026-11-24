"""线上核验：站点 Skills 库 21 项 + 两页 + zip；平台两篇手册能下 zip。"""

from __future__ import annotations

import json
import urllib.request

SITE = "https://shenle2019.github.io/shenle-ai-qa"
API = "https://ai-qa-lab-production.up.railway.app"


def head(url: str) -> tuple[int, str, int]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
        return resp.status, resp.headers.get("content-type", ""), len(body)


for path in (
    "/skills/",
    "/skills/shenle-api-cli",
    "/skills/shenle-api-cli.zip",
    "/skills/shenle-device-record",
    "/skills/shenle-device-record.zip",
    "/kb/skills/api-cli",
    "/kb/skills/device-record",
):
    try:
        status, ctype, size = head(SITE + path)
        print(f"站点 {path:44s} {status} {ctype[:30]:32s} {size}")
    except Exception as exc:  # noqa: BLE001
        print(f"站点 {path:44s} ERR {exc}")

key = "dev-local-key"
try:
    req = urllib.request.Request(API + "/api/platform/skill-docs", headers={"X-API-Key": key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    print("平台 docs:", len(data))
    for item in data:
        if item["slug"] in ("api-cli", "device-record", "web-cli"):
            print("  ", item["slug"], "has_zip=", item.get("has_zip"))
except Exception as exc:  # noqa: BLE001
    print("平台 docs ERR", exc)

for slug in ("api-cli", "device-record"):
    try:
        req = urllib.request.Request(
            f"{API}/api/platform/skill-docs/{slug}/download", headers={"X-API-Key": key}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
        print(f"平台 {slug} zip: {resp.status} {resp.headers.get('content-type')} {len(body)}B 头两字节={body[:2]!r}")
    except Exception as exc:  # noqa: BLE001
        print(f"平台 {slug} zip ERR {exc}")
