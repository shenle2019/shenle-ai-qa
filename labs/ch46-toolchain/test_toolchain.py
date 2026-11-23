"""工具链复刻的自检：技能清单、命令注册、命名净化。"""

from __future__ import annotations

import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = ROOT / "labs" / "ch46-toolchain"
SKILLS = ROOT / ".claude" / "skills"

EXPECTED_SKILLS = {
    "playwright-cli",
    "shenle-android-cli",
    "shenle-api-record",
    "shenle-dynamic-function-generator",
    "shenle-report-generate-html",
    "shenle-test-flow-builder",
    "shenle-test-plan-generator",
    "shenle-test-runner",
    "shenle-web-cli",
    "shenle-web-record",
}

EXPECTED_COMMANDS = {
    "shenle-android-cli",
    "shenle-api-cli",
    "shenle-api-record",
    "shenle-device-record",
    "shenle-web-cli",
    "shenle-web-record",
}


def _console_scripts() -> dict[str, str]:
    found: dict[str, str] = {}
    for dist in metadata.distributions():
        name = (dist.metadata["Name"] or "").lower()
        if not name.startswith("shenle-"):
            continue
        for entry in dist.entry_points:
            if entry.group == "console_scripts":
                found[entry.name] = dist.version
    return found


def test_all_skills_are_registered() -> None:
    names = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    missing = EXPECTED_SKILLS - names
    assert not missing, f"缺少技能：{sorted(missing)}"


def test_every_skill_has_readable_frontmatter() -> None:
    for name in EXPECTED_SKILLS:
        docs = list((SKILLS / name).rglob("SKILL.md"))
        assert docs, f"{name} 没有 SKILL.md"
        text = docs[0].read_text(encoding="utf-8")
        assert text.lstrip().startswith("---"), f"{name} 的 SKILL.md 缺少 frontmatter"
        assert re.search(r"^name:\s*\S+", text, re.M), f"{name} 的 frontmatter 没有 name"


def test_console_scripts_are_installed() -> None:
    scripts = _console_scripts()
    missing = EXPECTED_COMMANDS - set(scripts)
    assert not missing, f"未注册的命令：{sorted(missing)}"


def test_console_scripts_report_version() -> None:
    for command in sorted(EXPECTED_COMMANDS):
        exe = Path(sys.executable).with_name(f"{command}.exe")
        if not exe.exists():
            exe = Path(sys.executable).parent / command
        proc = subprocess.run(
            [str(exe), "--version"], capture_output=True, text=True, timeout=60
        )
        assert command in (proc.stdout + proc.stderr), f"{command} --version 没有输出版本"


def test_toolchain_sources_are_present() -> None:
    apps = TOOLCHAIN / "apps"
    assert apps.is_dir()
    packages = [p for p in apps.iterdir() if p.is_dir() and (p / "pyproject.toml").exists()]
    assert len(packages) >= 6, f"应有至少 6 个可安装工具，实际 {len(packages)}"


def test_no_legacy_vendor_name_left() -> None:
    banned = "hua" + "ce"
    hits = []
    for path in TOOLCHAIN.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".apk", ".pyc", ".png"}:
            continue
        if banned in path.read_text(encoding="utf-8", errors="ignore").lower():
            hits.append(str(path.relative_to(ROOT)))
    assert not hits, f"仍有旧厂牌字样：{hits[:3]}"


def test_no_legacy_vendor_name_in_paths() -> None:
    banned = "hua" + "ce"
    hits = [str(p.relative_to(ROOT)) for p in TOOLCHAIN.rglob("*") if banned in str(p).lower()]
    assert not hits, f"路径仍有旧厂牌字样：{hits[:3]}"
