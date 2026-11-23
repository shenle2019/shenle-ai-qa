"""Add a Skills library entry to the site nav/sidebar and repair two mojibake labels."""

from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "site" / ".vitepress" / "config.mts"
text = CONFIG.read_text(encoding="utf-8")
lines = text.splitlines()

KB = "{ text: 'Skills 手册（13 个技能）', link: '/kb/skills/' },"
LAB = "{ text: 'Skills 单跑记录', link: '/labs/skills/' },"
LIB = "{ text: 'Skills 库（可预览下载）', link: '/skills/' },"

out = []
kb_seen = lab_seen = 0
for line in lines:
    stripped = line.strip()
    if "link: '/kb/skills/'" in line:
        indent = line[: len(line) - len(line.lstrip())]
        if not any("link: '/skills/'" in prev for prev in out[-2:]):
            out.append(indent + LIB)
        out.append(indent + KB)
        kb_seen += 1
        continue
    if "link: '/labs/skills/'" in line:
        indent = line[: len(line) - len(line.lstrip())]
        out.append(indent + LAB)
        lab_seen += 1
        continue
    out.append(line)

body = "\n".join(out) + "\n"

nav_anchor = "{ text: '在线运行', link: '/labs/playground' },"
if nav_anchor in body and "'/skills/'" not in body.split("sidebar:")[0]:
    body = body.replace(nav_anchor, nav_anchor + "\n    { text: 'Skills 库', link: '/skills/' },", 1)

CONFIG.write_text(body, encoding="utf-8")
print(f"kb lines {kb_seen}, lab lines {lab_seen}")
print("nav has skills:", "'/skills/'" in body.split("sidebar:")[0])
