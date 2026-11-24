from pathlib import Path

import pytest
from testkit import (
    DataGen,
    ValidationError,
    dump_csv,
    dump_json,
    is_email,
    is_id_card,
    is_money,
    is_phone,
    load_json,
    require,
    unique_email,
    unique_order_no,
    unique_phone,
)
from testkit.validators import ValidationError as DirectValidationError


def test_validation_error_is_exported():
    assert DirectValidationError is ValidationError


@pytest.mark.parametrize(
    "value,expected",
    [("13800138000", True), ("19912345678", True), ("12345678901", False), ("1380013800", False)],
)
def test_is_phone(value, expected):
    assert is_phone(value) is expected


def test_is_email():
    assert is_email("qa.abc123@example.com") is True
    assert is_email("no-at-sign") is False
    assert is_email("a@b") is False


def test_is_id_card():
    assert is_id_card("110101199003071234") is True
    assert is_id_card("11010119900307123X") is True
    assert is_id_card("11010119900307123") is False


def test_is_money():
    assert is_money("12.34") is True
    assert is_money("12") is True
    assert is_money("12.345") is False
    assert is_money(-1) is False
    assert is_money(True) is False


def test_require_raises_with_field_name():
    with pytest.raises(ValidationError) as info:
        require("phone", "123", is_phone)
    assert info.value.field == "phone"
    assert "不合法" in str(info.value)


def test_unique_phone_and_email():
    phones = {unique_phone() for _ in range(50)}
    assert len(phones) == 50
    assert all(is_phone(p) for p in phones)

    email = unique_email("case")
    assert email.startswith("case.")
    assert is_email(email)


def test_unique_order_no_has_date_and_prefix():
    order_no = unique_order_no("PO")
    assert order_no.startswith("PO")
    assert len(order_no) == 2 + 8 + 6


def test_datagen_is_reproducible_with_same_seed():
    a = DataGen(seed=7).orders(3)
    b = DataGen(seed=7).orders(3)
    assert [o["customer"] for o in a] == [o["customer"] for o in b]
    assert [o["qty"] for o in a] == [o["qty"] for o in b]


def test_datagen_phones_and_emails_are_unique_inside_one_instance():
    gen = DataGen()
    rows = gen.orders(20)
    assert len({r["phone"] for r in rows}) == 20
    assert len({r["email"] for r in rows}) == 20


def test_datagen_orders_shape():
    row = DataGen().order("SKU-9", qty=3)
    assert set(row) == {"order_no", "customer", "phone", "email", "sku", "qty", "amount"}
    assert row["sku"] == "SKU-9"
    assert row["qty"] == 3
    assert is_money(f"{row['amount']:.2f}")


def test_datagen_rejects_negative_count():
    with pytest.raises(ValueError):
        DataGen().orders(-1)


def test_dump_and_load_json(tmp_path):
    path = dump_json(tmp_path / "out" / "orders.json", DataGen().orders(2))
    payload = load_json(path)
    assert isinstance(payload, list) and len(payload) == 2
    assert "customer" in payload[0]


def test_dump_json_handles_dates(tmp_path):
    from datetime import date

    path = dump_json(tmp_path / "d.json", {"day": date(2026, 11, 16)})
    assert load_json(path) == {"day": "2026-11-16"}


def test_dump_csv_writes_header_and_rows(tmp_path):
    path = dump_csv(tmp_path / "orders.csv", [{"id": 1, "name": "甲"}])
    text = Path(path).read_text(encoding="utf-8-sig")
    assert text.splitlines()[0] == "id,name"
    assert "甲" in text


def test_dump_csv_rejects_empty(tmp_path):
    with pytest.raises(ValueError):
        dump_csv(tmp_path / "x.csv", [])


def test_fixture_files_can_be_reused_by_cases(tmp_path):
    """模拟真实用法：一次生成，多个用例读取同一份数据。"""
    gen = DataGen(seed=1)
    path = dump_json(tmp_path / "orders.json", gen.orders(3))

    first = load_json(path)
    second = load_json(path)
    assert first == second
    assert {row["sku"] for row in first} == {"SKU-1", "SKU-2", "SKU-3"}

def test_is_phone_rejects_trailing_newline():
    # `$` 会放过末尾一个换行，validators 改用 fullmatch 才挡得住
    assert is_phone('13800138000\n') is False
    assert is_phone('13800138000') is True
