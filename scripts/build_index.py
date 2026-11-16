"""按标题把 283 篇语雀文档归入学习阶段，生成 INDEX.md 与分组统计。

用法: python build_index.py
"""
from __future__ import annotations

import json
import re
from collections import OrderedDict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "corpus" / "yuque"

STAGES = OrderedDict(
    [
        ("00 测试基础与流程", [r"测试职业发展", r"软件生命周期", r"测试工作流程", r"需求分析与测试用例", r"缺陷编写", r"禅道", r"测试计划"]),
        ("01 Python 与数据库", [r"Python基础课", r"Python AI测试开发基础", r"Mysql", r"MySQL", r"Python 入门"]),
        ("02 接口测试与自动化", [r"接口", r"API", r"postman", r"requests"]),
        ("03 Web 与 APP 自动化", [r"Web", r"APP", r"UI", r"selenium", r"playwright", r"appium"]),
        ("04 性能测试", [r"性能"]),
        ("05 测试平台与智能体", [r"课题[一二三四五六七八九十]", r"AI智能体平台", r"测试平台", r"平台开发"]),
        ("06 大模型与 AI 测评", [r"大模型", r"LLM", r"AI扫盲", r"AI工程应用", r"Ragas", r"测评"]),
        ("07 项目实战", [r"^项目[一二三四五六七八九十]", r"项目十九", r"EduScore", r"综合项目"]),
        ("08 面试与求职", [r"面试", r"简历", r"offer", r"薪资", r"笔试", r"笔试题", r"答题", r"题库"]),
        ("09 AI 辅助测试实战", [r"AI-辅助", r"AI 辅助", r"AI协作", r"提示词", r"AI基础", r"Python代码调用AI"]),
        ("10 工具与环境", [
            r"Openclaw", r"openclaw", r"MidScene", r"Dify", r"Claude", r"Trae", r"通义灵码",
            r"Ollama", r"Conda", r"conda", r"pipenv", r"pyenv", r"UV", r"NodeJS", r"centos",
            r"Docker", r"Git", r"git", r"Linux", r"openpyxl", r"BeanShell", r"LoadRunner",
            r"locust", r"Python打包", r"环境搭建", r"使用教程", r"安装教程", r"所有命令", r"browser命令",
        ]),
        ("11 测试设计与方法论", [
            r"测试方案", r"需求文档", r"需求分析报告", r"风险评估", r"兼容性", r"幂等", r"redis", r"mq",
            r"游戏测试", r"匹配机制", r"牌型", r"限购", r"数据库被锁", r"云桌面", r"人脸识别",
            r"巡检脚本", r"线程和进程", r"LEGB", r"自动化框架", r"框架介绍", r"编程题", r"练习题",
            r"面试题", r"测试思路", r"ChatGPT", r"聊天模块",
        ]),
    ]
)


def stage_of(title: str) -> str:
    for stage, patterns in STAGES.items():
        for pat in patterns:
            if re.search(pat, title, re.I):
                return stage
    return "99 其他"


def main() -> None:
    catalog = json.loads((BASE / "catalog.json").read_text(encoding="utf-8"))
    docs = catalog["docs"]

    groups: dict[str, list[dict]] = {s: [] for s in STAGES}
    groups["99 其他"] = []
    for doc in docs:
        groups[stage_of(doc["t"])].append(doc)

    lines = [
        "# 华测教育内部知识库 · 抓取索引",
        "",
        f"- 来源：https://www.yuque.com/shiduo-gf6e9/tnhrl5（book_id 73651885）",
        f"- 文档数：{len(docs)}，总字数：{sum(d.get('words', 0) for d in docs):,}",
        "- 正文：`md/` 下的 Markdown，原始 JSON：`raw/`，机器索引：`catalog.json`",
        "",
        "## 阶段分布",
        "",
        "| 阶段 | 篇数 | 字数 |",
        "| --- | --- | --- |",
    ]
    for stage, items in groups.items():
        if not items:
            continue
        lines.append(f"| {stage} | {len(items)} | {sum(i.get('words', 0) for i in items):,} |")

    for stage, items in groups.items():
        if not items:
            continue
        lines += ["", f"## {stage}", ""]
        for item in items:
            words = item.get("words", 0)
            lines.append(f"- [{item['t']}]({item['md']}) · {words:,} 字")

    out = BASE / "INDEX.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{'stage':<24}{'docs':>6}{'words':>10}")
    for stage, items in groups.items():
        print(f"{stage:<24}{len(items):>6}{sum(i.get('words', 0) for i in items):>10,}")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
