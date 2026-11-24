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
KB = SITE / "kb" / "skills"

# 手册页用的是短名（web-cli），技能目录名带 shenle- 前缀（shenle-web-cli）
SHORT = {
    "shenle-android-cli": "android-cli",
    "shenle-api-record": "api-record",
    "shenle-dynamic-function-generator": "dynamic-function-generator",
    "shenle-test-flow-builder": "test-flow-builder",
    "shenle-test-plan-generator": "test-plan-generator",
    "shenle-test-runner": "test-runner",
    "shenle-web-cli": "web-cli",
    "shenle-web-record": "web-record",
}


def redirect_html(target: str, label: str) -> str:
    """public 下不参与编译的静态跳转页，兜住短名与旧地址。"""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>跳到 {label}</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
<style>body{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:14vh auto;max-width:40rem;padding:0 1.5rem;line-height:1.7}}a{{color:#4d7c0f}}</style>
</head>
<body>
<p>正在跳到 <a href="{target}">{label}</a>…</p>
<p>没有自动跳转就点上面的链接。</p>
</body>
</html>
"""


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
            # 少数技能是「包内再套一层 skill/<name>/」的形态，SKILL.md 在更深的目录里
            nested = sorted(p for p in skill.glob("**/SKILL.md") if p.parent != skill)
            if len(nested) != 1:
                continue
            entry = nested[0]
        name = skill.name
        text = entry.read_text(encoding="utf-8", errors="replace")
        desc = frontmatter(text).get("description", "")
        refs = sorted((skill / "references").glob("*.md")) if (skill / "references").is_dir() else []
        if not refs:
            refs = sorted(skill.glob("*/references/*.md"))
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

        kb_slug = SHORT.get(name, name)
        page = [
            "---",
            f"title: {name}",
            "---",
            "",
            f"# {name}",
            "",
            f"> {esc(short(desc, 200))}",
            "",
            f"正文 {lines} 行，随包 references {len(refs)} 个。",
            "",
            f"读完想直接用：[下载 zip（SKILL.md{'+references' if refs else ''}）](/skills/{name}.zip)"
            f"　·　看说明与评分：[Skills 手册 · {kb_slug}](/kb/skills/{kb_slug})",
            "",
            "---",
            "",
            body,
            "",
        ]
        (PAGES / f"{name}.md").write_text("\n".join(page), encoding="utf-8")

        # 短名与旧地址都能走到同一页：/skills/web-cli → /skills/shenle-web-cli
        alias = SHORT.get(name)
        if alias:
            stale = PAGES / f"{alias}.md"
            if stale.exists():
                stale.unlink()
            target = f"/shenle-ai-qa/skills/{name}"
            (PUBLIC / alias).mkdir(parents=True, exist_ok=True)
            (PUBLIC / alias / "index.html").write_text(
                redirect_html(target, name), encoding="utf-8"
            )

            kb_alias = KB / f"{name}.md"
            if kb_alias.exists():
                kb_alias.unlink()
            kb_root = PUBLIC.parent / "kb" / "skills" / name
            kb_root.mkdir(parents=True, exist_ok=True)
            (kb_root / "index.html").write_text(
                redirect_html(f"/shenle-ai-qa/kb/skills/{alias}", alias), encoding="utf-8"
            )
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
            f"[预览](/skills/{name}) · [下载 zip](/skills/{name}.zip) |"
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
