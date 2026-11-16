"""第 3 章实验：列表、元组、字典与推导式。"""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    """去重且保留首次出现的顺序（不能直接用 set，set 无序）。"""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def word_count(text: str) -> dict[str, int]:
    """词频统计：按空白切分，忽略大小写。"""
    words = [w.strip(".,!?;:").lower() for w in text.split()]
    return dict(Counter(w for w in words if w))


def invert(mapping: dict[str, int]) -> dict[int, str]:
    """反转字典。值有重复时后者覆盖前者——调用方要自己保证唯一。"""
    return {v: k for k, v in mapping.items()}


def total_qty(orders: list[dict]) -> int:
    """嵌套结构求和：列表 → 字典 → 列表 → 字典。"""
    return sum(item["qty"] for order in orders for item in order.get("items", []))


def paid_skus(orders: list[dict]) -> list[str]:
    """所有已支付订单里的 SKU。"""
    return [
        item["sku"]
        for order in orders
        if order.get("status") == "paid"
        for item in order.get("items", [])
    ]


def chunk(items: list, size: int) -> list[list]:
    """按固定长度切片。"""
    if size < 1:
        raise ValueError("size 至少为 1")
    return [items[i : i + size] for i in range(0, len(items), size)]


def slice_is_shallow(matrix: list[list[int]]) -> bool:
    """验证切片是浅拷贝：改副本里的内层列表，原数据也会变。"""
    copy = matrix[:]
    copy[0].append(99)
    return matrix[0][-1] == 99


if __name__ == "__main__":
    print("去重:", dedupe_keep_order(["b", "a", "b", "c", "a"]))
    print("词频:", word_count("the cat and the dog, The end"))
    print("反转:", invert({"a": 1, "b": 2}))
    orders = [
        {"id": 1, "status": "paid", "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}]},
        {"id": 2, "status": "cancelled", "items": [{"sku": "C", "qty": 5}]},
        {"id": 3, "status": "paid", "items": [{"sku": "D", "qty": 3}]},
    ]
    print("总件数:", total_qty(orders), "已支付 SKU:", paid_skus(orders))
    print("分块:", chunk([1, 2, 3, 4, 5], 2))
    print("切片浅拷贝会互相影响:", slice_is_shallow([[1], [2]]))
