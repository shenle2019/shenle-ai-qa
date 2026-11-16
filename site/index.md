---
layout: home

hero:
  name: AI 测试全栈
  text: 从 Python 到 AI 测试平台
  tagline: 一条章一章往下叠的学习与工程记录：每章都有笔记、能跑的实验、可访问的页面
  actions:
    - theme: brand
      text: 从第一章开始
      link: /chapters/ch01
    - theme: alt
      text: 看实验代码
      link: /labs/

features:
  - title: 主线四段
    details: Python 与工程基础 → 接口自动化 → Web / APP 自动化 → 测试平台与 AI 能力。性能与 Agent 评估作为选修，不占主线。
  - title: 每章可跑
    details: 每章配一个 labs 目录，纯标准库优先，需要 key 的会自动降级到 mock，保证在干净环境里也能跑通。
  - title: 笔记先于代码
    details: 先把材料读成自己的话（含反例与常见错误），再动手写程序。引用原文时标清来源。
  - title: 持续部署
    details: 提交即部署。站点在 GitHub Pages，实验代码在仓库里，两边一一对应。
---

## 现在做到哪了

| 章 | 主题 | 笔记 | 实验 |
| --- | --- | --- | --- |
| 01 | Python 入门与第一个 AI 生成程序 | [笔记](/chapters/ch01) | [labs/ch01-hello-ai](https://github.com/shenle2019/shenle-ai-qa/tree/main/labs/ch01-hello-ai) |

## 仓库结构

```
notes/     提炼后的学习笔记
labs/      每章可运行的实验
site/      VitePress 站点（就是你现在看的这个）
corpus/    语雀知识库的本地语料与索引
```

## 下一步

02 接口自动化：从单接口调试到场景编排，把 `labs/ch02` 做成一个能跑的迷你接口测试框架，再接上第一章的 AI 生成能力。
