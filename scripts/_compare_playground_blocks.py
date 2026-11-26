# -*- coding: utf-8 -*-
"""对照「页面上读到的静态代码块」与「点运行真正执行的那段」是否一致。

不一致是隐性 bug：用户照着读的代码和跑的不是同一份，会被教学文档骗。
"""

import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
page = (ROOT / "site" / "labs" / "playground.md").read_text(encoding="utf-8")
ts = (ROOT / "site" / ".vitepress" / "theme" / "samples.ts").read_text(encoding="utf-8")

samples = dict(re.findall(r"export const (\w+) = `(.*?)`", ts, re.S))
blocks = re.findall(r"```python\n(.*?)```", page, re.S)
order = ["basics", "collections", "decorator", "exception"]

print("静态代码块:", len(blocks), "样例:", list(samples))
for idx, (block, key) in enumerate(zip(blocks, order), start=1):
    same = block.strip() == samples[key].strip()
    print(f"\n{idx}. {key}: {'一致' if same else '不一致'}")
    if not same:
        diff = difflib.unified_diff(
            samples[key].strip().splitlines(), block.strip().splitlines(),
            "samples.ts", "playground.md", lineterm="", n=1,
        )
        print("\n".join(list(diff)[:30]))
