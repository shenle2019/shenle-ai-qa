---
title: shenle-web-cli 单跑记录
---

# shenle-web-cli 单跑记录

> 分组：**执行与定位**　手册：[shenle-web-cli](/kb/skills/web-cli)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 技能：`.claude/skills/` 下已注册；可安装的命令用 `pip install -e --no-deps` 注册为控制台脚本

## 本次调用

```bash
shenle-web-cli open https://example.com
```

## 真实输出

```text
shenle-web-cli 0.1.0
```

## 判读

- 退出正常、能看到命令自身的用法/版本，说明**注册与依赖这一层通了**。
- 产物形态：操作日志 + 截图；断言失败时给出视觉差异说明
- 需要人工或外部条件（点 SNAP、真机、视觉模型 key）的步骤，标注为「未能自动验证」，不写成功。

## 复现

```bash
.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q
```
