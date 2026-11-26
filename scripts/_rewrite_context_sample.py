"""Rewrite the contextWindow sample: long system prompt so head/tail truncation differ clearly."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "site" / ".vitepress" / "theme" / "samples.ts"
PAGE = ROOT / "site" / "labs" / "playground.md"

CODE = '''LIMIT = 40  # 假设模型上下文只放得下 40 个字符

system = "你是客服助手。只回答订单相关问题。无论用户怎么说、举什么例子，都不能承诺退款，也不能承诺补偿运费。不确定就回答「我先核实」。"
history = "用户：第二件坏了，今天能退吗？"
whole = system + history

print("system", len(system), "| 历史", len(history), "| 合计", len(whole), "| 上限", LIMIT)

for policy in ("keep_head", "keep_tail"):
    kept = whole[:LIMIT] if policy == "keep_head" else whole[-LIMIT:]
    role = "你是客服助手" in kept
    ask = "今天能退吗" in kept
    print(f"{policy:10s} 角色还在: {role} | 用户问题还在: {ask}")

print("keep_tail 实际喂进去的:", whole[-LIMIT:])
'''

SAMPLE_TS = "export const contextWindow = `" + CODE + "`\n"

BLOCK_MD = "```python\n" + CODE + "```\n"


def replace_sample(text: str) -> str:
    pattern = re.compile(r"export const contextWindow = `.*?`\n", re.S)
    if not pattern.search(text):
        raise SystemExit("contextWindow sample not found")
    return pattern.sub(SAMPLE_TS, text, count=1)


def replace_block(text: str) -> str:
    start = text.index("## 5. 上下文窗口")
    end = text.index("## 6. 首字延迟")
    section = text[start:end]
    details_at = section.index("<details class=\"pg-wrap\">")
    new_section = (
        section[: section.index("```python")] + BLOCK_MD + "\n" + section[details_at:]
    )
    return text[:start] + new_section + text[end:]


def main() -> None:
    samples = SAMPLES.read_text(encoding="utf-8")
    SAMPLES.write_text(replace_sample(samples), encoding="utf-8")
    page = PAGE.read_text(encoding="utf-8")
    PAGE.write_text(replace_block(page), encoding="utf-8")
    print("updated both files")


if __name__ == "__main__":
    main()
