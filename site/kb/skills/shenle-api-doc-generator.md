---
title: shenle-api-doc-generator
---

# shenle-api-doc-generator

> 分组：**用例生成**　来源：`.claude/skills/shenle-api-doc-generator`

## 它是什么

接口文档生成器。

## 核心功能

- 一次处理**一个** `raw.json` 文件
- 该文件里通常含**多个**接口条目（数组或单个 dict），每个条目 = 一个 MD
- 跨文件 / 跨批次处理不在本技能范围
- `references/apidoc-template.md`：最终 MD 文件结构与字段

## 怎么用

```bash
AI-信息采集/{batch}/raw01.json  →  AI-接口管理/{batch}/001_GET_xxx.md
shenle-api-doc-generator/
├── SKILL.md                          ← 本文件
├── references/
```

## 产物与判读

执行前必须按需读取：

- `references/apidoc-template.md`：最终 MD 文件结构与字段
- `references/apidoc-spec.md`：事实性约束、去重规则

## 常见失败模式

输入缺字段、路径不存在时会直接报错；先按 SKILL.md 核对入参。

## 相关

- 全文与下载：[Skills 库](/skills/shenle-api-doc-generator)
- 返回：[Skills 手册](/kb/skills/)

## 评分（skill-judge）

本轮新补入，尚未逐维打分；评分脚本 `scripts/_score_skills.py`，口径见 `docs/skill-scores.md`。
