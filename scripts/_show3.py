from pathlib import Path

print("== skills dirs with SKILL.md")
for d in sorted(Path(".claude/skills").iterdir()):
    if d.is_dir():
        print("  ", d.name, (d / "SKILL.md").exists())

print("== ch39 passed calc")
for p in Path("labs/ch39-perf-platform").rglob("*.py"):
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if "passed" in line:
            print(p.name, i, line.strip())

print("== ch42 path param")
for p in Path("labs/ch42-assets").rglob("*.py"):
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if "PATH_PARAM" in line or "re.sub" in line or "replace(" in line:
            print(p.name, i, line.strip())

print("== ch46 table region")
lines = Path("notes/ch46-toolchain.md").read_text(encoding="utf-8").splitlines()
for i in range(13, 46):
    print(i + 1, "|", lines[i])
