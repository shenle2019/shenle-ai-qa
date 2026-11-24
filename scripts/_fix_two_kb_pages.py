"""把 api-cli / device-record 两页手册改成与实际技能一致（来源、真跑过的命令、BOM 坑）。"""

from __future__ import annotations

from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "site" / "kb" / "skills"

API = """---
title: shenle-api-cli
---

# shenle-api-cli

> 分组：**执行与定位**　来源：`.claude/skills/shenle-api-cli`

## 它是什么

命令行发接口请求、抽字段、断言，替代 curl 给 AI 用。装在仓库里，用 `.venv\\Scripts\\shenle-api-cli.exe` 调用。

## 核心功能

- `send` 发请求并把 request / response 落盘到 `%TEMP%/shenle-api-results/`
- `call` 一步 send + extract，JSONPath 直接取字段
- `extract` 从已有 result 文件里取字段，`assert` 用自然语言断言（需 AI 配置）

## 怎么用

```bash
# 发一次请求，落盘结果
shenle-api-cli send req.json

# 发请求并直接取字段（推荐）
shenle-api-cli call req.json --field "$.full_name"

# 4xx 也要继续取值
shenle-api-cli call req.json --field "$.msg" --no-fail-on-status
```

`req.json` 形如 `{"method": "GET", "url": "https://...", "headers": [{"name": "Accept", "value": "application/json"}]}`。

## 产物与判读

`%TEMP%/shenle-api-results/<时间戳>-<hash>.json`，含 `request` / `response`（status、headers、body_text、body_json、elapsed_ms）/ `meta`。
`[OK] send: 200 GET <url> elapsed=676ms result_file=...` 说明请求真的发出去了；断言要看状态码与字段，光有 `[OK]` 不算通过。

## 常见失败模式

- `Unexpected UTF-8 BOM`：`req.json` 被 PowerShell 写成带 BOM 的 UTF-8，改用 `Set-Content -Encoding utf8NoBOM` 或 Python 写文件。
- `JSONPath 未匹配`：字段路径写错或 body 不是 JSON，改 `--field "返回的 X"` 走自然语言。
- `[FAIL] send: 网络请求失败`：先确认 URL 可达，再调 `--timeout`。

## 相关

- 单跑记录：[shenle-api-cli 单跑记录](/labs/skills/api-cli)
- 全文与下载：[Skills 库](/skills/shenle-api-cli)
- 返回：[Skills 手册](/kb/skills/)
"""

DEVICE = """---
title: shenle-device-record
---

# shenle-device-record

> 分组：**录制采集**　来源：`.claude/skills/shenle-device-record`

## 它是什么

连安卓设备，抓当前屏幕与界面层级，落盘成结构化快照，供后续定位与用例生成。

## 核心功能

- `record` 单次抓取，`serve` 起本地服务供连续采集
- 截图 PNG + `uiautomator` 层级 XML 一起存，定位信息不丢
- 支持 `-s <serial>` 指定设备，多机时分流

## 怎么用

```bash
adb devices                       # 确认状态是 device，不是 unauthorized
shenle-device-record record       # 抓一屏：截图 + 层级 + 元信息
shenle-device-record serve        # 连续采集，本地起服务
shenle-device-record record -s FA7B11A03073
```

## 产物与判读

时间戳批次目录下 `img/` 截图与 `json/` 层级各一份。判读看三点：设备是 `device`、批次目录是新的、JSON 里 `elements` 与截图对得上。

## 常见失败模式

- `device unauthorized`：手机上没点允许调试，不点永远不会变。
- `more than one device/emulator`：多设备没带 `-s`。
- 层级只有系统 UI：锁屏或系统弹窗盖住了，先解锁关弹窗再采。

## 相关

- 单跑记录：[shenle-device-record 单跑记录](/labs/skills/device-record)
- 全文与下载：[Skills 库](/skills/shenle-device-record)
- 返回：[Skills 手册](/kb/skills/)
"""

for name, body in (("api-cli", API), ("device-record", DEVICE)):
    path = KB / f"{name}.md"
    path.write_text(body, encoding="utf-8")
    print(f"{name}.md 重写 {len(body.splitlines())} 行")
