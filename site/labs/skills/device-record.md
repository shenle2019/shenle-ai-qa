---
title: shenle-device-record 单跑记录
---

# shenle-device-record 单跑记录

> 分组：**录制采集**　手册：[shenle-device-record](/kb/skills/device-record)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 安装：`.venv\Scripts\python.exe -m pip install -e labs\ch46-toolchain\apps\shenle-device-record --no-deps`
- 入口：`.venv\Scripts\python.exe -m shenle_device_record`（这个包有 `__main__`）或 `shenle-device-record.exe`

## 本次调用

```bash
.venv\Scripts\python.exe -m shenle_device_record --version
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
