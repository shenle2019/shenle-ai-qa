"""第 2 章实验：条件、循环与函数。"""

from __future__ import annotations

from typing import Callable, Iterable


def grade_of(score: float) -> str:
    """分数转等级。边界值：90 / 80 / 60。

    注意判断顺序：从高到低，先命中的先返回，
    否则 95 分会在 score >= 60 处被判成 C。
    """
    if not 0 <= score <= 100:
        raise ValueError(f"分数必须在 0-100 之间，收到 {score}")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def multiplication_table(n: int = 9) -> list[str]:
    """生成九九乘法表的每一行（不含表头）。"""
    if n < 1:
        raise ValueError("n 至少为 1")
    rows = []
    for i in range(1, n + 1):
        cells = [f"{j}x{i}={i * j}" for j in range(1, i + 1)]
        rows.append("\t".join(cells))
    return rows


def find_first_even(nums: Iterable[int]) -> int | None:
    """用 return 在找到时立刻结束函数。"""
    for n in nums:
        if n % 2 == 0:
            return n
    return None


def first_pair_sum_over(nums: Iterable[int], limit: int) -> tuple[int, int] | None:
    """两数之和第一个超过 limit 的组合。

    嵌套循环里想「一次跳出两层」，break 做不到，
    这里把内层判断抽成函数，用 return 直接返回。
    """
    values = list(nums)
    for i, a in enumerate(values):
        for b in values[i + 1 :]:
            if a + b > limit:
                return a, b
    return None


def retry(times: int, fn: Callable[[], object]) -> object:
    """失败重试：最后一次仍失败就把异常抛出去。"""
    if times < 1:
        raise ValueError("重试次数至少为 1")
    last: Exception | None = None
    for attempt in range(1, times + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - 这里就是要兜住所有失败
            last = exc
            print(f"第 {attempt} 次失败：{exc}")
    assert last is not None
    raise last


def is_prime(n: int) -> bool:
    """用 for...else 判断质数。"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            break
    else:
        return True
    return False


if __name__ == "__main__":
    for s in (95, 85, 72, 59):
        print(s, "->", grade_of(s))
    print()
    print("\n".join(multiplication_table(5)))
    print()
    print("第一个偶数:", find_first_even([1, 3, 4, 6]))
    print("两数和超过 10:", first_pair_sum_over([1, 4, 7, 9], 10))
    print("质数判断 97 / 91:", is_prime(97), is_prime(91))

    state = {"n": 0}

    def flaky() -> str:
        state["n"] += 1
        if state["n"] < 3:
            raise RuntimeError(f"模拟第 {state['n']} 次失败")
        return "ok"

    print("retry 结果:", retry(3, flaky))
