"""把每章「延伸知识 / 常见坑 / 自测答案 / 学生常问 / 面试题」里的可判定断言抽出来，
标出带方向词、绝对词、默认值词的句子，供人工逐条复核（CONTENT-RULES.md 第七节）。

用法：
    .\.venv\Scripts\python.exe scripts\_audit_claims.py            # 全部打印
    .\.venv\Scripts\python.exe scripts\_audit_claims.py --flagged  # 只打印被标记的

输出里每条前面有 [方向]/[绝对]/[默认] 标签，没有标签的说明不含风险词，也要扫一眼。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"

SECTIONS = ("延伸知识", "常见坑", "常见错误", "附：自测答案", "学生常问", "面试题")

# 方向词：最容易写反的一类
DIRECTION = re.compile(
    r"小于|大于|少于|多于|早于|晚于|先于|后于|低于|高于|短于|长于|之前|之后|"
    r"上游|下游|先[^，。]{0,8}再|反过来"
)
# 绝对词：没有前提就下结论
ABSOLUTE = re.compile(r"一定|必然|永远|绝对|从不|所有|任何|必须|禁止|不可能")
# 默认值/隐式行为：最容易记错
DEFAULT = re.compile(
    r"默认|默认值|默认为|隐式|自动|内置|等同于|相当于|等价于|"
    r"timeout|超时|重试|状态码|退出码|幂等|分位|TPS|RT"
)


def sentences(block: str) -> list[str]:
    """按行切，保留列表项整行；过长再按句号切。"""
    out: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*]\s*|^\d+[.、]\s*", "", line)
        if len(line) > 160:
            out.extend(s.strip() for s in re.split(r"(?<=[。；])", line) if s.strip())
        else:
            out.append(line)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flagged", action="store_true", help="只打印被标记的句子")
    args = ap.parse_args()

    total = flagged = 0
    for path in sorted(NOTES.glob("ch*.md")):
        text = path.read_text(encoding="utf-8")
        parts = re.split(r"^##\s+", text, flags=re.M)
        printed_header = False
        for part in parts:
            head, _, body = part.partition("\n")
            if head.strip() not in SECTIONS:
                continue
            for sent in sentences(body):
                total += 1
                tags = []
                if DIRECTION.search(sent):
                    tags.append("方向")
                if ABSOLUTE.search(sent):
                    tags.append("绝对")
                if DEFAULT.search(sent):
                    tags.append("默认")
                if args.flagged and not tags:
                    continue
                if not printed_header:
                    print(f"\n=== {path.name} ===")
                    printed_header = True
                flagged += bool(tags)
                mark = f"[{'/'.join(tags)}] " if tags else "        "
                print(f"{mark}{sent[:150]}")

    print(f"\n共 {total} 条断言，其中 {flagged} 条含风险词，需要逐条对照事实复核。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
