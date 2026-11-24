"""device-record 正文压到 300 行以内：把四个 Step 的命令细节拆进 references/steps.md。"""

from __future__ import annotations

import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-device-record"
path = SKILL / "SKILL.md"
text = path.read_text(encoding="utf-8")

# 把 Step 1~3 的明细整段搬到 references/steps.md，正文只留「做什么 + 判定标准」
moved_headers = ("## Step 1: 环境预检", "## Step 2: 确认设备", "## Step 3: 启动录制", "## Step 4: 收尾")
parts = re.split(r"^(## .+)$", text, flags=re.M)
head = parts[0]
sections = [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]

moved = [(h, b) for h, b in sections if h in moved_headers]
kept = [(h, b) for h, b in sections if h not in moved_headers]
if not moved:
    print("没有可搬的 Step 段，跳过")
    raise SystemExit(0)

refs = SKILL / "references"
refs.mkdir(exist_ok=True)
steps_md = "# shenle-device-record 分步明细\n\n正文只留判定标准，命令与参数在这里。\n\n"
for h, b in moved:
    steps_md += h + "\n" + b.strip() + "\n\n"
(refs / "steps.md").write_text(steps_md, encoding="utf-8")

summary = """## 四个 Step 的判定标准

每一步的完整命令、参数、输出样例都在 `references/steps.md`，正文只留「怎么判断这步算过」。

| 步骤 | 过关标准 | 不过就停 |
| --- | --- | --- |
| 1 环境预检 | 依赖 `adb` 与 `shenle-device-record` 都能跑，版本打印正常 | 缺依赖先装，不往下走 |
| 2 确认设备 | `adb devices` 里目标设备是 `device` | `unauthorized` / `offline` 就修，别硬采 |
| 3 启动录制 | 产物目录出现新的时间戳批次，里面有截图与 JSON | 只有一半就当失败 |
| 4 收尾 | JSON 的 `elements` 与截图对得上，进程已退出 | 层级为空要重采 |

"""

out = head + summary + "".join(h + b for h, b in kept)
path.write_text(out, encoding="utf-8")
print("正文", len(out.splitlines()), "行；明细 ->", refs / "steps.md", len(steps_md.splitlines()), "行")
