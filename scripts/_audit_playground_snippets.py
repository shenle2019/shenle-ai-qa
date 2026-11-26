# -*- coding: utf-8 -*-
"""把「在线运行」的四个样例抽出来，用本机 Python 真跑一遍。

目的：浏览器里跑 Pyodide 只能看到「成功/失败」，看不到具体是语法错还是逻辑错；
先用 CPython 跑一遍，能把「代码本身有问题」和「浏览器加载有问题」分开。
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / ".vitepress" / "theme" / "samples.ts"

text = SRC.read_text(encoding="utf-8")
blocks = re.findall(r"export const (\w+) = `(.*?)`", text, re.S)
print("样例数:", len(blocks))

bad = 0
for name, code in blocks:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(code)
        path = fh.name
    proc = subprocess.run([sys.executable, path], capture_output=True, text=True, encoding="utf-8")
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    print(f"\n==== {name}  rc={proc.returncode} 行数={len(code.strip().splitlines())}")
    print(out[:400] if out else "(无输出)")
    if proc.returncode != 0 or not out:
        bad += 1
        print("STDERR:", err.splitlines()[-1] if err else "(空)")

print("\n有问题的样例数:", bad)
