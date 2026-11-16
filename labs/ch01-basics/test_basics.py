from basics import format_duration, precedence_demo, same_object, summary, to_int

import pytest


def test_to_int_accepts_plain_int():
    assert to_int("56") == 56


def test_to_int_truncates_float_string():
    assert to_int("3.5") == 3


def test_to_int_rejects_garbage():
    with pytest.raises(ValueError):
        to_int("abc")


def test_format_duration_with_hours():
    assert format_duration(3723) == "1h02m03s"


def test_format_duration_without_hours():
    assert format_duration(83) == "1m23s"


def test_format_duration_rejects_negative():
    with pytest.raises(ValueError):
        format_duration(-1)


def test_same_object_vs_equal():
    a = [1, 2, 3]
    b = a
    c = [1, 2, 3]
    assert same_object(a, b) is True
    assert same_object(a, c) is False
    assert a == c


def test_precedence():
    assert precedence_demo() == [14, 20]


def test_summary_layout():
    assert summary("李明", 18) == "姓名: 李明 | 年龄: 18"


def test_bool_of_non_empty_string():
    assert bool("False") is True
    assert bool("") is False
