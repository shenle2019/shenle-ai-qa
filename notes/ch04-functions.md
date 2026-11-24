# 第 4 章 · 函数进阶与内存模型

> 本章目标：搞清参数怎么传、变量在哪层可见、对象在内存里怎么共享，以及为什么「可变默认参数」会咬人。

## 1. 参数的五种形态

```python
def f(a, b=2, *args, c=3, **kwargs):
    print(a, b, args, c, kwargs)

f(1)                       # 1 2 () 3 {}
f(1, 5, 7, 8, c=9, d=10)   # 1 5 (7, 8) 9 {'d': 10}
```

| 形态 | 写法 | 说明 |
| --- | --- | --- |
| 位置参数 | `a` | 按顺序传 |
| 默认参数 | `b=2` | 不传就用默认值 |
| 可变位置 | `*args` | 多余的按元组收 |
| 仅关键字 | 放在 `*args` 之后的 `c=3` | 必须用 `c=` 传 |
| 可变关键字 | `**kwargs` | 多余的按字典收 |

调用时用 `*` / `**` 解包：`f(*[1, 2], **{"c": 3})`。

## 2. 默认参数只在定义时求值一次

```python
def bad(item, bucket=[]):      # 错：所有调用共享同一个 list
    bucket.append(item)
    return bucket

bad(1)   # [1]
bad(2)   # [1, 2]  ← 不是 [2]
```

正确写法：

```python
def good(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

原理：默认值在 `def` 执行时创建一次，之后每次调用都复用那个对象。

## 3. 作用域：LEGB

Python 找名字的顺序是 **Local → Enclosing → Global → Builtin**。

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        print(x)        # enclosing
    inner()

outer()
```

函数内给名字**赋值**会让它变成局部变量，除非声明 `global` / `nonlocal`：

```python
count = 0
def inc():
    global count
    count += 1
```

实践建议：少用 `global`，把状态放进参数或对象。

## 4. 函数是一等公民

函数可以赋值给变量、当参数、当返回值：

```python
def apply(fn, value):
    return fn(value)

apply(str.upper, "abc")     # "ABC"
```

回调的典型用法是排序键：

```python
rows = [{"n": "b", "v": 2}, {"n": "a", "v": 9}]
rows.sort(key=lambda r: r["v"], reverse=True)
```

## 5. 闭包与嵌套

```python
def make_counter():
    n = 0
    def counter():
        nonlocal n
        n += 1
        return n
    return counter

c = make_counter()
c(); c()      # 1, 2
```

内层函数记住了外层函数的变量，这就是闭包。`nonlocal` 用来修改外层变量（只读时不需要声明）。

## 6. 递归

```python
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

两个必要条件：**终止条件** + **规模递减**。Python 默认递归深度约 1000，深递归要改写成迭代。

## 7. 内存模型：id、引用、拷贝

```python
a = [1, 2]
b = a            # 同一个对象，id 相同
c = a[:]         # 浅拷贝，新列表，内层元素仍共享
d = copy.deepcopy(a)   # 深拷贝，递归复制
```

- `id(obj)` 是对象地址的近似值，`a is b` 就是比较 `id`；
- 赋值不复制对象，只复制引用；
- 浅拷贝只复制第一层，嵌套的可变对象还是同一份 —— 这是「改副本影响原数据」的根源；
- 不可变对象（int/str/tuple）共享是安全的，可变对象（list/dict/set）要当心。

```python
import copy
m = [[1], [2]]
shallow = m[:]
shallow[0].append(9)     # m 也变了
deep = copy.deepcopy(m)
deep[1].append(8)        # m 不变
```

## 8. 常用函数式工具

```python
list(map(str, [1, 2]))              # ['1', '2']
list(filter(None, [0, 1, "", "a"])) # [1, 'a']
sorted(words, key=len)              # 按长度
sum(x for x in range(10) if x % 2)  # 生成器表达式，省内存
```

推导式和 `map/filter` 都能表达同样的意思，团队里选一种就好。

## 9. 本章实操

`labs/ch04-functions/`：

```powershell
python labs/ch04-functions/functions_demo.py
python -m pytest labs/ch04-functions -q
```

包含：可变默认参数的 bug 与修复、`*args/**kwargs` 收集、闭包计数器、深/浅拷贝对比、`sorted(key=)` 多字段排序。

## 10. 自测

1. `def f(x, box={})` 连续调两次，第二次的 `box` 里有几个元素？
2. 函数里读全局变量要声明 `global` 吗？修改呢？
3. `copy.copy` 与 `copy.deepcopy` 在 `[[1]]` 上的差别是什么？
4. 用 `sorted` 按「分数降序、姓名升序」排一个字典列表。

## 附：自测答案

1. 第二次调用时 `box` 里有两个元素——默认参数只在函数定义时求值一次，`{}` 被所有调用共享。默认值写 `None`，函数体里用 `if box is None: box = {}` 判空再累加；写成 `box = box or {}` 会把「显式传进来的空 dict」也换成新对象，跟本节的正解不一致。
2. 只读不用声明；要重新绑定（`x = ...`）才需要 `global`。只想修改可变对象的内容（`lst.append`）也不用 `global`。
3. `copy.copy([[1]])` 的内层还是同一个列表，改内层两边都变；`deepcopy` 连内层一起复制，互不影响。
4. `sorted(rows, key=lambda r: (-r["score"], r["name"]))`——数字取负实现降序，字符串按原序升序。

## 学生常问

**Q：`*args` 和 `**kwargs` 到底装了什么？**

A：`*args` 收集位置参数成元组，`**kwargs` 收集关键字参数成字典。顺序固定：普通参数 → 默认参数 → `*args` → 关键字-only → `**kwargs`。

**Q：闭包和普通函数有什么区别？**

A：闭包把外层函数的变量「记住」了，外层返回后这些变量还活着，所以能做计数器、缓存。代价是状态藏在函数里，调试时不好看，写的时候给它一个明确的名字。

**Q：递归会不会栈溢出？**

A：会。Python 默认递归深度约 1000，深了就 `RecursionError`。能用循环就用循环，递归只留给天然的树形结构，并且先写终止条件。

## 面试题

**Q：Python 的参数传递是值传递还是引用传递？**

A：都不是，叫「对象引用传递」：传的是对象的引用，形参和实参指向同一个对象。可变对象在函数里被修改会影响外部；给形参重新赋值只是换绑定，不影响外部。

**Q：说说 LEGB 和作用域链，实际踩过什么坑？**

A：查找顺序 Local → Enclosing → Global → Builtin。常见坑两个：函数里给变量赋值会把它变成局部变量，导致读全局时报 `UnboundLocalError`；闭包里改外层变量要 `nonlocal`。

**Q：装饰器在测试框架里有什么真实用途？**

A：计时、重试、日志、权限校验、把函数注册进用例表（`@case("登录成功")`）。关键是 `functools.wraps` 保住原函数名和文档，否则 pytest 收集到的用例名全是 `wrapper`。

## 延伸知识

- 函数是第一类对象：可以当参数、当返回值、放进列表，`map/filter/sorted(key=...)` 全靠这个。
- `functools` 三件套：`wraps`（保元信息）、`partial`（预设参数）、`lru_cache`（记忆化）。
- 别用可变默认参数；也别在函数里改传入的列表，除非函数名明确写了「原地」。
- 推导式里的变量不会泄漏到外层（Python 3），但 `for` 循环的变量会，起名时注意。
