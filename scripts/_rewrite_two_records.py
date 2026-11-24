"""把 api-cli / device-record 的单跑记录换成真跑出来的输出。"""

from __future__ import annotations

from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "site" / "labs" / "skills"

API = """---
title: shenle-api-cli 单跑记录
---

# shenle-api-cli 单跑记录

> 分组：**执行与定位**　手册：[shenle-api-cli](/kb/skills/api-cli)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 安装：`.venv\\Scripts\\python.exe -m pip install -e labs\\ch46-toolchain\\apps\\shenle-api-cli --no-deps`
- 入口：`.venv\\Scripts\\shenle-api-cli.exe`（这个包没有 `__main__`，`python -m shenle_api_cli` 会报错，必须用 exe）

## 本次调用

```bash
# 1) 版本
shenle-api-cli --version

# 2) 真发一次 GET（req.json 用 Python 以无 BOM 的 UTF-8 写）
shenle-api-cli send %TEMP%\\req_demo.json

# 3) 发请求并直接取字段
shenle-api-cli call %TEMP%\\req_gh.json --field "$.full_name"
```

## 真实输出

```text
shenle-api-cli 0.2.0

[OK] send: 200 GET https://shenle2019.github.io/shenle-ai-qa/ elapsed=676ms result_file=C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\shenle-api-results\\20261124-143042-3ddf5957.json

[OK] call: status=200 method=GET elapsed=655ms name=value value=shenle2019/shenle-ai-qa result_file=C:\\Users\\ADMINI~1\\AppData\\Local\\Temp\\shenle-api-results\\20261124-143051-ca79da9c.json
```

## 判读

- 三条都退出正常：`--version` 说明装好了，`send` 说明真发出了请求并落盘，`call` 说明 JSONPath 取到了值。
- 产物形态：`%TEMP%\\shenle-api-results/<时间戳>-<hash>.json`，含 request / response / meta。
- 中途真踩到一个坑：用 PowerShell `Set-Content -Encoding utf8` 写 req.json 会带 BOM，工具报 `Unexpected UTF-8 BOM`；改成 Python 以 `encoding='utf-8'` 写就好了，这条已补进技能报错表。

## 复现

```bash
.venv/Scripts/python.exe -m pip install -e labs/ch46-toolchain/apps/shenle-api-cli --no-deps
.venv/Scripts/shenle-api-cli.exe --version
```
"""

DEVICE = """---
title: shenle-device-record 单跑记录
---

# shenle-device-record 单跑记录

> 分组：**录制采集**　手册：[shenle-device-record](/kb/skills/device-record)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 安装：`.venv\\Scripts\\python.exe -m pip install -e labs\\ch46-toolchain\\apps\\shenle-device-record --no-deps`
- 入口：`.venv\\Scripts\\python.exe -m shenle_device_record`（这个包有 `__main__`）或 `shenle-device-record.exe`

## 本次调用

```bash
.venv\\Scripts\\python.exe -m shenle_device_record --version
```

## 真实输出

```text
shenle-device-record 0.1.0
```

## 判读

- 退出正常、版本打印出来，说明**安装与入口这一层通了**。
- 真机采集（`record` / `serve`）本轮**没有跑**：需要一台开着 USB 调试的安卓设备，本次没有接入，因此不写「采集成功」。
- 产物形态（来自技能文档，未在本轮验证）：时间戳批次目录下 `img/` 截图 + `json/` 层级 + 元信息。

## 复现

```bash
.venv/Scripts/python.exe -m pip install -e labs/ch46-toolchain/apps/shenle-device-record --no-deps
.venv/Scripts/python.exe -m shenle_device_record --version
```

接上设备后追加：`adb devices` 确认状态为 `device`，再跑 `shenle-device-record record`。
"""

for name, body in (("api-cli", API), ("device-record", DEVICE)):
    path = LABS / f"{name}.md"
    path.write_text(body, encoding="utf-8")
    print(f"{name}.md 重写 {len(body.splitlines())} 行")
