"""把 shenle-report-generate-html 的 SKILL.md 从 skill/<name>/ 提到目录根，让评分与发布都能认。"""

from __future__ import annotations

import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-report-generate-html"
nested = root / "skill" / root.name
if (root / "SKILL.md").is_file():
    print("已有顶层 SKILL.md，跳过")
    raise SystemExit(0)
if not (nested / "SKILL.md").is_file():
    print("没找到嵌套 SKILL.md", nested)
    raise SystemExit(1)
shutil.copy2(nested / "SKILL.md", root / "SKILL.md")
print("已复制到顶层", (root / "SKILL.md"))
