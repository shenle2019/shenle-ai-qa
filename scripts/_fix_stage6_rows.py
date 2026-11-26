# -*- coding: utf-8 -*-
"""把第六阶段表的行改成实测目录名与实测条数（前面写的是估值，这里对齐真相）。"""

from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "site" / "labs" / "index.md"
text = PAGE.read_text(encoding="utf-8")

old = """| 40 | `labs/ch40-miniweb` | 微型 Web 框架、路由、模板、项目 CRUD | 7 |
| 41 | `labs/ch41-config` | 配置分层、`${VAR}` 展开、密钥脱敏 | 8 |
| 42 | `labs/ch42-assets` | OpenAPI 导入、四条一致性规则 | 7 |
| 43 | `labs/ch43-executor` | 关键字执行、变量渲染、失败即停 | 8 |
| 44 | `labs/ch44-plans` | 计划状态机、异步 worker、重试 | 7 |
| 45 | `labs/ch45-report` | Markdown/JUnit 报告、阈值门槛、退出码 | 8 |
| 46 | `labs/ch46-toolchain` | 技能注册、CLI 安装、命名净化 | 7 |"""
new = """| 40 | `labs/ch40-platform` | 微型 Web 框架、路由、项目 CRUD | 12 |
| 41 | `labs/ch41-config` | 配置分层、`${VAR}` 展开、密钥脱敏 | 8 |
| 42 | `labs/ch42-assets` | OpenAPI 导入、四条一致性规则 | 8 |
| 43 | `labs/ch43-executor` | 关键字执行、变量渲染、失败即停 | 8 |
| 44 | `labs/ch44-plans` | 计划状态机、异步 worker、重试 | 8 |
| 45 | `labs/ch45-report` | Markdown/JUnit 报告、阈值门槛、退出码 | 8 |
| 46 | `labs/ch46-toolchain` | 技能注册、CLI 安装、命名净化 | 7 |"""
assert old in text
PAGE.write_text(text.replace(old, new), encoding="utf-8")

# 顺手核对：第七阶段 8 行合计 90
rows = [l for l in new.splitlines()]
print("stage6 total =", 12 + 8 + 8 + 8 + 8 + 8 + 7)
print("patched ch40-46 rows")
