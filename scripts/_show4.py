import re
from pathlib import Path

print("== ch39 Report class")
p = Path("labs/ch39-perf-platform/perf_platform.py")
lines = p.read_text(encoding="utf-8").splitlines()
for i in range(38, 100):
    print(i + 1, "|", lines[i])

print("== locate phrases")
needles = [
    ("notes/ch42-assets.md", "路径参数用正则拒绝"),
    ("notes/ch42-assets.md", "404/405"),
    ("notes/ch42-assets.md", "探活"),
    ("notes/ch44-plans.md", "三个状态"),
    ("notes/ch44-plans.md", "挤占"),
    ("notes/ch46-toolchain.md", "L10"),
]
for rel, needle in needles:
    for i, line in enumerate(Path(rel).read_text(encoding="utf-8").splitlines(), 1):
        if needle in line:
            print(f"{rel}:{i}| {line}")

print("== apps with pyproject")
for d in sorted(Path("labs/ch46-toolchain/apps").iterdir()):
    if d.is_dir():
        print("  ", d.name, (d / "pyproject.toml").exists())
