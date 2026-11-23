---
title: shenle-test-flow-builder 单跑记录
---

# shenle-test-flow-builder 单跑记录

> 分组：**编排与计划**　手册：[shenle-test-flow-builder](/kb/skills/test-flow-builder)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 技能：`.claude/skills/` 下已注册；可安装的命令用 `pip install -e --no-deps` 注册为控制台脚本

## 本次调用

```bash
按 SKILL.md 提示，把快照目录交给它生成 flow
```

## 真实输出

```text
该技能由 Agent 按 SKILL.md 驱动，无独立命令；文档自检 -> SKILL.md: 638 行 / 12 个二级标题
```

## 判读

- 退出正常、能看到命令自身的用法/版本，说明**注册与依赖这一层通了**。
- 产物形态：`flows/*.json`（步骤、数据引用、断言）
- 需要人工或外部条件（点 SNAP、真机、视觉模型 key）的步骤，标注为「未能自动验证」，不写成功。

## 复现

```bash
.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q
```
