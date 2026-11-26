from pathlib import Path

root = Path(__file__).resolve().parent.parent / "labs"

renames = {
    "ch47-prompt-cases": ("cases.py", "ch47_cases.py"),
    "ch48-token-perf": ("cases.py", "ch48_cases.py"),
    "ch49-prompt-regression": ("cases.py", "ch49_cases.py"),
    "ch50-rag-eval": ("cases.py", "ch50_cases.py"),
}

for folder, (old, new) in renames.items():
    d = root / folder
    src = d / old
    if not src.exists():
        print("skip", src)
        continue
    src.rename(d / new)
    prefix = new[:-3]  # ch47_cases
    for py in d.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        if "from cases import" in text:
            text = text.replace("from cases import", f"from {prefix} import")
            py.write_text(text, encoding="utf-8")
            print("rewrote import in", py.name)
    print("renamed", folder, old, "->", new)
