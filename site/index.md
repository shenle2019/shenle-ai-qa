---
layout: home

hero:
  name: AI 测试全栈
  text: 从 Python 到 AI 测试平台
  tagline: 一章一章往下叠的学习与工程记录：每章都有笔记、能跑的实操、可访问的页面
  actions:
    - theme: brand
      text: 从第一章开始（知识库）
      link: /chapters/ch01
    - theme: alt
      text: 看实操记录
      link: /labs/
    - theme: alt
      text: 在线运行
      link: /labs/playground
    - theme: alt
      text: Skills 库
      link: /skills/

features:
  - title: 主线四段
    details: Python 与工程基础 → 接口自动化 → Web / APP 自动化 → 测试平台与 AI 能力。性能与 Agent 评估作为选修，不占主线。
  - title: 每章可跑
    details: 每章配一个 labs 目录（实操记录里可以单独跑），纯标准库优先，需要 key 的会自动降级到 mock，保证在干净环境里也能跑通。
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
| 17 | 页面对象（PO） | [ch17](/chapters/ch17) | `labs/ch17-po` |
| 18 | 定位集中管理（YAML） | [ch18](/chapters/ch18) | `labs/ch18-locators` |
| 19 | 前后置与浏览器复用 | [ch19](/chapters/ch19) | `labs/ch19-fixtures` |
| 20 | 数据驱动与多用例 | [ch20](/chapters/ch20) | `labs/ch20-data-driven` |
| 21 | 视觉回归与可访问性 | [ch21](/chapters/ch21) | `labs/ch21-visual` |
| 22 | 用 AI 生成 Web 用例 | [ch22](/chapters/ch22) | `labs/ch22-ai-cases` |
| 23 | 框架收口（CLI + 报告） | [ch23](/chapters/ch23) | `labs/ch23-framework` |

### 第四阶段 · APP 终端 UI 自动化

| 章 | 主题 | 笔记 | 实操 |
| --- | --- | --- | --- |
| 24 | ADB 与设备连接 | ch24 | labs/ch24-adb |
| 25 | 元素定位与窗口树 | ch25 | labs/ch25-locators |
| 26 | 页面对象与页面栈 | ch26 | labs/ch26-page-object |
| 27 | 手势与输入 | ch27 | labs/ch27-gestures |
| 28 | 数据驱动与多用例 | ch28 | labs/ch28-data-driven |
| 29 | 稳定性与失败留证 | ch29 | labs/ch29-stability |
| 30 | logcat 与崩溃定位 | ch30 | labs/ch30-logcat |
| 31 | 框架收口（APP CLI） | ch31 | labs/ch31-framework |

### 第五阶段 · 性能测试

| 章 | 主题 | 笔记 | 实操 |
| --- | --- | --- | --- |
| 32 | 性能测试基础与指标 | ch32 | labs/ch32-perf-basics |
| 33 | 压测场景与拐点 | ch33 | labs/ch33-scenarios |
| 34 | 压测脚本与权重 | ch34 | labs/ch34-scripts |
| 35 | 性能归因 | ch35 | labs/ch35-analyze |
| 36 | 中间件与链路指标 | ch36 | labs/ch36-middleware |
| 37 | 全链路与影子隔离 | ch37 | labs/ch37-chain |
| 38 | AI 辅助性能分析 | ch38 | labs/ch38-ai |
| 39 | 性能平台收口 | ch39 | labs/ch39-perf-platform |

480 条 pytest 用例（465 条离线通过 + 15 条真机用例在未接手机时自动跳过），四十六个实操都能单独运行：

```powershell
python -m pytest labs -q
python labs/ch23-framework/run.py --base-url http://127.0.0.1:8000
```

## 第六阶段 · AI 测试平台与工具

| 章 | 主题 | 实操目录 |
| --- | --- | --- |
| 40 | 平台架构与最小可用 | `labs/ch40-*` |
| 41 | 项目配置与环境上下文 | `labs/ch41-*` |
| 42 | 接口资产与一致性校验 | `labs/ch42-*` |
| 43 | 用例与关键字执行器 | `labs/ch43-executor` |
| 44 | 测试计划与异步执行 | `labs/ch44-plans` |
| 45 | 平台收口：报告、门槛与部署 | `labs/ch45-report` |
| 46 | 工具链：skills 与 CLI | `labs/ch46-toolchain` |

## 仓库结构

```
notes/     提炼后的学习笔记（知识库页面直接引用这些文件）
labs/      每章可运行的实操 + 单元测试
site/      VitePress 站点（就是你现在看的这个）
```

## 下一步

前六个阶段都写完了：Python 基础、接口、Web、APP（ch24–31，只用 adb，不引 Appium）、性能、平台与工具链。下一步是把六个阶段收口成一条流水线——一条命令从接口跑到界面、从压测跑到平台报告；再往后才是真机农场与多环境并行。
