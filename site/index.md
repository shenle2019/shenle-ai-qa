---
layout: home

hero:
  name: AI 测试全栈
  text: 从 Python 到 AI 测试平台
  tagline: 一章一章往下叠的学习与工程记录：每章都有笔记、能跑的实验、可访问的页面
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
    details: 先把材料读成自己的话（含反例与常见错误），再动手写程序。
  - title: 持续部署
    details: 提交即部署。站点在 GitHub Pages，实验代码在仓库里，两边一一对应。
---

## 现在做到哪了

| 章 | 主题 | 笔记 | 实验 |
| --- | --- | --- | --- |
| 01 | 环境、第一个程序与基础语法 | [ch01](/chapters/ch01) | `labs/ch01-basics` |
| 02 | 条件、循环与函数入门 | [ch02](/chapters/ch02) | `labs/ch02-control-flow` |
| 03 | 列表、元组、字典与推导式 | [ch03](/chapters/ch03) | `labs/ch03-collections` |
| 04 | 函数进阶与内存模型 | [ch04](/chapters/ch04) | `labs/ch04-functions` |
| 05 | 面向对象与装饰器 | [ch05](/chapters/ch05) | `labs/ch05-oop` |
| 06 | 标准库、文件、JSON 与异常 | [ch06](/chapters/ch06) | `labs/ch06-stdlib` |
| 07 | 实战：测试数据工具箱 | [ch07](/chapters/ch07) | `labs/ch07-testkit` |

93 条 pytest 用例全绿，七个实验都能单独运行：

```powershell
python -m pytest labs -q
python labs/ch07-testkit/demo.py
```

## 仓库结构

```
notes/     提炼后的学习笔记（章节页直接引用这些文件）
labs/      每章可运行的实验 + 单元测试
site/      VitePress 站点（就是你现在看的这个）
```

## 下一步

第二阶段：接口自动化。从单接口调试开始，把请求、断言、数据驱动、场景编排一层层叠上去，最后接上 AI 生成用例与失败归因。
