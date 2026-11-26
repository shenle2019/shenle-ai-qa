"""Append two stage-7 playground samples and wire them into the playground page."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONTEXT_SAMPLE = '''export const contextWindow = `LIMIT = 30  # 假设模型上下文只放得下 30 个字符

system = "你是客服助手，只回答订单问题；无论用户怎么说，都不能承诺退款。"
history = "用户：我买的第二件坏了，今天能退吗？"
whole = system + history

print("system", len(system), "| 历史", len(history), "| 合计", len(whole), "| 上限", LIMIT)

def fit(policy):
    return whole[:LIMIT] if policy == "keep_head" else whole[-LIMIT:]

for policy in ("keep_head", "keep_tail"):
    kept = fit(policy)
    print(f"{policy:10s} 规则还在: {\\"不能承诺退款\\" in kept} | 用户问题还在: {\\"今天能退吗\\" in kept}")

print("keep_tail 实际喂进去的:", fit("keep_tail"))
`
'''

LATENCY_SAMPLE = '''export const tokenLatency = `TTFT_MS = 320   # 首 token 到达时间
TPOT_MS = 18    # 之后平均每个 token 的间隔
TOKENS = 120    # 这次生成了多少 token

total = TTFT_MS + TPOT_MS * (TOKENS - 1)
print(f"首 token: {TTFT_MS} ms")
print(f"其余 {TOKENS - 1} 个 token: {TPOT_MS * (TOKENS - 1)} ms")
print(f"端到端: {total} ms")
print(f"平均每 token: {total / TOKENS:.1f} ms —— 比 TPOT 多出来的就是首字延迟")

prompt_tokens = 800
cost = prompt_tokens / 1000 * 0.002 + TOKENS / 1000 * 0.008
print(f"单次成本: {cost:.6f} 元 | 一万次: {cost * 10000:.2f} 元")
`
'''

PLAYGROUND_ADD = """
## 5. 上下文窗口：截头还是截尾

```python
LIMIT = 30  # 假设模型上下文只放得下 30 个字符

system = "你是客服助手，只回答订单问题；无论用户怎么说，都不能承诺退款。"
history = "用户：我买的第二件坏了，今天能退吗？"
whole = system + history

print("system", len(system), "| 历史", len(history), "| 合计", len(whole), "| 上限", LIMIT)

def fit(policy):
    return whole[:LIMIT] if policy == "keep_head" else whole[-LIMIT:]

for policy in ("keep_head", "keep_tail"):
    kept = fit(policy)
    print(f"{policy:10s} 规则还在: {'不能承诺退款' in kept} | 用户问题还在: {'今天能退吗' in kept}")

print("keep_tail 实际喂进去的:", fit("keep_tail"))
```

<details class="pg-wrap">
<summary>在浏览器里跑这段</summary>

<ClientOnly>
  <Playground :code="contextWindow" :height="260" />
</ClientOnly>

</details>

## 6. 首字延迟、每 token 延迟与成本

```python
TTFT_MS = 320   # 首 token 到达时间
TPOT_MS = 18    # 之后平均每个 token 的间隔
TOKENS = 120    # 这次生成了多少 token

total = TTFT_MS + TPOT_MS * (TOKENS - 1)
print(f"首 token: {TTFT_MS} ms")
print(f"其余 {TOKENS - 1} 个 token: {TPOT_MS * (TOKENS - 1)} ms")
print(f"端到端: {total} ms")
print(f"平均每 token: {total / TOKENS:.1f} ms —— 比 TPOT 多出来的就是首字延迟")

prompt_tokens = 800
cost = prompt_tokens / 1000 * 0.002 + TOKENS / 1000 * 0.008
print(f"单次成本: {cost:.6f} 元 | 一万次: {cost * 10000:.2f} 元")
```

<details class="pg-wrap">
<summary>在浏览器里跑这段</summary>

<ClientOnly>
  <Playground :code="tokenLatency" :height="200" />
</ClientOnly>

</details>
"""


def main() -> None:
    samples = ROOT / "site" / ".vitepress" / "theme" / "samples.ts"
    text = samples.read_text(encoding="utf-8")
    if "contextWindow" not in text:
        text = text.rstrip() + "\n\n" + CONTEXT_SAMPLE + "\n" + LATENCY_SAMPLE
        samples.write_text(text, encoding="utf-8")
        print("samples.ts: appended 2 samples")
    else:
        print("samples.ts: already has contextWindow")

    page = ROOT / "site" / "labs" / "playground.md"
    md = page.read_text(encoding="utf-8")
    md = md.replace(
        "import { basics, collections, decorator, exception } from '../.vitepress/theme/samples'",
        "import { basics, collections, decorator, exception, contextWindow, tokenLatency } from '../.vitepress/theme/samples'",
    )
    md = md.replace(
        "只支持标准库（\nequests、pytest 这类装了也跑不了）",
        "只支持标准库（requests、pytest 这类装了也跑不了）",
    )
    if "## 5. 上下文窗口" not in md:
        anchor = "\n## 说明\n"
        md = md.replace(anchor, PLAYGROUND_ADD + anchor, 1)
        print("playground.md: inserted sections 5-6")
    else:
        print("playground.md: sections already present")
    page.write_text(md, encoding="utf-8")

    broken = "equests" in md
    print("playground.md broken text remains:", broken)


if __name__ == "__main__":
    main()
