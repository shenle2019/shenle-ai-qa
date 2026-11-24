import re
from pathlib import Path

p = Path("site/kb/skills/index.md")
lines = p.read_text(encoding="utf-8").splitlines()
fixed = 0
for i in range(28, 36):
    if re.search(r"\|\s*\|\s*$", lines[i]):
        lines[i] = re.sub(r"\|\s*\|\s*$", "|", lines[i]).rstrip()
        fixed += 1
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("fixed rows:", fixed)
for i in range(28, 36):
    print(i + 1, "|", lines[i][-46:])
