"""把 ch46 工具链里自带 skill/ 的包，补登记为仓库技能。

ch46 的 6 个包里有 2 个（api-cli / device-record）当时只留了包内 skill 目录，
没在 .claude/skills 下注册，导致手册页存在、技能目录缺失、也打不出 zip。

用法：python scripts/_restore_ch46_skills.py [--check]
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "labs" / "ch46-toolchain" / "apps"
SKILLS = ROOT / ".claude" / "skills"
NAMES = ("shenle-api-cli", "shenle-device-record")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    for name in NAMES:
        src = APPS / name / "skill" / name
        if not (src / "SKILL.md").is_file():
            print(f"缺源：{src}")
            continue
        dst = SKILLS / name
        files = sorted(p for p in src.rglob("*") if p.is_file())
        print(f"{name}: 源 {len(files)} 个文件 -> {dst}")
        if args.check:
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print("  已复制", [p.relative_to(src).as_posix() for p in files])
    print("检查完成" if args.check else "恢复完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
