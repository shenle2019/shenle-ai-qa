from pathlib import Path

TARGETS = [
    ("notes/ch16-web-basics.md", [186]),
    ("notes/ch17-po.md", [80, 159]),
    ("notes/ch18-locators.md", [82, 96, 134]),
    ("notes/ch19-fixtures.md", [25]),
    ("notes/ch23-framework.md", [117]),
    ("notes/ch24-adb.md", [13, 63]),
    ("notes/ch29-stability.md", [43, 108]),
]
for rel, nums in TARGETS:
    lines = Path(rel).read_text(encoding="utf-8").splitlines()
    for n in nums:
        print(f"{rel}:{n}| {lines[n - 1]}")
