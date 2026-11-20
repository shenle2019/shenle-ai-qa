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

469 条 pytest 用例（15 条真机用例在未接手机时自动跳过），四十五个实操都能单独运行：

```powershell
python -m pytest labs -q
python labs/ch23-framework/run.py --base-url http://127.0.0.1:8000
```

## 仓库结构

```
notes/     提炼后的学习笔记（知识库页面直接引用这些文件）
labs/      每章可运行的实操 + 单元测试
site/      VitePress 站点（就是你现在看的这个）
```

## 下一步

第四阶段：APP 终端 UI 自动化。把 Appium 与设备农场接进来，把「接口通 → 界面对」扩到移动端，再回到测试平台做统一编排。
| ch43 | 用例与关键字执行器 | `labs/ch43-executor` |
| ch44 | 测试计划与异步执行 | `labs/ch44-plans` |
| ch45 | 平台收口：报告、门槛与部署 | `labs/ch45-report` |
