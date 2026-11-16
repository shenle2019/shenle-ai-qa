"""测试数据生成：保证同一次运行里不重复。"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime

SURNAMES = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨"
GIVEN = "伟芳娜敏静秀丽强磊洋艳勇军杰娟涛明超秀霞平刚桂英"


def _digits(n: int, rng: random.Random) -> str:
    return "".join(rng.choice("0123456789") for _ in range(n))


def unique_phone(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    return f"1{rng.choice('3456789')}{_digits(9, rng)}"


def unique_email(prefix: str = "qa", rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    return f"{prefix}.{uuid.uuid4().hex[:8]}@example.com"


def unique_order_no(prefix: str = "SO") -> str:
    """业务单号：前缀 + 日期 + 6 位随机，天然按天分段。"""
    return f"{prefix}{datetime.now():%Y%m%d}{uuid.uuid4().hex[:6].upper()}"


def random_name(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    return rng.choice(SURNAMES) + "".join(rng.choice(GIVEN) for _ in range(rng.choice((1, 2))))


@dataclass
class DataGen:
    """带种子生成器：同一种子 → 同一批数据，便于复现失败用例。"""

    seed: int = 20261116
    _used_phones: set[str] = field(default_factory=set, init=False)
    _used_emails: set[str] = field(default_factory=set, init=False)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def phone(self) -> str:
        for _ in range(1000):
            value = unique_phone(self._rng)
            if value not in self._used_phones:
                self._used_phones.add(value)
                return value
        raise RuntimeError("手机号耗尽（不该发生）")

    def email(self, prefix: str = "qa") -> str:
        while True:
            value = unique_email(prefix, self._rng)
            if value not in self._used_emails:
                self._used_emails.add(value)
                return value

    def name(self) -> str:
        return random_name(self._rng)

    def order(self, sku: str = "SKU-1", qty: int | None = None) -> dict:
        return {
            "order_no": unique_order_no(),
            "customer": self.name(),
            "phone": self.phone(),
            "email": self.email(),
            "sku": sku,
            "qty": qty if qty is not None else self._rng.randint(1, 5),
            "amount": round(self._rng.uniform(9.9, 999.0), 2),
        }

    def orders(self, count: int = 5) -> list[dict]:
        if count < 0:
            raise ValueError("count 不能为负")
        return [self.order(sku=f"SKU-{i}") for i in range(1, count + 1)]
