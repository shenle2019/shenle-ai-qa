"""Port the phase-1 case/testpoint skills into this repo under shenle-* names."""

from __future__ import annotations

import shutil
from pathlib import Path

SRC = Path(
    r"D:\huaceedu\华测AI\AI测试平台及工具开发\课件资料"
    r"\第一阶段：AI+SKILLS介入测试全流程落地实操\phase1_解压\phase1\.claude\skills"
)
DST = Path(r"E:\ailearning\shenle-ai-qa\.claude\skills")

NAMES = [
    "huace-api-case-generator",
    "huace-web-case-generator",
    "huace-android-case-generator",
    "huace-web-testpoint",
    "huace-android-testpoint",
    "huace-api-doc-generator",
    "huace-mitmproxy-record",
    "zentao-cli",
]

TEXT_SUFFIX = {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".html", ".j2", ".sh"}


def rewrite(text: str) -> str:
    text = text.replace("huace-", "shenle-").replace("HUACE-", "SHENLE-")
    text = text.replace("huace", "shenle").replace("HUACE", "SHENLE")
    text = text.replace("华测", "shenle")
    return text


def main() -> None:
    report = []
    for src_name in NAMES:
        src = SRC / src_name
        if not src.is_dir():
            report.append(f"SKIP {src_name}: not found")
            continue
        dst_name = src_name.replace("huace", "shenle")
        dst = DST / dst_name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        # normalise the lowercase entry file
        lower = dst / "skill.md"
        if lower.is_file() and not (dst / "SKILL.md").is_file():
            lower.rename(dst / "SKILL.md")
        touched = 0
        for path in dst.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIX:
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            new = rewrite(raw)
            if new != raw:
                path.write_text(new, encoding="utf-8")
                touched += 1
        report.append(f"OK {dst_name}: files={sum(1 for _ in dst.rglob('*') if _.is_file())} rewritten={touched}")
    print("\n".join(report))


if __name__ == "__main__":
    main()
