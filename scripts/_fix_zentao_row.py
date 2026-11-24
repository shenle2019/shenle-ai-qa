from pathlib import Path

p = Path("site/kb/skills/index.md")
lines = p.read_text(encoding="utf-8").splitlines()
i = 35
assert lines[i].lstrip().startswith("| `zentao-cli`"), lines[i]
lines[i] = lines[i].rstrip()[: -len("**109** |")].rstrip() + " |"
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("fixed:", lines[i])
