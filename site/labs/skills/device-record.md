---
title: shenle-device-record 单跑记录
---

# shenle-device-record 单跑记录

> 分组：**录制采集**　手册：[shenle-device-record](/kb/skills/device-record)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 技能：`.claude/skills/` 下已注册；可安装的命令用 `pip install -e --no-deps` 注册为控制台脚本

## 本次调用

```bash
shenle-device-record record
```

## 真实输出

```text
shenle-device-record 0.1.0
```

## 判读

- 退出正常、能看到命令自身的用法/版本，说明**注册与依赖这一层通了**。
- 产物形态：截图 PNG + 层级 XML + 元信息 JSON（按用户要求本轮不做真机验证）
- 需要人工或外部条件（点 SNAP、真机、视觉模型 key）的步骤，标注为「未能自动验证」，不写成功。

## 复现

```bash
.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q
```
