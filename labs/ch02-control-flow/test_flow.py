import pytest
from flow import (
    find_first_even,
    first_pair_sum_over,
    grade_of,
    is_prime,
    multiplication_table,
    retry,
)


def test_grade_boundaries():
    assert grade_of(100) == "A"
    assert grade_of(90) == "A"
    assert grade_of(89.9) == "B"
    assert grade_of(80) == "B"
    assert grade_of(79.9) == "C"
    assert grade_of(60) == "C"
    assert grade_of(59.9) == "D"
    assert grade_of(0) == "D"


def test_grade_rejects_out_of_range():
    with pytest.raises(ValueError):
        grade_of(-1)
    with pytest.raises(ValueError):
        grade_of(101)


def test_multiplication_table_shape():
    rows = multiplication_table(3)
    assert rows == ["1x1=1", "1x2=2\t2x2=4", "1x3=3\t2x3=6\t3x3=9"]


def test_multiplication_table_rejects_zero():
    with pytest.raises(ValueError):
        multiplication_table(0)


def test_find_first_even():
    assert find_first_even([1, 3, 4, 6]) == 4
    assert find_first_even([1, 3, 5]) is None


def test_first_pair_sum_over():
    assert first_pair_sum_over([1, 4, 7, 9], 10) == (4, 7)
    assert first_pair_sum_over([1, 2], 100) is None


def test_retry_succeeds_after_failures():
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert retry(3, flaky) == "ok"
    assert calls["n"] == 3


def test_retry_raises_last_error():
    def always_fail() -> str:
        raise RuntimeError("always")

    with pytest.raises(RuntimeError, match="always"):
        retry(2, always_fail)


def test_retry_rejects_zero_times():
    with pytest.raises(ValueError):
        retry(0, lambda: "x")


def test_is_prime():
    assert is_prime(2) is True
    assert is_prime(97) is True
    assert is_prime(91) is False
    assert is_prime(1) is False
