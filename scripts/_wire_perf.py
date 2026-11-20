"""把性能阶段 33–39 章节页与各处计数接上（一次性脚本）。"""

from pathlib import Path

CH = [
    ("ch33", "场景设计：基准、负载、压力、稳定性", "labs/ch33-scenarios", "ch33-scenarios"),
    ("ch34", "压测脚本与参数化", "labs/ch34-scripts", "ch34-scripts"),
    ("ch35", "结果分析与瓶颈定位", "labs/ch35-analyze", "ch35-analyze"),
    ("ch36", "中间件性能要点", "labs/ch36-middleware", "ch36-middleware"),
    ("ch37", "全链路压测与数据隔离", "labs/ch37-chain", "ch37-chain"),
    ("ch38", "AI 辅助性能分析", "labs/ch38-ai", "ch38-ai"),
    ("ch39", "性能平台收口", "labs/ch39-perf-platform", "ch39-perf-platform"),
]

SITE = Path("site")

for slug, title, lab, note in CH:
    page = SITE / "chapters" / f"{slug}.md"
    page.write_text(
        f"---\ntitle: {slug[2:]} · {title}\n---\n\n<!--@include: ../../notes/{note}.md-->\n",
        encoding="utf-8",
    )

config = SITE / ".vitepress" / "config.mts"
text = config.read_text(encoding="utf-8")
anchor = "      { text: '32 性能测试基础', link: '/chapters/ch32' }\n"
extra = "".join(
    f"      {{ text: '{slug[2:]} {title}', link: '/chapters/{slug}' }},\n" for slug, title, _, _ in CH
)
if anchor in text and "ch33" not in text:
    text = text.replace(anchor, anchor.rstrip("\n") + ",\n" + extra, 1)
    text = text.replace("'32 性能测试基础', link: '/chapters/ch32' },", "'32 性能测试基础', link: '/chapters/ch32' },", 1)
    config.write_text(text, encoding="utf-8")
    print("sidebar wired")

rows = "".join(
    f"| {slug[2:]} | {title} | [{slug[2:]}](/{'chapters'}/{slug}) | `{lab}` |\n" for slug, title, lab, _ in CH
)
rows = rows.replace("](//", "](")

for target in [SITE / "index.md", Path("README.md")]:
    body = target.read_text(encoding="utf-8")
    if "| 33 |" in body:
        continue
    marker = "| 32 | 性能测试基础与指标 | [32](/chapters/ch32) | `labs/ch32-perf-basics` |\n"
    if marker in body:
        body = body.replace(marker, marker + rows, 1)
    else:
        body = body.replace("| 32 |", rows + "| 32 |", 1) if False else body
    target.write_text(body, encoding="utf-8")
    print("rows ->", target)
