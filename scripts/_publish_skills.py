"""Publish every platform skill on the site: inline preview page + one zip per skill.

Raw .md files stay inside the zip only, because VitePress would try to compile any
`.md` placed under site/public as a page and choke on skill placeholders like <slug>.
"""

from __future__ import annotations

import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
SITE = ROOT / "site"
PAGES = SITE / "skills"
PUBLIC = SITE / "public" / "skills"

NAME_RE = re.compile(r"^name:\s*(.+)$", re.M)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip("\"'")
    return meta


def esc(text: str) -> str:
    """Keep placeholders like <slug> from being parsed as Vue template tags."""
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|")


def short(text: str, limit: int = 60) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for stale in PUBLIC.glob("*"):
        if stale.is_dir():
            shutil.rmtree(stale)
        else:
            stale.unlink()

    rows = []
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        entry = skill / "SKILL.md"
        if not entry.is_file():
            continue
        name = skill.name
        text = entry.read_text(encoding="utf-8", errors="replace")
        desc = frontmatter(text).get("description", "")
        refs = sorted((skill / "references").glob("*.md")) if (skill / "references").is_dir() else []
        lines = len(text.splitlines())
        body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S).lstrip("\n")
        body = body.replace("<", "&lt;").replace(">", "&gt;").replace("{{", "&#123;&#123;")

        archive = PUBLIC / f"{name}.zip"
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / name
            stage.mkdir()
            shutil.copy2(entry, stage / "SKILL.md")
            for ref in refs:
                shutil.copy2(ref, stage / ref.name)
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in sorted(stage.rglob("*")):
                    if item.is_file():
                        zf.write(item, f"{name}/{item.relative_to(stage)}")

        page = [
            "---",
            f"title: {name}",
            "---",
            "",
            f"# {name}",
            "",
            f"> {esc(short(desc, 200))}",
            "",
            f"- 正文 {lines} 行，随包 references {len(refs)} 个",
            f"- [下载这个技能（zip，含 SKILL.md{'+references' if refs else ''}）](/skills/{name}.zip)",
            "",
            "---",
            "",
            body,
            "",
        ]
        (PAGES / f"{name}.md").write_text("\n".join(page), encoding="utf-8")
        rows.append((name, lines, len(refs), short(desc)))

    table = [
        "---",
        "title: Skills 库",
        "---",
        "",
        "# Skills 库",
        "",
        f"平台在用的 {len(rows)} 个技能，全部可直接读全文、也可下载原始文件（zip 内含 `SKILL.md` 与 references）。",
        "",
        "| 技能 | 一句话说明 | 正文 | references | 打开 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, lines, ref_count, desc in rows:
        table.append(
            f"| `{name}` | {esc(desc)} | {lines} 行 | {ref_count} | "
            f"[预览](/skills/{name}) · [zip](/skills/{name}.zip) |"
        )
    table += [
        "",
        "## 怎么用",
        "",
        "解开 zip，把整个目录放进项目的 `.claude/skills/` 下，重启会话即可被识别。",
        "",
        "每个技能的评分与设计取舍见 [Skills 手册](/kb/skills/)，单次调用记录见 [Skills 单跑记录](/labs/skills/)。",
        "",
    ]
    (PAGES / "index.md").write_text("\n".join(table), encoding="utf-8")
    print(f"skills {len(rows)}")


if __name__ == "__main__":
    main()
