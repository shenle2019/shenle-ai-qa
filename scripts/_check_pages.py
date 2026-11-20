# -*- coding: utf-8 -*-
"""检查 45 个章节页是否都有正文。"""

import re
from pathlib import Path

dist = Path("site/.vitepress/dist/chapters")
bad = []
pages = sorted(dist.glob("ch*.html"))
for page in pages:
    html = page.read_text(encoding="utf-8")
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    h1 = re.sub(r"<[^>]+>", "", match.group(1)).strip() if match else ""
    text_len = len(re.sub(r"<[^>]+>", "", html))
    if not h1 or text_len < 4000:
        bad.append((page.name, h1[:24], text_len))

print("pages", len(pages), "suspicious", len(bad))
for row in bad[:10]:
    print(row)
