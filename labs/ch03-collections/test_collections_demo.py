import pytest
from collections_demo import (
    chunk,
    dedupe_keep_order,
    invert,
    paid_skus,
    slice_is_shallow,
    total_qty,
    word_count,
)

ORDERS = [
    {"id": 1, "status": "paid", "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}]},
    {"id": 2, "status": "cancelled", "items": [{"sku": "C", "qty": 5}]},
    {"id": 3, "status": "paid", "items": [{"sku": "D", "qty": 3}]},
]


def test_dedupe_keeps_first_order():
    assert dedupe_keep_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]


def test_word_count_ignores_case_and_punctuation():
    assert word_count("the cat and the dog, The end") == {
        "the": 3,
        "cat": 1,
        "and": 1,
        "dog": 1,
        "end": 1,
    }


def test_word_count_skips_empty_tokens():
    assert word_count("  ") == {}


def test_invert():
    assert invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}


def test_invert_last_wins_on_duplicate_values():
    assert invert({"a": 1, "b": 1}) == {1: "b"}


def test_total_qty_walks_nested_lists():
    assert total_qty(ORDERS) == 11


def test_total_qty_handles_missing_items():
    assert total_qty([{"id": 9}]) == 0


def test_paid_skus_only_paid_orders():
    assert paid_skus(ORDERS) == ["A", "B", "D"]


def test_chunk_even_and_uneven():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([], 3) == []


def test_chunk_rejects_bad_size():
    with pytest.raises(ValueError):
        chunk([1], 0)


def test_slice_is_shallow():
    assert slice_is_shallow([[1], [2]]) is True


def test_tuple_unpack_and_single_element():
    point = (3, 4)
    x, y = point
    assert (x, y) == (3, 4)
    assert isinstance((5,), tuple)
    assert not isinstance((5), tuple)
