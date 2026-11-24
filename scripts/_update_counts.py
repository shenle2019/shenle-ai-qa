from pathlib import Path

PAIRS = [
    (
        "site/index.md",
        "476 条 pytest 用例（15 条真机用例在未接手机时自动跳过），四十六个实操都能单独运行：",
        "480 条 pytest 用例（465 条离线通过 + 15 条真机用例在未接手机时自动跳过），四十六个实操都能单独运行：",
    ),
    (
        "site/labs/index.md",
        "合计 **476 条测试**（15 条真机用例需连接安卓设备）。",
        "合计 **480 条测试**（465 条离线可跑，15 条真机用例需连接安卓设备）。",
    ),
]
for rel, old, new in PAIRS:
    p = Path(rel)
    t = p.read_text(encoding="utf-8")
    assert old in t, rel
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("ok", rel)
