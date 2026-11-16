# 第 5 章 · 面向对象与装饰器

> 本章目标：会用类组织状态与行为，看懂 `@property`、`@classmethod`、`@staticmethod` 的区别，并能写一个带参数的装饰器。

## 1. 类的基本格式

```python
class Order:
    def __init__(self, order_id: int, amount: float):
        self.order_id = order_id      # 实例属性
        self.amount = amount

    def is_big(self) -> bool:
        return self.amount >= 1000

o = Order(1, 1200)
o.is_big()      # True
```

- `__init__` 不是构造函数，只是「对象建好之后的初始化钩子」；
- `self` 就是实例本身，方法调用时 Python 自动传；
- 属性直接挂在 `self` 上，不需要提前声明。

## 2. 实例属性 vs 类属性

```python
class Counter:
    total = 0                     # 类属性：所有实例共享

    def __init__(self):
        self.count = 0            # 实例属性：每个实例独立
        Counter.total += 1
```

`self.count` 与 `Counter.total` 是两个东西。**坑**：`self.total += 1` 会创建实例属性遮蔽类属性，想改类属性要写 `Counter.total += 1` 或 `type(self).total += 1`。

## 3. 三种方法

```python
class User:
    domain = "example.com"

    def __init__(self, name: str):
        self.name = name

    def mail(self) -> str:                 # 实例方法：要 self
        return f"{self.name}@{self.domain}"

    @classmethod
    def from_email(cls, email: str):       # 类方法：要 cls，常做备用构造
        name = email.split("@")[0]
        return cls(name)

    @staticmethod
    def valid_name(name: str) -> bool:     # 静态方法：不碰 self / cls
        return bool(name) and name.isascii()
```

| 装饰器 | 第一个参数 | 典型用途 |
| --- | --- | --- |
| 无 | `self` | 读写实例状态 |
| `@classmethod` | `cls` | 备用构造函数、读类级配置 |
| `@staticmethod` | 无 | 纯工具函数，放类里只是归类 |

## 4. `@property`：把方法当属性用

```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("低于绝对零度")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32
```

好处：对外仍是 `t.celsius`，但读和写都能加校验，不用改成 `get_celsius()`。

## 5. 魔术方法

| 方法 | 触发时机 |
| --- | --- |
| `__str__` | `print(obj)`、`f"{obj}"` |
| `__repr__` | 交互式回显、调试输出 |
| `__eq__` | `==` |
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[i]` |
| `__iter__` | `for x in obj` |
| `__enter__` / `__exit__` | `with obj:` |

```python
class Playlist:
    def __init__(self, songs: list[str]):
        self._songs = songs

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, i):
        return self._songs[i]

    def __repr__(self) -> str:
        return f"Playlist({self._songs!r})"
```

经验：`__repr__` 给开发者看（尽量能重建对象），`__str__` 给用户看。

## 6. 继承与 super

```python
class Base:
    def greet(self) -> str:
        return "base"

class Child(Base):
    def greet(self) -> str:
        return super().greet() + " + child"
```

- `super()` 按 MRO（方法解析顺序）找下一个实现，多继承时尤其重要；
- 子类 `__init__` 里记得调 `super().__init__(...)`，否则父类状态没初始化；
- 组合（把对象当属性）通常比继承更灵活，先考虑组合。

## 7. 装饰器

装饰器就是「接收函数、返回函数」的高阶函数：

```python
import functools

def timing(fn):
    @functools.wraps(fn)                 # 保留 __name__ / __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} 耗时 {time.perf_counter() - start:.4f}s")
    return wrapper
```

带参数的装饰器要多包一层：

```python
def retry(times: int):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if i == times - 1:
                        raise
        return wrapper
    return decorator
```

`@functools.wraps` 一定要加，否则被装饰函数的 `__name__`、文档、类型标注都会变成 `wrapper`。

## 8. 本章实验

`labs/ch05-oop/`：

```powershell
python labs/ch05-oop/oop_demo.py
python -m pytest labs/ch05-oop -q
```

包含：实例/类属性对比、三种方法、`@property` 校验、`__eq__/__len__/__getitem__`、继承 + `super()`、计时装饰器与带参数的 retry 装饰器。

## 9. 自测

1. `self.x += 1` 与 `ClassName.x += 1` 的区别？
2. `@classmethod` 的第一个参数是什么，什么时候必须用它？
3. 为什么装饰器里要写 `@functools.wraps(fn)`？
4. `__str__` 和 `__repr__` 分别在什么时候被调用？
