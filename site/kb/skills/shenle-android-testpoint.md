---
title: shenle-android-testpoint
---

# shenle-android-testpoint

> 分组：**测试点分析**　来源：`.claude/skills/shenle-android-testpoint`

## 它是什么

安卓 UI 功能测试点分析生成技能（单批次版）。

## 核心功能

- `references/testpoint-template.md`：安卓页面测试点与全局公共模块的最终 Markdown 模板
- `references/testpoint-spec.md`：批次读取、分析边界、输出规则、公共模块策略和自检规范
- 用户说"分析安卓测试点" / "生成安卓测试点" / "安卓UI测试点分析" + **明确提供批次号**
- 用户提供具体 JSON 文件路径

## 怎么用

```bash
{工作空间}/                          ← 项目根目录
├── AI-信息采集/{批次号}/{模块路径}/      ← 输入
│   ├── json/dom_001.json
│   └── img/screenshot_001.png
```

## 产物与判读

本技能有明确输出物：安卓页面测试点分析 Markdown 与全局公共模块 Markdown。执行前必须按需读取：

- `references/testpoint-template.md`：安卓页面测试点与全局公共模块的最终 Markdown 模板
- `references/testpoint-spec.md`：批次读取、分析边界、输出规则、公共模块策略和自检规范

硬性要求：最终产物结构以 template 为准，生成行为和质量要求以 spec 为准。

## 常见失败模式

输入缺字段、路径不存在时会直接报错；先按 SKILL.md 核对入参。

## 相关

- 全文与下载：[Skills 库](/skills/shenle-android-testpoint)
- 返回：[Skills 手册](/kb/skills/)

## 评分（skill-judge）

本轮新补入，尚未逐维打分；评分脚本 `scripts/_score_skills.py`，口径见 `docs/skill-scores.md`。
