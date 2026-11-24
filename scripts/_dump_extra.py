"""把每章的「延伸知识」小节抽出来打印，供人工复核（这一节最容易凑干货写错）。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pat = re.compile(r"^## 延伸知识\s*$(.*?)(?=^## |\Z)", re.M | re.S)

for p in sorted((ROOT / "notes").glob("ch*.md")):
    text = p.read_text(encoding="utf-8")
    m = pat.search(text)
    if not m:
        continue
    print("==", p.name)
    for line in m.group(1).strip().splitlines():
        if line.strip():
            print("  ", line.strip()[:160])
