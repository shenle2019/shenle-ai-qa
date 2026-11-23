"""Repair the /labs/ sidebar group by structural scan (encoding-agnostic)."""

from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "site" / ".vitepress" / "config.mts"
lines = CONFIG.read_text(encoding="utf-8").splitlines()

fixed_block = [
    "        {",
    "          text: 'Skills 单跑记录',",
    "          items: [{ text: 'Skills 单跑记录', link: '/labs/skills/' }]",
    "        },",
]

for i in range(len(lines) - 3):
    if (
        lines[i].strip() == "{"
        and "text:" in lines[i + 1]
        and lines[i + 2].strip().startswith("{ text:")
        and lines[i + 3].strip() == "},"
    ):
        lines[i : i + 4] = fixed_block
        CONFIG.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"repaired at line {i + 1}")
        break
else:
    print("pattern not found")
