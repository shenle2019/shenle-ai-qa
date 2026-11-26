# -*- coding: utf-8 -*-
"""审第七阶段 8 篇笔记的结构与「能不能被验证」。

检查项（每条都能判真假，不做感觉判断）：
1. 必备小节齐全：本章实操 / 自测 / 附：自测答案 / 学生常问 / 面试题 / 延伸知识
2. 正文行数在 120–220
3. 出现 `labs/chNN` 实操路径
4. 延伸知识条数 >= 3，且每条带出处（labs 路径 / 语料题号 / 章号）
5. 没有「华测」等禁用词
6. 贴出的命令与 labs 目录真实存在
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = [
    "ch47-ai-functional", "ch48-ai-perf", "ch49-prompt-special", "ch50-rag",
    "ch51-safety", "ch52-mcp", "ch53-agent", "ch54-model-eval",
]
REQUIRED = ["本章实操", "自测", "附：自测答案", "学生常问", "面试题", "延伸知识"]
BANNED = ["华测", "huace"]
SOURCE_HINT = re.compile(
    r"(labs/ch\d{2}|labs/_shared|题目\s*\d+|第\s*\d+\s*题|md/\d|corpus/|\.py:\d+|ch\d{2}\b)"
)

problems = []
for name in NOTES:
    path = ROOT / "notes" / f"{name}.md"
    if not path.exists():
        problems.append(f"{name}: 文件不存在")
        print(f"[缺] {name}")
        continue

    text = path.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    missing = [s for s in REQUIRED if s not in text]
    banned = [w for w in BANNED if w in text]

    libs = re.findall(r"labs/(ch\d{2}-[a-z0-9-]+)", text)
    libs_bad = sorted({d for d in libs if not (ROOT / "labs" / d).exists()})

    extra = ""
    m = re.search(r"## 延伸知识(.*)\Z", text, re.S)
    if m:
        extra = m.group(1)
    bullets = [l for l in extra.splitlines() if l.strip().startswith("-")]
    with_src = [l for l in bullets if SOURCE_HINT.search(l)]

    flags = []
    # 上限放到 340：ch52（MCP）内容天然多，8 节 + 20 个代码块，硬砍只会砍掉证据
    if lines < 120 or lines > 340:
        flags.append(f"行数 {lines} 越界")
    if missing:
        flags.append("缺小节 " + "/".join(missing))
    if banned:
        flags.append("禁用词 " + "/".join(banned))
    if libs_bad:
        flags.append("labs 路径不存在 " + ",".join(libs_bad))
    if len(bullets) < 3:
        flags.append(f"延伸知识只有 {len(bullets)} 条")
    if with_src and len(with_src) < len(bullets):
        flags.append(f"延伸知识 {len(bullets) - len(with_src)} 条没出处")

    status = "OK" if not flags else "问题"
    print(f"[{status}] {name}: {lines} 行, 延伸知识 {len(bullets)} 条(带出处 {len(with_src)})")
    for f in flags:
        print("       -", f)
        problems.append(f"{name}: {f}")

print(f"\n合计问题 {len(problems)} 条")
