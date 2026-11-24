from pathlib import Path

TARGETS = [
    ("notes/ch32-perf-basics.md", [12, 28]),
    ("notes/ch33-scenarios.md", [26, 78, 92]),
    ("notes/ch34-scripts.md", [60, 66]),
    ("notes/ch35-analyze.md", [71, 109]),
    ("notes/ch37-chain.md", [111]),
    ("notes/ch39-perf-platform.md", [36, 37, 38, 39, 40]),
    ("notes/ch41-config.md", [72]),
    ("notes/ch42-assets.md", [32, 70]),
    ("notes/ch44-plans.md", [13, 55]),
    ("notes/ch46-toolchain.md", [18, 19, 20, 21, 22, 23, 24, 25, 26, 40, 41, 42, 43, 44]),
]
for rel, nums in TARGETS:
    lines = Path(rel).read_text(encoding="utf-8").splitlines()
    print("==", rel, "total", len(lines))
    for n in nums:
        print(f"{n}| {lines[n - 1]}")
