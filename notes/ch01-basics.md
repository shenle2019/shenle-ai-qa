# 第 1 章 · 环境、第一个程序与基础语法

> 本章目标：搞清楚「代码跑在哪」，然后一次性把变量、类型转换、输入输出、运算符这几块地基打平。

## 1. 三个角色：解释器、编辑器、终端

| 角色 | 做什么 | 常见选择 |
| --- | --- | --- |
| 解释器 | 真正执行 `.py`，把源码翻译成机器动作 | CPython 3.11+ |
| 编辑器 / IDE | 编辑文件、补全、调试，本身不执行 | VS Code、PyCharm |
| 终端 | 敲命令、看输出、装依赖 | PowerShell、bash |

链路是：**终端调用解释器 → 解释器读文件 → 输出回到终端**。IDE 的「运行」按钮不过是在后台替你敲了 `python xxx.py`。

排查「代码不跑」的三步：文件存了吗 → 终端当前目录对不对 → `python -V` 是哪个解释器。

```powershell
python -V                 # Python 3.11.9
where python              # 看有没有装出多份
python hello.py           # 在当前目录执行
```

## 2. 第一个程序与注释

```python
# 单行注释：井号后面到行尾
print("hello")

"""
三引号是多行字符串，
放在语句位置时常被当作多行注释用。
"""
```

`print()` 默认换行；`end=` 可以改结尾：

```python
print("A", end=" ")
print("B")        # A B
print()           # 空行
```

## 3. 变量与四种基础类型

```python
name = "李明"     # str
age = 18          # int
height = 1.75     # float
passed = True     # bool
```

- 变量是「有名字的盒子」，赋值即绑定；
- Python 是**动态类型**：同一个名字可以先后指向不同类型的值；
- 用 `type(x)` 查类型，`isinstance(x, int)` 做判断更稳妥（`bool` 是 `int` 的子类，`isinstance(True, int)` 为 `True`）。

## 4. 类型转换

```python
int("56")        # 56
int(34.87)       # 34   截断，不四舍五入
float("3.14")    # 3.14
str(89)          # "89"
bool(0)          # False
bool("")         # False
bool("False")    # True  非空字符串一律为真
```

`input()` 拿到的**永远是字符串**，要算数必须先转。这一条能解释掉初学阶段一半的报错。

```python
a = "1"; b = "2"
print(a + b)             # 12   字符串拼接
print(int(a) + int(b))   # 3    数值相加
```

## 5. 输出格式化

```python
n = 8
print("你有{}个".format(n))
print("你有%d个" % n)          # 老式写法，能读但别新写
print(f"你有{n}个")            # 推荐
print(f"{3.14159:.2f}")        # 3.14 保留两位
print(f"{n:>5}")               # 右对齐宽度 5
```

f-string 里可以写表达式：`f"{n * 2}"`、`f"{name.upper()}"`。

## 6. 运算符

| 类别 | 运算符 | 说明 |
| --- | --- | --- |
| 算术 | `+ - * / // % **` | `/` 得浮点，`//` 地板除，`%` 取余，`**` 幂 |
| 比较 | `== != > >= < <=` | 结果是 `bool` |
| 逻辑 | `and or not` | 短路求值 |
| 成员 | `in` / `not in` | 字符串、列表、字典都用得上 |
| 身份 | `is` / `is not` | 比的是**是不是同一个对象**，不是值相等 |
| 赋值 | `= += -= *= /= %=` | `x += 1` 等价 `x = x + 1` |

```python
print("abc" * 3)          # abcabcabc
print(6 ** 2)             # 36
print(7 % 2)              # 1
print("Hello" in "Hello World")   # True
print(3 in [1, 2, 3])             # True

a = [1, 2, 3]
b = a
c = [1, 2, 3]
print(a is b, a == c)     # True True
print(a is c)             # False  值相同但不是同一个对象
```

::: tip `==` 与 `is` 的分工
判断「值一样」用 `==`；判断「是不是同一个对象」用 `is`。日常只有和 `None` 比较时才惯用 `is None`。
:::

## 7. 标识符与命名

- 由字母、数字、下划线组成，不能数字开头；
- 区分大小写；不能与关键字重名（`if`、`for`、`class`…）；
- 约定：变量/函数 `snake_case`，类 `PascalCase`，常量 `UPPER_CASE`；
- 别用 `list`、`dict`、`str` 这种内置名当变量名，会把内置函数遮住。

## 8. 本章实操

`labs/ch01-basics/`：

```powershell
python labs/ch01-basics/basics.py        # 跑一遍基础语法 demo
python -m pytest labs/ch01-basics -q     # 跑测试
```

包含：类型转换的边界（`int("3.5")` 会炸）、`==`/`is` 的区别、f-string 格式化、一个把秒数转成 `1h02m03s` 的小函数。

## 9. 自测

1. `int("3.5")` 会怎样？该怎么写才对？
2. `bool("False")` 为什么是 `True`？
3. `a = [1,2]; b = a; b.append(3)` 之后 `a` 是什么？为什么？
4. 用一行 f-string 输出 `姓名: 李明 | 年龄: 18`。

## 附：自测答案

1. `int("3.5")` 抛 `ValueError`，因为 `int()` 只认整数字面量。要转就写 `int(float("3.5"))`，但更稳的是先判断字符串是不是整数形态，别让脏数据把用例炸掉。
2. `bool("False")` 是 `True`——`bool()` 只看「空不空」，非空字符串一律为真。要判断真假语义，比较字符串本身：`text.strip().lower() in ("true", "1", "yes")`。
3. `a` 会变成 `[1, 2, 3]`。`b = a` 只是把同一个列表对象多挂一个名字，`append` 原地修改，所以两边都变。要各改各的，用 `b = a[:]` 或 `list(a)`。
4. `print(f"姓名: {name} | 年龄: {age}")`。

## 学生常问

**Q：`print(a, b)` 中间的空格能去掉吗？**

A：能。`print` 的 `sep` 默认是一个空格，`print(a, b, sep="")` 就不带空格；行尾换行由 `end` 控制，`end=""` 表示不换行。

**Q：Python 变量要不要先声明类型？**

A：不用，赋值即创建。但「不用声明」不等于「没有类型」：`type(x)` 随时能查，写类型标注（`def f(x: int) -> str`）只是给人看和给编辑器看，运行时不强制。

**Q：读文件报 `UnicodeDecodeError` 怎么办？**

A：先把编码说清楚，`open(path, encoding="utf-8")`。Windows 上老文件可能是 GBK，实在不确定就用 `errors="replace"` 先看内容再决定，别直接忽略。

## 面试题

**Q：Python 里哪些类型可变、哪些不可变？这有什么实际影响？**

A：`list`、`dict`、`set` 可变；`int`、`str`、`tuple`、`frozenset` 不可变。影响有三处：可变对象不能当字典键；函数默认参数写成 `[]` 会被所有调用共享；多线程共享可变对象要加锁。

**Q：`is` 和 `==` 有什么区别？**

A：`==` 比值（调用 `__eq__`），`is` 比身份（是不是同一个对象）。判断 `None` 用 `is None`；比较数值和字符串用 `==`。小整数和短字符串有驻留机制，`is` 偶尔「看起来对」，但那是实现细节，不能依赖。

**Q：为什么说 `a = b` 不是复制？**

A：它是给同一个对象再绑一个名字，`id(a) == id(b)`。要复制得显式：切片 `a[:]`、`list(a)`、`dict(a)`，或者 `copy.copy` / `copy.deepcopy`。

## 延伸知识

- 编码：源文件、终端、文件读写三处编码要一致，团队统一 UTF-8；Windows 控制台是 GBK，打印中文乱码通常是终端的问题，不是代码的问题。
- 命名：变量和函数 `snake_case`、类 `PascalCase`、常量 `UPPER_CASE`；不要用 `list`、`dict`、`str`、`id` 当变量名，会把内置函数盖掉。
- 数字边界：`0.1 + 0.2 != 0.3`，金额一律用 `Decimal` 或整数分；`float` 只用于度量值。
- 字符串：`f"{x:.2f}"` 保留两位、`f"{x:,}"` 千分位、`f"{x:>8}"` 右对齐；格式化写进 f-string，别用 `%` 和 `format` 混着来。
