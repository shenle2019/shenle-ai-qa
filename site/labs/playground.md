---
title: 在线运行
---

<script setup>
import { basics, collections, decorator, exception } from '../.vitepress/theme/samples'
</script>

# 在线运行

这里不用装 Python：代码在浏览器里用 CPython（WebAssembly 版）执行，点一下就跑，输出直接回显。

首次运行会下载一次运行时（约 10 MB），之后走缓存，几乎瞬开。代码框可以随便改。

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

## 说明

- 运行环境是 Pyodide（CPython 的 WASM 版），纯标准库都能用；
- 不能用 `pip install` 的第三方包、不能读写你本地的文件、不能起服务；
- 想跑完整实验（含 pytest），还是克隆仓库在本地跑，命令在 [实验总览](/labs/)。
