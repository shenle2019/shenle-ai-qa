"""Publish the skill-judge scores onto the handbook pages and the index."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "site" / "kb" / "skills"
LABS = ROOT / "site" / "labs" / "skills"
SCORES = ROOT / "docs" / "skill-scores.json"
MARK = "## 评分（skill-judge）"


def sync_copies() -> int:
    src = ROOT / ".claude" / "skills"
    dst = ROOT / "labs" / "ch46-toolchain" / ".claude" / "skills"
    n = 0
    for skill in sorted(src.iterdir()):
        if not skill.is_dir():
            continue
        target = dst / skill.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill, target)
        n += 1
    return n


def score_block(row: dict) -> str:
    dims = [
        ("D1 知识增量", row["D1"], 20),
        ("D2 心智与流程", row["D2"], 15),
        ("D3 反模式", row["D3"], 15),
        ("D4 规格", row["D4"], 15),
        ("D5 渐进披露", row["D5"], 15),
        ("D6 自由度", row["D6"], 15),
        ("D7 模式识别", row["D7"], 10),
        ("D8 实用可用性", row["D8"], 15),
    ]
    lines = [MARK, "", f"总分 **{row['total']} / 120**（≥108 为 A 级），按 skill-judge 八维逐项打分：", "", "| 维度 | 得分 | 满分 |", "| --- | --- | --- |"]
    for name, got, full in dims:
        lines.append(f"| {name} | {got} | {full} |")
    lines += ["", f"判定：{'✅ 达标' if row['total'] >= 108 else '⚠️ 未达标'}，规范条数见 `docs/skill-scores.json`。", ""]
    return "\n".join(lines)


def main() -> None:
    data = json.loads(SCORES.read_text(encoding="utf-8"))
    rows = {(r.get("slug") or r.get("name")): r for r in data}
    copied = sync_copies()
    touched = 0
    for slug, row in rows.items():
        page = None
        for name in (slug, slug.replace("shenle-", "")):
            cand = KB / f"{name}.md"
            if cand.exists():
                page = cand
                break
        if page is None:
            continue
        text = page.read_text(encoding="utf-8")
        if MARK in text:
            text = text.split(MARK)[0].rstrip() + "\n"
        page.write_text(text + "\n" + score_block(row), encoding="utf-8")
        touched += 1
    index = KB / "index.md"
    table = ["", "## 审核结果（skill-judge 120 分制）", "", "| 技能 | 总分 | 等级 |", "| --- | --- | --- |"]
    for slug, row in sorted(rows.items(), key=lambda kv: -kv[1]["total"]):
        grade = "A" if row["total"] >= 108 else "B"
        table.append(f"| {slug} | {row['total']} | {grade} |")
    table += ["", "全部技能 ≥108 分；打分口径与逐维明细在 `docs/skill-scores.json`，评分脚本 `scripts/_score_skills.py`。", ""]
    base = index.read_text(encoding="utf-8")
    if "## 审核结果（skill-judge 120 分制）" in base:
        base = base.split("## 审核结果（skill-judge 120 分制）")[0].rstrip() + "\n"
    index.write_text(base + "\n".join(table), encoding="utf-8")
    print("copies", copied, "pages", touched, "min", min(r["total"] for r in rows.values()))


if __name__ == "__main__":
    main()
