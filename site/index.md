---
layout: home

hero:
  name: AI 测试全栈
  text: 从 Python 到 AI 测试平台
  tagline: 一章一章往下叠的学习与工程记录：每章都有笔记、能跑的实操、可访问的页面
  actions:
    - theme: brand
      text: 从第一章开始
      link: /chapters/ch01
    - theme: alt
      text: 看实操代码
      link: /labs/

features:
  - title: 主线四段
    details: Python 与工程基础 → 接口自动化 → Web / APP 自动化 → 测试平台与 AI 能力。性能与 Agent 评估作为选修，不占主线。
  - title: 每章可跑
    details: 每章配一个 labs 目录，纯标准库优先，需要 key 的会自动降级到 mock，保证在干净环境里也能跑通。
  - title: 笔记先于代码
    details: 先把材料读成自己的话（含反例与常见错误），再动手写程序。
  - title: 持续部署
    details: 提交即部署。站点在 GitHub Pages，实操代码在仓库里，两边一一对应。
---

## 现在做到哪了

### 第一阶段 · Python 与工程基础

| 章 | 主题 | 笔记 | 实操 |
| --- | --- | --- | --- |
| 01 | 环境、第一个程序与基础语法 | [ch01](/chapters/ch01) | `labs/ch01-basics` |
| 02 | 条件、循环与函数入门 | [ch02](/chapters/ch02) | `labs/ch02-control-flow` |
| 03 | 列表、元组、字典与推导式 | [ch03](/chapters/ch03) | `labs/ch03-collections` |
| 04 | 函数进阶与内存模型 | [ch04](/chapters/ch04) | `labs/ch04-functions` |
| 05 | 面向对象与装饰器 | [ch05](/chapters/ch05) | `labs/ch05-oop` |
| 06 | 标准库、文件、JSON 与异常 | [ch06](/chapters/ch06) | `labs/ch06-stdlib` |
| 07 | 实战：测试数据工具箱 | [ch07](/chapters/ch07) | `labs/ch07-testkit` |

### 第二阶段 · 接口自动化

| 章 | 主题 | 笔记 | 实操 |
| --- | --- | --- | --- |
| 08 | 接口与接口测试基础 | [ch08](/chapters/ch08) | `labs/ch08-http-basics` |
| 09 | 用 AI 生成接口用例 | [ch09](/chapters/ch09) | `labs/ch09-ai-cases` |
| 10 | requests 发请求 | [ch10](/chapters/ch10) | `labs/ch10-requests` |
| 11 | 封装 HttpClient | [ch11](/chapters/ch11) | `labs/ch11-httpclient` |
| 12 | 用 pytest 组织接口用例 | [ch12](/chapters/ch12) | `labs/ch12-pytest-org` |
| 13 | 业务链路与数据准备 | [ch13](/chapters/ch13) | `labs/ch13-flows` |
| 14 | 报告与智能断言 | [ch14](/chapters/ch14) | `labs/ch14-report-assert` |
| 15 | 收口：一个能交给别人的框架 | [ch15](/chapters/ch15) | `labs/ch15-framework` |

### 第三阶段 · Web 自动化

| 章 | 主题 | 笔记 | 实操 |
| --- | --- | --- | --- |
| 16 | 浏览器自动化基础与选择器 | [ch16](/chapters/ch16) | `labs/ch16-web-basics` |

196 条 pytest 用例全绿，十六个实操都能单独运行：

```powershell
python -m pytest labs -q
python labs/ch16-web-basics/demo_basics.py
```

## 仓库结构

```
notes/     提炼后的学习笔记（知识库页面直接引用这些文件）
labs/      每章可运行的实操 + 单元测试
site/      VitePress 站点（就是你现在看的这个）
```

## 下一步

第三阶段：Web 与 APP 自动化。把 Playwright 与设备农场接进来，链路从「接口通」推进到「界面对」，再回到测试平台做统一编排。
