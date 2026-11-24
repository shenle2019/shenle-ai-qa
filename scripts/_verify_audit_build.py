from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("site/.vitepress/dist/chapters/ch32.html", "要<strong>大于</strong>服务端的处理超时"),
    ("site/.vitepress/dist/chapters/ch32.html", "5xx 与超时的比例"),
    ("site/.vitepress/dist/chapters/ch39.html", "- 失败：2"),
    ("site/.vitepress/dist/kb/interview-api.html", "408/429"),
    ("site/.vitepress/dist/index.html", "480 条"),
    ("site/.vitepress/dist/kb/rules.html", "复核与台账"),
]
for rel, needle in CHECKS:
    text = (ROOT / rel).read_text(encoding="utf-8")
    print(("OK " if needle in text else "MISS ") + f"{rel} :: {needle[:32]}")
