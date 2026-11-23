"""把工具链里的 huace 字样统一改成 shenle（文件名 + 文件内容）。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "labs" / "ch46-toolchain"
BINARY = {".apk", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".whl", ".pyc"}
REPLACEMENTS = [("HUACE", "SHENLE"), ("Huace", "Shenle"), ("huace", "shenle")]


def rewrite_text(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    new = text
    for old, new_word in REPLACEMENTS:
        new = new.replace(old, new_word)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for path in sorted(TARGET.rglob("*")):
        if path.is_file() and path.suffix.lower() not in BINARY:
            if rewrite_text(path):
                changed += 1
    renamed = 0
    for path in sorted(TARGET.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if "huace" in path.name.lower():
            target = path.with_name(
                path.name.replace("Huace", "Shenle").replace("HUACE", "SHENLE").replace("huace", "shenle")
            )
            path.rename(target)
            renamed += 1
    print(f"files rewritten: {changed}, paths renamed: {renamed}")

    leftover = [
        str(p.relative_to(ROOT))
        for p in TARGET.rglob("*")
        if "huace" in str(p).lower()
    ]
    print("leftover paths:", len(leftover))
    for item in leftover[:5]:
        print("  ", item)


if __name__ == "__main__":
    main()
