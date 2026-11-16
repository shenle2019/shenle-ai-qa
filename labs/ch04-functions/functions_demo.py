"""第 4 章实验：参数、作用域、闭包与内存模型。"""

from __future__ import annotations

import copy
from typing import Callable, Iterable


def collect_args(*args, **kwargs) -> tuple[tuple, dict]:
    """把可变参数原样收集起来，便于观察形态。"""
    return args, kwargs


def safer_append(item: str, bucket: list[str] | None = None) -> list[str]:
    """用 None 做默认值，避免所有调用共享同一个 list。"""
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


def buggy_append(item: str, bucket: list[str] = []) -> list[str]:  # noqa: B006 - 故意的反例
    """反例：默认值只在定义时创建一次，多次调用会累积。"""
    bucket.append(item)
    return bucket


def make_counter(start: int = 0) -> Callable[[], int]:
    """闭包：内层函数记住外层的 n，并用 nonlocal 修改它。"""
    n = start

    def counter() -> int:
        nonlocal n
        n += 1
        return n

    return counter


def make_accumulator(step: int) -> Callable[[int], int]:
    """闭包 + 参数：每次调用把 step 加到传入值上，并记住累计次数。"""
    calls = 0

    def add(value: int) -> int:
        nonlocal calls
        calls += 1
        return value + step * calls

    return add


def apply(fn: Callable[[str], str], value: str) -> str:
    """函数当参数传：验证「函数是一等公民」。"""
    return fn(value)


def sort_rows(rows: list[dict], key: str, reverse: bool = True) -> list[dict]:
    """按某个字段排序，不修改入参。"""
    return sorted(rows, key=lambda r: r[key], reverse=reverse)


def sort_multi(rows: list[dict]) -> list[dict]:
    """分数降序、姓名升序：用元组做排序键。"""
    return sorted(rows, key=lambda r: (-r["score"], r["name"]))


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("n 不能为负")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def flatten(nested: Iterable) -> list:
    """递归展平任意层嵌套（列表/元组）。"""
    result: list = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def shallow_vs_deep(matrix: list[list[int]]) -> tuple[bool, bool]:
    """返回 (浅拷贝会互相影响, 深拷贝不会互相影响)。"""
    shallow = matrix[:]
    shallow[0].append(99)
    shallow_affects = matrix[0][-1] == 99

    deep_source = [[1], [2]]
    deep = copy.deepcopy(deep_source)
    deep[0].append(99)
    deep_affects = deep_source[0][-1] == 99
    return shallow_affects, deep_affects


def shared_or_copied() -> tuple[bool, bool]:
    """赋值共享引用、切片创建新列表。"""
    original = [1, 2]
    alias = original
    slice_copy = original[:]
    return alias is original, slice_copy is original


def even_squares(limit: int) -> list[int]:
    """推导式 vs map/filter：同一件事的两种写法。"""
    return [x * x for x in range(limit) if x % 2 == 0]


def even_squares_functional(limit: int) -> list[int]:
    return list(map(lambda x: x * x, filter(lambda x: x % 2 == 0, range(limit))))


if __name__ == "__main__":
    print("args/kwargs:", collect_args(1, 2, c=3))
    print("safer_append 两次:", safer_append("a"), safer_append("b"))
    print("buggy_append 两次:", buggy_append("a"), buggy_append("b"))

    c = make_counter(10)
    print("闭包计数:", c(), c(), c())
    acc = make_accumulator(5)
    print("闭包累加:", acc(0), acc(0), acc(0))

    print("函数当参数:", apply(str.upper, "abc"))
    rows = [
        {"name": "李四", "score": 88},
        {"name": "张三", "score": 92},
        {"name": "王五", "score": 88},
    ]
    print("按分数降序:", [r["name"] for r in sort_rows(rows, "score")])
    print("分数降序+姓名升序:", [(r["name"], r["score"]) for r in sort_multi(rows)])
    print("5! =", factorial(5))
    print("展平:", flatten([1, [2, [3, [4]]], (5, 6)]))
    print("浅/深拷贝:", shallow_vs_deep([[1], [2]]))
    print("赋值 vs 切片:", shared_or_copied())
    print("偶数平方:", even_squares(10) == even_squares_functional(10) == [0, 4, 16, 36, 64])
