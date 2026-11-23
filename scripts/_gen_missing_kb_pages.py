"""Generate handbook pages for skills that have no page yet (auto-derived from SKILL.md)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
KB = ROOT / "site" / "kb" / "skills"

GROUPS = {
    "case-generator": "用例生成",
    "testpoint": "测试点分析",
    "doc-generator": "用例生成",
    "mitmproxy-record": "录制采集",
    "zentao-cli": "执行与定位",
}


def group_of(name: str) -> str:
    for key, group in GROUPS.items():
        if key in name:
            return group
    return "执行与定位"


def one_line(text: str, name: str) -> str:
    m = re.search(r'^description:\s*"?(.*?)"?\s*$', text, re.M)
    if m:
        desc = m.group(1).strip()
        desc = re.split(r"(?<=。)|\n", desc)[0].strip()
        return desc[:120] or name
    m = re.search(r"^#\s+.+?\n+(.{0,200})", text, re.S)
    if m:
        return m.group(1).strip().splitlines()[0][:120]
    return name


def bullets(text: str, limit: int = 4) -> list[str]:
    items = re.findall(r"^[-*]\s+(.{4,90})$", text, re.M)
    seen, out = set(), []
    for item in items:
        item = item.strip()
        if item in seen or item.startswith("*图") or "|" in item:
            continue
        seen.add(item)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def commands(text: str, limit: int = 4) -> list[str]:
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    lines: list[str] = []
    for block in blocks:
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line not in lines:
                lines.append(line)
            if len(lines) >= limit:
                return lines
    return lines


def section(text: str, title: str) -> str:
    m = re.search(rf"^##\s+{re.escape(title)}.*?\n(.*?)(?=^##\s|\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def build(name: str, text: str) -> str:
    desc = one_line(text, name)
    core = bullets(text)
    cmds = commands(text)
    lines = [
        "---",
        f"title: {name}",
        "---",
        "",
        f"# {name}",
        "",
        f"> 分组：**{group_of(name)}**　来源：`.claude/skills/{name}`",
        "",
        "## 它是什么",
        "",
        desc,
        "",
        "## 核心功能",
        "",
    ]
    lines += [f"- {item}" for item in (core or ["见 SKILL.md"])]
    lines += ["", "## 怎么用", "", "```bash"]
    lines += (cmds or [f"# 见 .claude/skills/{name}/SKILL.md"])
    lines += ["```", ""]
    products = section(text, "产物") or section(text, "输出")
    lines += ["## 产物与判读", ""]
    lines += [products[:400] or "按 SKILL.md 约定落盘到工作目录，失败时保留原始输入。", ""]
    fails = section(text, "常见失败") or section(text, "反模式")
    lines += ["## 常见失败模式", ""]
    lines += [fails[:400] or "输入缺字段、路径不存在时会直接报错；先按 SKILL.md 核对入参。", ""]
    lines += [
        "## 相关",
        "",
        f"- 全文与下载：[Skills 库](/skills/{name})",
        "- 返回：[Skills 手册](/kb/skills/)",
        "",
        "## 评分（skill-judge）",
        "",
        "本轮新补入，尚未逐维打分；评分脚本 `scripts/_score_skills.py`，口径见 `docs/skill-scores.md`。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    KB.mkdir(parents=True, exist_ok=True)
    made = []
    for folder in sorted(SKILLS.iterdir()):
        entry = folder / "SKILL.md"
        if not folder.is_dir() or not entry.is_file():
            continue
        page = KB / f"{folder.name}.md"
        if page.is_file():
            continue
        page.write_text(build(folder.name, entry.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
        made.append(folder.name)
    print("generated", len(made), made)


if __name__ == "__main__":
    main()
