# 第 2 章 · 条件、循环与函数入门

> 本章目标：让程序会「分叉」和「重复」，并把重复逻辑收进函数。

## 1. 条件语句的三种形态

```python
# 单分支
if a >= b:
    print("a 大")

# 双分支
if x >= y:
    print("x 大")
else:
    print("y 大")

# 多分支：从上往下匹配，命中即跳出
score = 78
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"
```

要点：

- 条件表达式的结果会被当作真假判断（`0`、`""`、`[]`、`None` 为假）；
- `elif` 之间是互斥的，顺序错了结果就错（把 `>= 60` 写在 `>= 90` 前面，90 分也会判成 C）；
- 三元表达式适合一句话：`grade = "A" if score >= 90 else "B"`。

## 2. 循环：for 与 while

```python
# for：遍历可迭代对象
for i in range(1, 11):        # 1..10，不含 11
    result *= i

for ch in "abc":
    print(ch)

# while：条件为真就继续
n = 3
while n > 0:
    print(n)
    n -= 1
```

`range` 的三种写法：`range(5)` → 0..4；`range(1, 6)` → 1..5；`range(0, 10, 2)` → 0,2,4,6,8。

**选择建议**：次数已知或要遍历集合用 `for`；次数未知、靠条件退出用 `while`。`while` 一定要确认有让条件变假的路径，否则死循环。

## 3. break / continue / else

```python
for i in range(1, 100):
    if i * i > 50:
        print("第一个平方超过 50 的是", i)
        break          # 整个循环结束
    if i % 2 == 0:
        continue       # 跳过本次，进入下一次
```

`for ... else` 是 Python 特色：循环**没有被 break 打断**时执行 else，适合「找一圈没找到」的场景。

```python
for user in users:
    if user == target:
        print("找到了")
        break
else:
    print("没有这个人")
```

## 4. 嵌套循环

```python
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}x{i}={i*j}", end="\t")
    print()
```

九九乘法表的关键在**内层上界跟着外层走**（`i + 1`）。嵌套的复杂度是乘积：外层 9 次 × 内层平均 5 次 ≈ 45 次。

## 5. 函数：把一段逻辑命名

```python
def max_of_three(a, b, c):
    """返回三个数里的最大值。"""
    result = a
    if b > result:
        result = b
    if c > result:
        result = c
    return result
```

- `def` 定义，缩进体是函数体；
- `return` 结束函数并交回值；没有 `return` 时返回 `None`；
- 参数可以有默认值：`def greet(name, prefix="你好")`；
- 文档字符串写在函数第一行，`help(f)` 能看到。

## 6. return 与 break 的区别

这两个最容易被混：

| | 作用范围 | 之后发生什么 |
| --- | --- | --- |
| `break` | 只跳出**当前这一层**循环 | 循环后面的代码继续执行 |
| `return` | 结束**整个函数** | 函数内剩余代码（含外层循环）都不再执行 |

```python
def find_first_even(nums):
    for n in nums:
        if n % 2 == 0:
            return n      # 直接交回结果，函数结束
    return None           # 一个都没有

def count_even(nums):
    count = 0
    for n in nums:
        if n % 2 == 0:
            count += 1
        # 这里用 continue 只是跳过，不影响计数逻辑
    return count
```

在嵌套循环里想「一次跳出两层」，`break` 做不到，要么用标志位，要么把内层抽成函数用 `return`。

## 7. 一个能用的例子：重试

```python
def retry(times: int, fn):
    for attempt in range(1, times + 1):
        try:
            return fn()
        except Exception as exc:
            last = exc
            print(f"第 {attempt} 次失败：{exc}")
    raise last
```

这段把「循环 + 条件 + 函数 + 异常」串起来了，第 6 章会真的用上。

## 8. 本章实操

`labs/ch02-control-flow/`：

```powershell
python labs/ch02-control-flow/flow.py
python -m pytest labs/ch02-control-flow -q
```

包含：分数转等级（边界值 90/80/60）、九九乘法表生成、`find_first_even` 与 `break` 的对比、`retry` 重试器。

## 9. 自测

1. 把 `>= 60` 的判断挪到 `>= 90` 前面，90 分会得到什么？为什么？
2. `for ... else` 里的 else 什么时候**不**执行？
3. 嵌套两层循环，内层 `break` 之后外层还在跑吗？
4. 写一个 `count_words(text)`，统计一段文字里每个单词出现次数（提示：先 `split()`，再用字典，第 3 章会正式讲字典）。

## 附：自测答案

1. 90 分会落进 `>= 60` 那一支，被判成及格甚至更低——条件从上往下走，第一个命中的分支直接返回。高优先级的判断必须写在前面。
2. 循环被 `break` 打断时 `else` 不执行；循环自然跑完（包括空循环）才执行。它等价于「没找到才走这里」。
3. 还在跑。`break` 只跳出它所在的那一层，外层循环继续下一轮。要一起退出，用标志位或把逻辑抽成函数 `return`。
4. ```python
   def count_words(text: str) -> dict:
       result = {}
       for word in text.split():
           result[word] = result.get(word, 0) + 1
       return result
   ```

## 学生常问

**Q：`while True` 会不会写死循环？**

A：只要里面有明确的退出条件（`break`、`return` 或状态翻转）就不会。真正危险的是「条件依赖的变量在循环里没被更新」，写完先问自己：哪一行会让条件变成假？

**Q：`range(1, 5)` 为什么没有 5？**

A：区间左闭右开。想包含 5 就是 `range(1, 6)`，或者 `range(1, n + 1)`。切片、`range` 都是这个约定，记住一次就够。

**Q：`continue` 和 `break` 分不清怎么办？**

A：`continue` 是「这一轮到此为止，下一轮继续」；`break` 是「整个循环到此为止」。用打印计数器的办法跑一遍，比背定义快。

## 面试题

**Q：`for ... else` 的执行时机是什么？举个真实用途。**

A：循环正常结束执行 `else`，`break` 跳出则不执行。典型用途是「查找」：遍历列表找目标，找到就 `break`，`else` 分支里报「没找到」，比设标志位干净。

**Q：三元表达式、`and/or` 短路在测试代码里怎么用？**

A：`value = a if cond else b` 只求值一个分支；`x = cfg.get("timeout") or 5` 利用 `or` 短路给默认值（注意 `0`、`""` 也会被当假值，这种场景要写 `if x is None`）。

**Q：函数里 `return` 和 `break` 谁先谁后？**

A：`return` 直接结束整个函数，`break` 只结束当前循环。循环里想带结果出去，用 `return`；只是想跳出继续执行后面的代码，用 `break`。

## 延伸知识

- 条件写法：`if 0 < size <= 100` 是合法链式比较，别再写 `0 < size and size <= 100`。
- 早返回：把「参数不合法」的守卫写在函数开头 `return` / `raise`，主逻辑少一层缩进。
- 循环优先用 `enumerate`、`zip`、`items()`，比下标和 `range(len(...))` 可读。
- 别在遍历列表时增删元素，要改就先复制一份，或者收集起来循环后统一处理。
