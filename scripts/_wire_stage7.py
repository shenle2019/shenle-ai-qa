# -*- coding: utf-8 -*-
"""把第七阶段（ch47–ch54）接进站点：侧栏分组 + 8 个章节页。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "site" / ".vitepress" / "config.mts"

CHAPTERS = [
    ("47", "AI 应用功能测试：把 Prompt 当接口", "ch47-ai-functional"),
    ("48", "AI 性能：TTFT、TPOT 与并发", "ch48-ai-perf"),
    ("49", "Prompt 专项与回归", "ch49-prompt-special"),
    ("50", "RAG：检索层与生成层", "ch50-rag"),
    ("51", "安全与合规：注入、泄露、越权", "ch51-safety"),
    ("52", "MCP 工具调用测试", "ch52-mcp"),
    ("53", "Agent：规划、循环、记忆与不可逆", "ch53-agent"),
    ("54", "大模型评估与部署", "ch54-model-eval"),
]

cfg = CFG.read_text(encoding="utf-8")

if "第七阶段" not in cfg:
    anchor = """            { text: '46 AI 测试 Skills 与工具链落地', link: '/chapters/ch46' },
          ]
        },"""
    assert anchor in cfg, "第六阶段锚点没找到"
    items = "\n".join(
        f"            {{ text: '{num} {title}', link: '/chapters/ch{num}' }}," for num, title, _ in CHAPTERS
    )
    block = (
        anchor
        + """
        {
          text: '第七阶段 · AI 应用与 Agent 专项测试',
          items: [
"""
        + items
        + """
          ]
        },"""
    )
    cfg = cfg.replace(anchor, block, 1)
    CFG.write_text(cfg, encoding="utf-8")
    print("sidebar: 第七阶段 已插入")
else:
    print("sidebar: 已存在，跳过")

for num, title, slug in CHAPTERS:
    page = ROOT / "site" / "chapters" / f"ch{num}.md"
    page.write_text(
        f"---\ntitle: {num} {title}\n---\n\n<!--@include: ../../notes/{slug}.md-->\n",
        encoding="utf-8",
    )
print("chapters: 已写", len(CHAPTERS), "页")
