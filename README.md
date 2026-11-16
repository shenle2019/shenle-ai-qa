# shenle-ai-qa

AI 测试全栈的学习与实践仓库：**笔记**（notes）、**可运行的实验**（labs）、**对外站点**（site）。

每一章都按同一个闭环推进：读透材料 → 提炼成笔记 → 写一个能跑的程序 → 跑通测试 → 截图 → 提交部署。

## 结构

```
notes/     按章整理的学习笔记（自己的话，不是原文摘录）
labs/      每章的实验代码，独立可跑，带 pytest 测试
site/      VitePress 站点，聚合笔记与实验入口
```

## 章节进度

### 第一阶段 · Python 与工程基础

| 章 | 主题 | 笔记 | 实验 |
| --- | --- | --- | --- |
| 01 | 环境、第一个程序与基础语法 | [笔记](notes/ch01-basics.md) | [labs/ch01-basics](labs/ch01-basics) |
| 02 | 条件、循环与函数入门 | [笔记](notes/ch02-control-flow.md) | [labs/ch02-control-flow](labs/ch02-control-flow) |
| 03 | 列表、元组、字典与推导式 | [笔记](notes/ch03-collections.md) | [labs/ch03-collections](labs/ch03-collections) |
| 04 | 函数进阶与内存模型 | [笔记](notes/ch04-functions.md) | [labs/ch04-functions](labs/ch04-functions) |
| 05 | 面向对象与装饰器 | [笔记](notes/ch05-oop.md) | [labs/ch05-oop](labs/ch05-oop) |
| 06 | 标准库、文件、JSON 与异常 | [笔记](notes/ch06-stdlib.md) | [labs/ch06-stdlib](labs/ch06-stdlib) |
| 07 | 实战：测试数据工具箱 | [笔记](notes/ch07-testkit.md) | [labs/ch07-testkit](labs/ch07-testkit) |

### 第二阶段 · 接口自动化

| 章 | 主题 | 笔记 | 实验 |
| --- | --- | --- | --- |
| 08 | 接口与接口测试基础 | [笔记](notes/ch08-http-basics.md) | [labs/ch08-http-basics](labs/ch08-http-basics) |
| 09 | 用 AI 生成接口用例 | [笔记](notes/ch09-ai-cases.md) | [labs/ch09-ai-cases](labs/ch09-ai-cases) |
| 10 | requests 发请求 | [笔记](notes/ch10-requests.md) | [labs/ch10-requests](labs/ch10-requests) |
| 11 | 封装 HttpClient | [笔记](notes/ch11-httpclient.md) | [labs/ch11-httpclient](labs/ch11-httpclient) |
| 12 | 用 pytest 组织接口用例 | [笔记](notes/ch12-pytest-org.md) | [labs/ch12-pytest-org](labs/ch12-pytest-org) |
| 13 | 业务链路与数据准备 | [笔记](notes/ch13-flows.md) | [labs/ch13-flows](labs/ch13-flows) |
| 14 | 报告与智能断言 | [笔记](notes/ch14-report-assert.md) | [labs/ch14-report-assert](labs/ch14-report-assert) |
| 15 | 收口：一个能交给别人的框架 | [笔记](notes/ch15-framework.md) | [labs/ch15-framework](labs/ch15-framework) |

阶段验收：`python -m pytest labs -q` → 184 passed。

第二阶段的实验跑在同一个内存态被测服务上（`labs/_shared/mini_api.py`），只依赖 `requests`。

## 本地开发

```powershell
# 跑全部实验测试
.venv\Scripts\python.exe -m pytest labs -q

# 单个实验
.venv\Scripts\python.exe labs\ch08-http-basics\explore_api.py

# 框架入口（跑用例 + 出 HTML 报告）
.venv\Scripts\python.exe labs\ch15-framework\run.py --env local --report

# 站点
cd site
npm ci
npm run dev        # http://localhost:5173
npm run build      # 产物在 site/.vitepress/dist
```

## 约定

- 笔记只写自己消化过的内容，不抄原文、不写来源。
- 实验一律可在干净环境跑起来：优先标准库，依赖少而明确，密钥只从环境变量读，缺密钥时降级到本地 mock。
- 每个 lab 带 `test_*.py`，`python -m pytest labs -q` 必须全绿。
- 每章合并前跑一次测试并更新站点。

站点地址：https://shenle2019.github.io/shenle-ai-qa/
