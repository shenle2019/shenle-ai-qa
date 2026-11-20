# -*- coding: utf-8 -*-
"""重建 01–45 章站点页：中文标题从侧栏配置取，include 路径从现有文件取。"""

import re
from pathlib import Path

cfg = Path("site/.vitepress/config.mts").read_text(encoding="utf-8")
titles = {}
for m in re.finditer(r"\{ text: '(\d{2}) ([^']+)', link: '/chapters/ch(\d{2})' \}", cfg):
    titles[m.group(3)] = f"{m.group(3)} · {m.group(2)}"

FALLBACK_SLUG = {"41": "ch41-config", "42": "ch42-assets"}

fixed = []
for num in [f"{i:02d}" for i in range(1, 46)]:
    page = Path(f"site/chapters/ch{num}.md")
    old = page.read_text(encoding="utf-8")
    m = re.search(r"<!--@include: ../../notes/([^>]+?)-->", old)
    slug = m.group(1) if m else None
    if not slug or "{" in slug:
        slug = FALLBACK_SLUG.get(num) or f"ch{num}-x"
    slug = slug.replace(".md", "")
    note = Path(f"notes/{slug}.md")
    if not note.exists():
        fixed.append(f"MISSING notes/{slug}.md (ch{num})")
        continue
    title = titles.get(num, f"{num}")
    page.write_text(
        f"---\ntitle: {title}\n---\n\n<!--@include: ../../notes/{slug}.md-->\n",
        encoding="utf-8",
    )
    fixed.append(f"ch{num} -> notes/{slug}.md | {title}")

print("\n".join(fixed[:6]))
print("...")
print("\n".join(fixed[-6:]))
print("total", len(fixed))
