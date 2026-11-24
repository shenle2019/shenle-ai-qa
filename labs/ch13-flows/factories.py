"""造数工厂：唯一、可复用、失败可清理。"""

from __future__ import annotations

import itertools
import random
import string

_counter = itertools.count(1)
_rand = random.Random(20261116)


def unique_name(prefix: str = "qa") -> str:
    return f"{prefix}_{next(_counter):04d}"


def unique_phone(seed: int | None = None) -> str:
    n = seed if seed is not None else next(_counter)
    return "13" + f"{n % 10**9:09d}"


def unique_order_no() -> str:
    tail = "".join(_rand.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD{next(_counter):04d}{tail}"


def make_user(client, name: str | None = None, role: str = "tester") -> dict:
    payload = {"name": name or unique_name("user"), "role": role}
    return client.post("/api/users", json=payload).json()


def make_order(client, items: list[dict] | None = None, idem: str | None = None) -> dict:
    headers = {"Idempotency-Key": idem} if idem else {}
    payload = {"items": items or [{"sku": "A-1", "qty": 1}]}
    return client.post("/api/orders", json=payload, headers=headers).json()
