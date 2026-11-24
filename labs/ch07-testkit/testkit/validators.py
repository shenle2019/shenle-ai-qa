"""校验函数：只做判断，不抛业务异常；需要报错时用 require。"""

from __future__ import annotations

import re

PHONE_RE = re.compile(r"1[3-9]\d{9}")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
ID_RE = re.compile(r"\d{17}[\dXx]")
MONEY_RE = re.compile(r"\d+(\.\d{1,2})?")


class ValidationError(ValueError):
    """校验失败。带字段名，方便在接口测试里直接断言。"""

    def __init__(self, field: str, value: object, reason: str):
        super().__init__(f"{field}={value!r} 不合法：{reason}")
        self.field = field
        self.value = value
        self.reason = reason


def is_phone(value: str) -> bool:
    return isinstance(value, str) and bool(PHONE_RE.fullmatch(value))


def is_email(value: str) -> bool:
    return isinstance(value, str) and bool(EMAIL_RE.fullmatch(value))


def is_id_card(value: str) -> bool:
    """18 位，前 17 位数字，末位数字或 X。"""
    return isinstance(value, str) and bool(ID_RE.fullmatch(value))


def is_money(value: str | int | float) -> bool:
    """最多两位小数、非负。浮点数会先转成字符串再判断。"""
    if isinstance(value, bool):
        return False
    return bool(MONEY_RE.fullmatch(str(value)))


def require(field: str, value: object, check) -> object:
    """把布尔校验升格成异常，返回原值便于链式调用。"""
    if not check(value):
        raise ValidationError(field, value, "格式不符合要求")
    return value
