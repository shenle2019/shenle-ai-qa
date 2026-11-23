"""把第 46 章接进站点：页面、侧栏、索引表与计数。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

PAGE = """---
title: 46 · AI 测试 Skills 与工具链落地
---

<!--@include: ../../notes/ch46-toolchain.md-->
"""


def write_page() -> None:
    (SITE / "chapters" / "ch46.md").write_text(PAGE, encoding="utf-8")


def patch_sidebar() -> None:
    path = SITE / ".vitepress" / "config.mts"
    text = path.read_text(encoding="utf-8")
    anchor = "{ text: '45 平台收口', link: '/chapters/ch45' }"
    entry = "{ text: '46 AI 测试 Skills 与工具链', link: '/chapters/ch46' }"
    assert text.count(anchor) == 2, f"anchor 出现 {text.count(anchor)} 次"
    if entry in text:
        return
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        out.append(line)
        if anchor in line:
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f"{indent}{entry},")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def patch_counts() -> None:
    pairs = [("469 条", "476 条"), ("四十五个实操", "四十六个实操"), ("共 469 条", "共 476 条")]
    for rel in ["site/index.md", "site/chapters/index.md", "site/labs/index.md", "README.md", "STAGE-BRIEF.md"]:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new = text
        for old, value in pairs:
            new = new.replace(old, value)
        if new != text:
            path.write_text(new, encoding="utf-8")


def append_rows() -> None:
    row_chapters = "| 46 | AI 测试 Skills 与工具链 | [ch46](/chapters/ch46) | `labs/ch46-toolchain` |"
    row_labs = "| 46 | `labs/ch46-toolchain` | 工具链源码 + 自检 | 技能注册、命令安装、命名净化 | 7 |"
    for rel, row in [("site/chapters/index.md", row_chapters), ("site/labs/index.md", row_labs)]:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if "ch46" in text:
            continue
        lines = text.splitlines()
        last = max((i for i, line in enumerate(lines) if line.startswith("| 45 ")), default=-1)
        if last < 0:
            continue
        lines.insert(last + 1, row)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_page()
    patch_sidebar()
    patch_counts()
    append_rows()
    print("wired ch46")


if __name__ == "__main__":
    main()
