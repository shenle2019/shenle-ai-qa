"""第 5 章实验：类、继承与装饰器。"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable


class Counter:
    """演示实例属性与类属性的区别。"""

    total = 0

    def __init__(self, name: str = "c"):
        self.name = name
        self.count = 0
        Counter.total += 1

    def hit(self) -> int:
        self.count += 1
        return self.count

    @classmethod
    def reset_total(cls) -> None:
        cls.total = 0

    @staticmethod
    def valid_name(name: str) -> bool:
        return bool(name) and name.isascii() and name.isidentifier()


class Temperature:
    """@property + setter 校验。"""

    def __init__(self, celsius: float):
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("低于绝对零度")
        self._celsius = float(value)

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32


class Playlist:
    """魔术方法：len / 下标 / 迭代 / 相等 / 可读表示。"""

    def __init__(self, songs: list[str]):
        self._songs = list(songs)

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, index: int) -> str:
        return self._songs[index]

    def __iter__(self):
        return iter(self._songs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Playlist):
            return NotImplemented
        return self._songs == other._songs

    def __repr__(self) -> str:
        return f"Playlist({self._songs!r})"

    def __str__(self) -> str:
        return f"歌单（{len(self._songs)} 首）"


class Base:
    def describe(self) -> str:
        return "base"


class Child(Base):
    """super() 按 MRO 调父类实现。"""

    def describe(self) -> str:
        return super().describe() + "+child"


class Tagged(Base):
    def __init__(self, tag: str):
        super().__init__()
        self.tag = tag


def timing(fn: Callable) -> Callable:
    """不带参数的装饰器：记录耗时，返回原结果。"""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            wrapper.elapsed = time.perf_counter() - start

    wrapper.elapsed = 0.0  # type: ignore[attr-defined]
    return wrapper


def retry(times: int) -> Callable:
    """带参数的装饰器：失败重试，最后一次仍失败就抛出。"""
    if times < 1:
        raise ValueError("times 至少为 1")

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last: Exception | None = None
            for attempt in range(1, times + 1):
                wrapper.attempts = attempt  # type: ignore[attr-defined]
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last = exc
            assert last is not None
            raise last

        wrapper.attempts = 0  # type: ignore[attr-defined]
        return wrapper

    return decorator


def memoize(fn: Callable) -> Callable:
    """用字典缓存结果；被装饰函数的参数必须可哈希。"""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    wrapper.cache = cache  # type: ignore[attr-defined]
    return wrapper


@memoize
def slow_square(n: int) -> int:
    time.sleep(0.001)
    return n * n


if __name__ == "__main__":
    Counter.reset_total()
    a, b = Counter("a"), Counter("b")
    a.hit()
    a.hit()
    b.hit()
    print("实例 count:", a.count, b.count, "类 total:", Counter.total)
    print("合法标识符:", Counter.valid_name("abc_1"), Counter.valid_name("1abc"))

    t = Temperature(25)
    print("摄氏度/华氏度:", t.celsius, t.fahrenheit)
    try:
        t.celsius = -300
    except ValueError as exc:
        print("校验生效:", exc)

    pl = Playlist(["a", "b"])
    print("len / 下标 / 迭代 / 相等:", len(pl), pl[0], list(pl), pl == Playlist(["a", "b"]))
    print("str / repr:", str(pl), repr(pl))

    print("继承链:", Child().describe(), Tagged("x").describe(), Tagged("x").tag)

    @timing
    def work() -> int:
        time.sleep(0.002)
        return 42

    print("计时装饰器:", work(), f"{work.elapsed:.4f}s", work.__name__)

    calls = {"n": 0}

    @retry(3)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    print("retry:", flaky(), "尝试次数:", flaky.attempts)

    print("memoize:", slow_square(9), slow_square(9), "缓存条目:", len(slow_square.cache))
