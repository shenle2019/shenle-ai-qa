"""把「一页速查」拆进 references/，让正文回到 300 行以内并触发渐进披露加分。"""

from __future__ import annotations

import re
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / ".claude" / "skills"

TARGETS = {
    "shenle-api-cli": "shenle-api-cli",
    "shenle-device-record": "shenle-device-record",
}

for name in TARGETS:
    path = SKILLS / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## 一页速查\n(.*)\Z", text, re.S | re.M)
    if not m:
        print(f"{name}: 没找到一页速查，跳过")
        continue
    table = m.group(1).strip()
    refs = SKILLS / name / "references"
    refs.mkdir(exist_ok=True)
    (refs / "quick-reference.md").write_text(
        f"# {name} 一页速查\n\n{name} 的高频命令与对照表，动手前先扫一眼。\n\n{table}\n",
        encoding="utf-8",
    )
    body = text[: m.start()].rstrip()
    note = (
        "\n\n## 速查表在 references 里\n\n"
        "MANDATORY：动手前先读 `references/quick-reference.md`，那里是高频命令与对照表；"
        "正文只讲判断与避坑，不重复贴命令清单。\n"
    )
    path.write_text(body + note, encoding="utf-8")
    print(f"{name}: 正文 {len((body + note).splitlines())} 行，速查表移到 references/quick-reference.md")
