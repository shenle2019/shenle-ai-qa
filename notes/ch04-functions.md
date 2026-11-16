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

## 9. 本章实验

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
