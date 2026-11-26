# -*- coding: utf-8 -*-
"""首页同步第七阶段：补阶段表、改条数与实操数、重写「下一步」。"""

from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "site" / "index.md"
text = PAGE.read_text(encoding="utf-8")

old_count = "480 条 pytest 用例（465 条离线通过 + 15 条真机用例在未接手机时自动跳过），四十六个实操都能单独运行："
new_count = "570 条 pytest 用例（555 条离线全绿 + 15 条真机用例在未接手机时自动跳过），五十四个实操都能单独运行："
assert old_count in text, "条数行没找到"
text = text.replace(old_count, new_count, 1)

stage7 = """## 第七阶段 · AI 应用与 Agent 专项测试

前六个阶段测的是「确定的系统」：接口返回 200 就是 200。这一阶段测的是「概率的系统」——
同一个输入两次结果可能不同，所以用例、判定、性能口径、安全边界全都要换一套写法。

| 章 | 主题 | 实操目录 |
| --- | --- | --- |
| 47 | AI 应用功能测试：把 Prompt 当接口 | `labs/ch47-prompt-cases` |
| 48 | AI 性能：TTFT、TPOT 与并发 | `labs/ch48-token-perf` |
| 49 | Prompt 专项与回归 | `labs/ch49-prompt-regression` |
| 50 | RAG：检索层与生成层 | `labs/ch50-rag-eval` |
| 51 | 安全与合规：注入、泄露、越权 | `labs/ch51-safety-redteam` |
| 52 | MCP 工具调用测试 | `labs/ch52-mcp-tools` |
| 53 | Agent：规划、循环、记忆与不可逆 | `labs/ch53-agent-loop` |
| 54 | 大模型评估与部署 | `labs/ch54-model-eval` |

这八章不需要 API Key：`labs/_shared/` 里有一套可复现的假模型（`llm_sim.py`）、假检索（`rag_sim.py`）、
假工具层（`mcp_sim.py`）、假 Agent（`agent_sim.py`）和评测函数（`eval_sim.py`），
所以「不确定性」「上下文截断」「越权」「死循环」这些原本只能靠线上事故学习的东西，在这里都变成了可断言的用例。

## 仓库结构"""

text = text.replace("## 仓库结构", stage7, 1)

old_next = """前六个阶段都写完了：Python 基础、接口、Web、APP（ch24–31，只用 adb，不引 Appium）、性能、平台与工具链。下一步是把六个阶段收口成一条流水线——一条命令从接口跑到界面、从压测跑到平台报告；再往后才是真机农场与多环境并行。"""
new_next = """七个阶段都写完了：Python 基础、接口、Web、APP（ch24–31，只用 adb，不引 Appium）、性能、平台与工具链、
AI 应用与 Agent 专项（ch47–54）。

下一步是把它们串成一条流水线：接口造数 → 界面回归 → 压测定基线 → 平台出报告，
AI 那一层则在每次模型或提示词变更后跑固定的评测集。真机农场与多环境并行放在最后。"""
assert old_next in text, "下一步段落没找到"
text = text.replace(old_next, new_next, 1)

PAGE.write_text(text, encoding="utf-8")
print("index.md patched, lines =", len(text.splitlines()))
