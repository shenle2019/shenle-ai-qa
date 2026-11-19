# 测试全栈知识库

按学习顺序排列。每一章都对应笔记一份、`labs/` 目录一个、可访问页面一个。

## 第一阶段 · Python 与工程基础

| 章 | 主题 | 笔记 | 实操目录 |
| --- | --- | --- | --- |
| 01 | 环境、第一个程序与基础语法 | [ch01](/chapters/ch01) | `labs/ch01-basics` |
| 02 | 条件、循环与函数入门 | [ch02](/chapters/ch02) | `labs/ch02-control-flow` |
| 03 | 列表、元组、字典与推导式 | [ch03](/chapters/ch03) | `labs/ch03-collections` |
| 04 | 函数进阶与内存模型 | [ch04](/chapters/ch04) | `labs/ch04-functions` |
| 05 | 面向对象与装饰器 | [ch05](/chapters/ch05) | `labs/ch05-oop` |
| 06 | 标准库、文件、JSON 与异常 | [ch06](/chapters/ch06) | `labs/ch06-stdlib` |
| 07 | 实战：测试数据工具箱 | [ch07](/chapters/ch07) | `labs/ch07-testkit` |

## 第二阶段 · 接口自动化

| 章 | 主题 | 笔记 | 实操目录 |
| --- | --- | --- | --- |
| 08 | 接口与接口测试基础 | [ch08](/chapters/ch08) | `labs/ch08-http-basics` |
| 09 | 用 AI 生成接口用例 | [ch09](/chapters/ch09) | `labs/ch09-ai-cases` |
| 10 | requests 发请求 | [ch10](/chapters/ch10) | `labs/ch10-requests` |
| 11 | 封装 HttpClient | [ch11](/chapters/ch11) | `labs/ch11-httpclient` |
| 12 | 用 pytest 组织接口用例 | [ch12](/chapters/ch12) | `labs/ch12-pytest-org` |
| 13 | 业务链路与数据准备 | [ch13](/chapters/ch13) | `labs/ch13-flows` |
| 14 | 报告与智能断言 | [ch14](/chapters/ch14) | `labs/ch14-report-assert` |
| 15 | 收口：一个能交给别人的框架 | [ch15](/chapters/ch15) | `labs/ch15-framework` |

## 第三阶段 · Web 自动化

| 章 | 主题 | 笔记 | 实操目录 |
| --- | --- | --- | --- |
| 16 | 浏览器自动化基础与选择器 | [ch16](/chapters/ch16) | `labs/ch16-web-basics` |
| 17 | 页面对象（PO） | [ch17](/chapters/ch17) | `labs/ch17-po` |
| 18 | 定位集中管理 | [ch18](/chapters/ch18) | `labs/ch18-locators` |
| 19 | 前后置与浏览器复用 | [ch19](/chapters/ch19) | `labs/ch19-fixtures` |
| 20 | 数据驱动与多用例 | [ch20](/chapters/ch20) | `labs/ch20-data-driven` |
| 21 | 视觉回归与可访问性 | [ch21](/chapters/ch21) | `labs/ch21-visual` |
| 22 | 用 AI 生成 Web 用例 | [ch22](/chapters/ch22) | `labs/ch22-ai-cases` |
| 23 | 框架收口（CLI） | [ch23](/chapters/ch23) | `labs/ch23-framework` |

阶段验收：`python -m pytest labs -q` 全绿（当前 345 条）。

## 后续规划

- 第四阶段：APP 终端 UI 自动化（编号 24 起）
- 第五阶段：测试平台与 AI 能力（用例生成、失败归因、知识库）
- 选修：性能测试、Agent 与大模型评估

规划会随实际学习进度调整，以站点上的最新内容为准。

### 第四阶段 · APP 终端 UI 自动化

| 章 | 主题 | 笔记 | 实操 |
| --- | --- | --- | --- |
| 24 | ADB 与设备连接 | [ch24](/chapters/ch24) | labs/ch24-adb |
| 25 | 元素定位与窗口树 | [ch25](/chapters/ch25) | labs/ch25-locators |
| 26 | 页面对象与页面栈 | [ch26](/chapters/ch26) | labs/ch26-page-object |
| 27 | 手势与输入 | [ch27](/chapters/ch27) | labs/ch27-gestures |
| 28 | 数据驱动与多用例 | [ch28](/chapters/ch28) | labs/ch28-data-driven |
| 29 | 稳定性与失败留证 | [ch29](/chapters/ch29) | labs/ch29-stability |
| 30 | logcat 与崩溃定位 | [ch30](/chapters/ch30) | labs/ch30-logcat |
| 31 | 框架收口（APP CLI） | [ch31](/chapters/ch31) | labs/ch31-framework |
