"""Score the platform skills with the skill-judge rubric (heuristic, auditable)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"

WHEN = re.compile(r"(Use when|使用场景|什么时候用|何时用|当用户|触发词|Triggers?:)", re.I)
ANTI = re.compile(r"(NEVER|不要做|禁止|反模式|Anti-pattern|常犯错误)", re.I)
TABLE = re.compile(r"^\|.+\|$", re.M)
CODE = re.compile(r"```")
REF_TRIGGER = re.compile(r"(MANDATORY|必须先读|Do NOT load|不要加载|references/)", re.I)
FALLBACK = re.compile(r"(兜底|失败时|fallback|回退|如果.*失败|错误处理)", re.I)
EXAMPLES = re.compile(r"(示例|Example|```bash)")


def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    block = text[3:end]
    body = text[end + 4 :]
    meta = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def score(text: str, has_refs: bool) -> dict:
    meta, body = frontmatter(text)
    lines = len(body.splitlines())
    desc = meta.get("description", "")
    name = meta.get("name", "")

    # D4 specification (15): frontmatter + description WHAT/WHEN/KEYWORDS
    d4 = 0
    if name and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        d4 += 4
    if len(desc) >= 40:
        d4 += 4
    elif len(desc) >= 20:
        d4 += 2
    if WHEN.search(desc):
        d4 += 4
    if re.search(r"(\.(py|md|json|yaml)|cli|adapter|record|runner)", desc, re.I):
        d4 += 3
    d4 = min(d4, 15)

    # D5 progressive disclosure (15)
    d5 = 6 if lines < 300 else 4 if lines < 500 else 2
    if has_refs:
        d5 += 6 if REF_TRIGGER.search(body) else 2
    else:
        d5 += 4 if lines < 300 else 2
    if lines < 200:
        d5 += 2
    d5 = min(d5, 15)

    # D3 anti-patterns (15)
    hits = len(ANTI.findall(body))
    never = len(re.findall(r"\*\*NEVER\*\*|^- NEVER|^- 不要", body, re.M))
    reasoned = len(re.findall(r"NEVER.*?——", body))
    d3 = 4 + min(hits, 3) + min(never, 4) + (2 if reasoned >= 4 else 0)
    d3 = min(d3, 15)

    # D8 usability (15)
    d8 = 3
    d8 += 3 if len(TABLE.findall(body)) >= 6 else 1 if TABLE.search(body) else 0
    d8 += 3 if CODE.search(body) else 0
    d8 += 3 if FALLBACK.search(body) else 0
    d8 += 3 if EXAMPLES.search(body) else 0
    d8 = min(d8, 15)

    # D1 knowledge delta (20): penalise tutorial markers, reward decision/edge content
    tutorial = len(re.findall(r"(什么是|简介|基础概念|入门|安装步骤)", body))
    d1 = 14 - min(tutorial * 2, 10) + (3 if TABLE.search(body) else 0)
    d1 = max(4, min(d1, 20))

    # D2 mindset + procedures (15)
    d2 = 5 + (3 if re.search(r"(先.*再|顺序|workflow|流程)", body) else 0)
    d2 += 3 if re.search(r"(判断|选择|决策|哪个)", body) else 0
    d2 += 2 if CODE.search(body) else 0
    d2 += 2 if "## 执行顺序" in body else 0
    d2 = min(d2, 15)

    # D6 freedom (15): exact commands for fragile CLI ops = good
    d6 = 12 if CODE.search(body) else 6
    d6 = min(d6, 15)

    # D7 pattern (10): tool/process pattern
    d7 = 10 if (CODE.search(body) and TABLE.search(body) and "## 执行顺序" in body) else 8 if CODE.search(body) and TABLE.search(body) else 6

    total = d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8
    return {
        "name": name or "?",
        "lines": lines,
        "desc_len": len(desc),
        "D1": d1, "D2": d2, "D3": d3, "D4": d4,
        "D5": d5, "D6": d6, "D7": d7, "D8": d8,
        "total": total,
    }


def main() -> None:
    rows = []
    for d in sorted(SKILLS.iterdir()):
        f = d / "SKILL.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        has_refs = any(p.is_dir() for p in d.iterdir() if p.name in {"references", "scripts", "assets"})
        row = score(text, has_refs)
        row["dir"] = d.name
        rows.append(row)
    rows.sort(key=lambda r: r["total"])
    print(f"{'skill':34s} {'tot':>4s} D1 D2 D3 D4 D5 D6 D7 D8  lines")
    for r in rows:
        print(f"{r['dir']:34s} {r['total']:4d} {r['D1']:2d} {r['D2']:2d} {r['D3']:2d} {r['D4']:2d} {r['D5']:2d} {r['D6']:2d} {r['D7']:2d} {r['D8']:2d} {r['lines']:5d}")
    low = [r["dir"] for r in rows if r["total"] < 108]
    print("below108:", len(low), low)
    (ROOT / "docs" / "skill-scores.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
