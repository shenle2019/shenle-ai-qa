from pathlib import Path

p = Path(__file__).resolve().parent / "_verify_live_playground_blocks.py"
text = p.read_text(encoding="utf-8")
old = 'BASE = "https://shenle2019.github.io/shenle-ai-qa/labs/playground"'
new = (
    "import os\n"
    'BASE = os.environ.get(\n'
    '    "PG_BASE", "https://shenle2019.github.io/shenle-ai-qa/labs/playground"\n'
    ")"
)
if old in text:
    p.write_text(text.replace(old, new), encoding="utf-8")
    print("patched")
else:
    print("already patched or pattern missing")
