---
title: shenle-test-plan-generator
---

# shenle-test-plan-generator

> 分组：**编排与计划**　来源：`.claude/skills/test-plan-generator`

## 它是什么

按流程与用例生成测试计划，含环境选择与编排扫描。

技能自带的触发描述：

> 对话式引导生成 AIQE 自动化测试计划（plan）。触发场景：用户说"生成测试计划"、"新建测试计划"、"做一个 plan"、"编排一个测试计划"、"把这些 flow 串成一个计划" 等。核心职责：扫描当前项目的 AI-自动化测试编排 目录，列出 ID+name 让用户挑选（或用户直接指定 ID/title），按用户

## 核心功能

- 扫描现有编排，避免重复计划
- 按环境挑变量（`env-key-selection`）
- 输出计划元信息模板（`plan-meta-template`）

## 怎么用

```bash
按 SKILL.md 给定用例集与环境，生成计划
计划落盘后用 test-runner 执行
```

## 产物与判读

`plans/<name>/plan.json` + 元信息

## 常见失败模式

环境变量缺失时计划能生成但执行前会失败

## 相关

- 单跑记录：[shenle-test-plan-generator 单跑记录](/labs/skills/test-plan-generator)
- 返回：[Skills 手册](/kb/skills/)
