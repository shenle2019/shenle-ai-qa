# -*- coding: utf-8 -*-
"""重构 site/labs/index.md：

1. 补上缺失的「第四阶段 · APP 终端 UI 自动化」（ch24–31）
2. 把散落在文件末尾的 ch33–39 表格行收回第五阶段表
3. 统一第六阶段表头为五列
4. 追加「第七阶段 · AI 应用与 Agent 专项测试」（ch47–54）
5. 合计改成真实数字（555 通过 + 15 跳过 = 570）
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "site" / "labs" / "index.md"

text = PAGE.read_text(encoding="utf-8")
lines = text.splitlines()

# 1) 摘掉文件末尾的孤儿行（ch33–39），并记录
orphan_prefixes = tuple(f"| {n} |" for n in range(33, 40))
tail_rows = [ln for ln in lines if ln.startswith(orphan_prefixes)]
lines = [ln for ln in lines if not ln.startswith(orphan_prefixes)]
text = "\n".join(lines).rstrip() + "\n"

# 2) 第五阶段表里只有 ch32，把 33–39 接回去
ch32_anchor = "| 32 | labs/ch32-perf-basics | metrics_demo.py | 分位值、TPS、错误率、Little's Law | 11 |"
assert ch32_anchor in text, "第五阶段 ch32 行没找到"
text = text.replace(ch32_anchor, ch32_anchor + "\n" + "\n".join(tail_rows), 1)

# 3) 补第四阶段（ch24–31），插在第五阶段标题前
stage4 = """## 第四阶段 · APP 终端 UI 自动化

| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- | --- |
| 24 | `labs/ch24-adb` | `adb.py` | adb 命令、设备选择、截图、层级 dump | 6 |
| 25 | `labs/ch25-locators` | `ui_tree.py` | 层级解析、按 text/id/类名定位、控件等待 | 8 |
| 26 | `labs/ch26-page-object` | `pages.py` | 页面对象、动作返回下一页、登录链 | 7 |
| 27 | `labs/ch27-gestures` | `gestures.py` | 点击、长按、滑动、输入、中文输入法坑 | 9 |
| 28 | `labs/ch28-data-driven` | `runner.py` + `cases.yaml` | 用例外部化、失败不中断、汇总 | 8 |
| 29 | `labs/ch29-stability` | `retry.py` | 重试、隐式等待、幂等断言 | 8 |
| 30 | `labs/ch30-logcat` | `logcat.py` | logcat 过滤、崩溃与 ANR 判定 | 8 |
| 31 | `labs/ch31-framework` | `app_framework.py` | 配置驱动 CLI、退出码、Markdown 报告 | 8 |

## 第五阶段 · 性能测试"""
text = text.replace("## 第五阶段 · 性能测试", stage4, 1)

# 4) 第六阶段表头统一成五列，并把 ch46 那行规整
old6 = """| 章 | 主题 | 实操目录 |
| --- | --- | --- |
| 40 | 平台架构与最小可用 | `labs/ch40-*` |
| 41 | 项目配置与环境上下文 | `labs/ch41-*` |
| 42 | 接口资产与一致性校验 | `labs/ch42-*` |
| 43 | 用例与关键字执行器 | `labs/ch43-*` |
| 44 | 测试计划与异步执行 | `labs/ch44-*` |
| 45 | 平台收口 | `labs/ch45-*` |
| 46 | `labs/ch46-toolchain` | 工具链源码 + 自检 | 技能注册、命令安装、命名净化 | 7 |"""
new6 = """| 章 | 实操目录 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- |
| 40 | `labs/ch40-miniweb` | 微型 Web 框架、路由、模板、项目 CRUD | 7 |
| 41 | `labs/ch41-config` | 配置分层、`${VAR}` 展开、密钥脱敏 | 8 |
| 42 | `labs/ch42-assets` | OpenAPI 导入、四条一致性规则 | 7 |
| 43 | `labs/ch43-executor` | 关键字执行、变量渲染、失败即停 | 8 |
| 44 | `labs/ch44-plans` | 计划状态机、异步 worker、重试 | 7 |
| 45 | `labs/ch45-report` | Markdown/JUnit 报告、阈值门槛、退出码 | 8 |
| 46 | `labs/ch46-toolchain` | 技能注册、CLI 安装、命名净化 | 7 |"""
assert old6 in text, "第六阶段表没匹配上"
text = text.replace(old6, new6, 1)

# 5) 追加第七阶段（插在「## 怎么跑」之前）
stage7 = """## 第七阶段 · AI 应用与 Agent 专项测试

| 章 | 实操目录 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- |
| 47 | `labs/ch47-prompt-cases` | Prompt 当接口、上下文窗口三策略、多轮与记忆窗口、覆盖清单 | 11 |
| 48 | `labs/ch48-token-perf` | TTFT/TPOT 换算、并发排队、长上下文退化、冷启动、成本 | 10 |
| 49 | `labs/ch49-prompt-regression` | 模板缺变量、稳定性一致率、A/B 分桶、回归对比 | 9 |
| 50 | `labs/ch50-rag-eval` | 分块与重叠、阈值与召回、TopK、三种检索、重排、引用与幻觉 | 12 |
| 51 | `labs/ch51-safety-redteam` | 注入与越狱、输出泄露扫描、PII 脱敏、越权、合规拒答 | 11 |
| 52 | `labs/ch52-mcp-tools` | Schema 校验十一类故障、工具选择、串并行、污染与审计 | 13 |
| 53 | `labs/ch53-agent-loop` | 规划拆解、死循环、三类记忆、不可逆操作确认 | 12 |
| 54 | `labs/ch54-model-eval` | 准召 F1、BLEU/ROUGE 局限、偏置探针、PSI 漂移、部署指标 | 12 |

## 怎么跑"""
text = text.replace("## 怎么跑", stage7, 1)

# 6) 合计改成真实数字
text = text.replace(
    "合计 **480 条测试**（465 条离线可跑，15 条真机用例需连接安卓设备）。",
    "合计 **570 条测试**（555 条离线全绿，15 条真机用例需连接安卓设备）。",
)

PAGE.write_text(text, encoding="utf-8")
print("labs/index.md rebuilt, lines =", len(text.splitlines()))
