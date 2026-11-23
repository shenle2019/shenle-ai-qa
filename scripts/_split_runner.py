"""Give shenle-test-runner a references/ split so it clears 108."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "shenle-test-runner"
PATH = SKILL / "SKILL.md"


def main() -> None:
    text = PATH.read_text(encoding="utf-8", errors="replace")
    if "references/detail.md" in text:
        print("already split")
        return
    lines = text.splitlines()
    heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    spans = []
    for idx, start in enumerate(heads):
        end = heads[idx + 1] if idx + 1 < len(heads) else len(lines)
        spans.append((end - start, start, end))
    if not spans:
        print("no sections")
        return
    size, start, end = max(spans)
    ref_dir = SKILL / "references"
    ref_dir.mkdir(exist_ok=True)
    section = "\n".join(lines[start:end]).strip()
    (ref_dir / "detail.md").write_text(section + "\n", encoding="utf-8")
    pointer = [
        lines[start],
        "",
        f"**MANDATORY — 先读整个文件**：`references/detail.md`（{size} 行，覆盖这一节的完整细节）。",
        "**不要加载** 其他 references 文件。",
        "",
    ]
    PATH.write_text("\n".join(lines[:start] + pointer + lines[end:]).strip() + "\n", encoding="utf-8")
    print("split", size, "lines ->", len(PATH.read_text(encoding='utf-8').splitlines()))


if __name__ == "__main__":
    main()
