from pathlib import Path

p = Path("scripts/_publish_skills.py")
t = p.read_text(encoding="utf-8")

old = """        entry = skill / "SKILL.md"
        if not entry.is_file():
            # 少数技能是「包内带 skill/ 子目录」的形态，SKILL.md 在下一层
            nested = sorted(skill.glob("*/SKILL.md"))
            if len(nested) != 1:
                continue
            entry = nested[0]
            skill = entry.parent"""
new = """        entry = skill / "SKILL.md"
        if not entry.is_file():
            # 少数技能是「包内再套一层 skill/<name>/」的形态，SKILL.md 在更深的目录里
            nested = sorted(p for p in skill.glob("**/SKILL.md") if p.parent != skill)
            if len(nested) != 1:
                continue
            entry = nested[0]"""
assert old in t
t = t.replace(old, new, 1)
p.write_text(t, encoding="utf-8")
print("publisher patched v2")
