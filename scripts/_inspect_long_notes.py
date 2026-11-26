# -*- coding: utf-8 -*-
"""看两篇偏长笔记的小节结构与代码块数量，判断是「内容扎实」还是「有重复」。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FENCE = "``" + "`"

for name in ("ch51-safety", "ch52-mcp"):
    text = (ROOT / "notes" / f"{name}.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    print("=" * 12, name, len(lines), "行")
    for line in lines:
        if line.startswith("## "):
            print("  ", line)
    print("   代码块:", text.count(FENCE) // 2, "个")
