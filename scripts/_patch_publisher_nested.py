from pathlib import Path

p = Path("scripts/_publish_skills.py")
t = p.read_text(encoding="utf-8")

old = """    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        entry = skill / "SKILL.md"
        if not entry.is_file():
            continue
        name = skill.name
        text = entry.read_text(encoding="utf-8", errors="replace")"""
new = """    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        entry = skill / "SKILL.md"
        if not entry.is_file():
            # 少数技能是「包内带 skill/ 子目录」的形态，SKILL.md 在下一层
            nested = sorted(skill.glob("*/SKILL.md"))
            if len(nested) != 1:
                continue
            entry = nested[0]
            skill = entry.parent
        name = skill.name
        text = entry.read_text(encoding="utf-8", errors="replace")"""
assert old in t
t = t.replace(old, new, 1)

old_refs = '        refs = sorted((skill / "references").glob("*.md")) if (skill / "references").is_dir() else []'
new_refs = """        refs = sorted((skill / "references").glob("*.md")) if (skill / "references").is_dir() else []
        if not refs:
            refs = sorted(skill.glob("*/references/*.md"))"""
assert old_refs in t
t = t.replace(old_refs, new_refs, 1)

p.write_text(t, encoding="utf-8")
print("publisher patched")
