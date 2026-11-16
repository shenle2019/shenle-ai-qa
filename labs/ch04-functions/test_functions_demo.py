import pytest
from functions_demo import (
    apply,
    buggy_append,
    collect_args,
    even_squares,
    even_squares_functional,
    factorial,
    flatten,
    make_accumulator,
    make_counter,
    safer_append,
    shallow_vs_deep,
    shared_or_copied,
    sort_multi,
    sort_rows,
)

ROWS = [
    {"name": "李四", "score": 88},
    {"name": "张三", "score": 92},
    {"name": "王五", "score": 88},
]


def test_collect_args():
    args, kwargs = collect_args(1, 2, c=3, d=4)
    assert args == (1, 2)
    assert kwargs == {"c": 3, "d": 4}


def test_safer_append_does_not_leak_between_calls():
    assert safer_append("a") == ["a"]
    assert safer_append("b") == ["b"]


def test_buggy_append_shares_the_default_list():
    # 反例演示：两次调用拿到的是同一个 list，长度会累加
    buggy_append.__defaults__[0].clear()
    first = buggy_append("a")
    second = buggy_append("b")
    assert first is second
    assert second == ["a", "b"]
    buggy_append.__defaults__[0].clear()


def test_make_counter_is_independent():
    a = make_counter()
    b = make_counter(100)
    assert [a(), a()] == [1, 2]
    assert b() == 101


def test_make_accumulator_remembers_calls():
    acc = make_accumulator(10)
    assert acc(0) == 10
    assert acc(0) == 20
    assert acc(5) == 35


def test_apply_takes_function_as_argument():
    assert apply(str.upper, "abc") == "ABC"
    assert apply(lambda s: s[::-1], "abc") == "cba"


def test_sort_rows_does_not_mutate_input():
    original = list(ROWS)
    sorted_rows = sort_rows(ROWS, "score")
    assert ROWS == original
    assert [r["score"] for r in sorted_rows] == [92, 88, 88]


def test_sort_multi_score_desc_name_asc():
    assert [r["name"] for r in sort_multi(ROWS)] == ["张三", "李四", "王五"]


def test_factorial():
    assert factorial(0) == 1
    assert factorial(5) == 120
    with pytest.raises(ValueError):
        factorial(-1)


def test_flatten_nested_structures():
    assert flatten([1, [2, [3, [4]]], (5, 6)]) == [1, 2, 3, 4, 5, 6]


def test_shallow_copy_leaks_deep_copy_does_not():
    assert shallow_vs_deep([[1], [2]]) == (True, False)


def test_assignment_shares_slice_copies():
    assert shared_or_copied() == (True, False)


def test_comprehension_matches_functional_version():
    assert even_squares(10) == even_squares_functional(10) == [0, 4, 16, 36, 64]
