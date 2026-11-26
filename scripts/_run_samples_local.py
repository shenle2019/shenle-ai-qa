"""Run every sample in samples.ts with local CPython and print real output."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "site" / ".vitepress" / "theme" / "samples.ts"

pattern = re.compile(r"export const (\w+) = `(.*?)`\n", re.S)
text = SAMPLES.read_text(encoding="utf-8")
blocks = pattern.findall(text)
print(f"samples: {len(blocks)}")

failures = 0
for name, body in blocks:
    code = body.replace("\\\\", "\\")
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0
    failures += 0 if ok else 1
    print(f"\n=== {name} rc={proc.returncode} ===")
    print(proc.stdout.strip())
    if proc.stderr.strip():
        print("STDERR:", proc.stderr.strip()[:400])

print(f"\nfailures: {failures}")
