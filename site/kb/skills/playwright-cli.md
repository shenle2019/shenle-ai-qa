---
title: playwright-cli
---

# playwright-cli

> 分组：**通用能力**　来源：`.claude/skills/playwright-cli`

## 它是什么

直接用 Playwright 操作浏览器：导航、取属性、跑脚本、存会话。

技能自带的触发描述：

> Automate browser interactions, test web pages and work with Playwright tests.

## 核心功能

- 覆盖导航、点击、输入、断言、截图、trace
- 支持存/复用 `storage_state` 跳过登录
- 可跑任意 JS、可 mock 请求

## 怎么用

```bash
按 SKILL.md 里的参考文档选择动作
复杂场景参考 `references/spec-driven-testing.md`
```

## 产物与判读

截图、trace、执行日志

## 常见失败模式

选择器写死时页面一改就断，优先用 role / label

## 相关

- 单跑记录：[playwright-cli 单跑记录](/labs/skills/playwright-cli)
- 返回：[Skills 手册](/kb/skills/)
