---
title: 在线运行
---

<script setup>
import { basics, collections, decorator, exception, contextWindow, tokenLatency } from '../.vitepress/theme/samples'
</script>

# 在线运行

这里不用装 Python：代码在浏览器里用 CPython（WebAssembly 版）执行，点一下就跑，输出直接回显。

首次运行会下载一次运行时（约 10 MB），之后走缓存，几乎瞬开。整页共用同一份运行时，所以第二段起是秒开的。

代码框可以随便改。两点先记住：只支持标准库（requests、pytest 这类装了也跑不了）；别写 while True——浏览器里跑死循环会把这个标签页卡住，刷新才能恢复。

## 1. 基础：变量与 f-string

```python
name = "李明"
scores = [85, 92, 78]
total = sum(scores)
print(f"{name} 的总分 {total}，平均 {total / len(scores):.1f}")
```

<details class="pg-wrap">
<summary>在浏览器里跑这段</summary>

<ClientOnly>
  <Playground :code="basics" :height="150" />
</ClientOnly>

</details>

## 2. 容器与推导式

```python
orders = [
    {"id": 1, "status": "paid", "qty": 2},
    {"id": 2, "status": "new", "qty": 5},
    {"id": 3, "status": "paid", "qty": 3},
]

paid = [o["id"] for o in orders if o["status"] == "paid"]
print("已支付订单:", paid)
print("已支付件数:", sum(o["qty"] for o in orders if o["status"] == "paid"))
```

<details class="pg-wrap">
<summary>在浏览器里跑这段</summary>

<ClientOnly>
  <Playground :code="collections" :height="180" />
</ClientOnly>

</details>

## 3. 装饰器：给函数加计时

```python
import time

def timing(fn):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} 用了 {time.perf_counter() - start:.4f}s")
    return wrapper

@timing
def slow_sum(n):
    return sum(range(n))

print("结果:", slow_sum(1_000_000))
```

<details class="pg-wrap">
<summary>在浏览器里跑这段</summary>

<ClientOnly>
  <Playground :code="decorator" :height="240" />
</ClientOnly>

</details>

## 4. 异常：把失败说清楚

```python
def parse_int(raw):
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{raw!r} 不是整数") from exc

for value in ["42", "3.14"]:
    try:
        print(value, "->", parse_int(value))
    except ValueError as err:
        print("失败:", err, "| 原因:", repr(err.__cause__))
```

<details class="pg-wrap">
<summary>在浏览器里跑这段</summary>

<ClientOnly>
  <Playground :code="exception" :height="200" />
</ClientOnly>

</details>

## 5. 上下文窗口：截头还是截尾

```python
LIMIT = 40  # 假设模型上下文只放得下 40 个字符

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

## 说明

- 运行环境是 Pyodide（CPython 的 WASM 版），纯标准库都能用；
- 不能用 `pip install` 的第三方包、不能读写你本地的文件、不能起服务；
- 想跑完整实验（含 pytest），还是克隆仓库在本地跑，命令在 [实验总览](/labs/)。
