# -*- coding: utf-8 -*-
"""把「实操总览」「在线运行」两页里贴的命令抽出来，能安全执行的先跑一遍。

不改用 PowerShell 解析（引号会被吃掉，报 At line:1 char:55），
直接用参数列表调 subprocess，跑得干净。
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")

PAGES = ["site/labs/index.md", "site/labs/playground.md"]
SKIP = ("pytest labs -q", "run.py", "--base-url", "pip install", "playwright install", "adb ")

items: list[tuple[str, str]] = []
for page in PAGES:
    text = (ROOT / page).read_text(encoding="utf-8")
    for block in re.findall(r"```(?:powershell|bash)\n(.*?)```", text, re.S):
        for raw in block.splitlines():
            cmd = raw.strip()
            if cmd and not cmd.startswith("#"):
                items.append((page, cmd))

print(f"共 {len(items)} 条命令\n")
ok = skipped = failed = 0

for page, cmd in items:
    if any(mark in cmd for mark in SKIP):
        print(f"[skip] {cmd}")
        skipped += 1
        continue

    parts = cmd.replace(".venv\\Scripts\\python.exe", PY).replace(".venv/Scripts/python.exe", PY).split()
    proc = subprocess.run(parts, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT))
    out = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
    first = next((l for l in out if l.strip()), "(无输出)")[:100]
    if proc.returncode == 0:
        print(f"[ok]   {cmd}\n       -> {first}")
        ok += 1
    else:
        print(f"[FAIL] {cmd}\n       -> rc={proc.returncode} {first}")
        failed += 1

print(f"\nok={ok} skip={skipped} fail={failed}")
