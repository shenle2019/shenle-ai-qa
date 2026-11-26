"""Rewrite the contextWindow sample so it runs on Python 3.8+ (no backslash in f-string)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "site" / ".vitepress" / "theme" / "samples.ts"
PAGE = ROOT / "site" / "labs" / "playground.md"

OLD_LOOP = '''for policy in ("keep_head", "keep_tail"):
    kept = fit(policy)
    print(f"{policy:10s} 规则还在: {\\"不能承诺退款\\" in kept} | 用户问题还在: {\\"今天能退吗\\" in kept}")
'''

NEW_LOOP = '''for policy in ("keep_head", "keep_tail"):
    kept = fit(policy)
    rule_ok = "不能承诺退款" in kept
    ask_ok = "今天能退吗" in kept
    print(f"{policy:10s} 规则还在: {rule_ok} | 用户问题还在: {ask_ok}")
'''


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if OLD_LOOP not in text:
        print(f"{path.name}: OLD_LOOP not found (maybe already patched)")
        return
    text = text.replace(OLD_LOOP, NEW_LOOP)
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: patched")


patch(SAMPLES)
patch(PAGE)
