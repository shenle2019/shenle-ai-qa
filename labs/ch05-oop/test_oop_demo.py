import pytest
from oop_demo import (
    Base,
    Child,
    Counter,
    Playlist,
    Tagged,
    Temperature,
    memoize,
    retry,
    timing,
)


def setup_function():
    Counter.reset_total()


def test_class_attribute_counts_instances():
    a, b = Counter("a"), Counter("b")
    assert Counter.total == 2
    assert a.count == 0 and b.count == 0


def test_instance_counter_is_independent():
    a, b = Counter("a"), Counter("b")
    assert a.hit() == 1
    assert a.hit() == 2
    assert b.hit() == 1
    assert Counter.total == 2


def test_classmethod_and_staticmethod():
    assert Counter.valid_name("abc_1") is True
    assert Counter.valid_name("1abc") is False
    assert Counter.valid_name("张三") is False


def test_property_reads_and_validates():
    t = Temperature(25)
    assert t.fahrenheit == pytest.approx(77.0)
    t.celsius = 0
    assert t.fahrenheit == pytest.approx(32.0)
    with pytest.raises(ValueError):
        t.celsius = -300


def test_magic_methods():
    pl = Playlist(["a", "b"])
    assert len(pl) == 2
    assert pl[1] == "b"
    assert list(pl) == ["a", "b"]
    assert pl == Playlist(["a", "b"])
    assert pl != Playlist(["a"])
    assert "2 首" in str(pl)
    assert repr(pl).startswith("Playlist(")


def test_inheritance_uses_super():
    assert Child().describe() == "base+child"
    tagged = Tagged("x")
    assert tagged.describe() == "base"
    assert tagged.tag == "x"


def test_timing_wrapper_keeps_metadata_and_passes_result():
    @timing
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert add.__name__ == "add"
    assert add.elapsed >= 0


def test_retry_succeeds_after_failures():
    state = {"n": 0}

    @retry(3)
    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert flaky() == "ok"
    assert flaky.attempts == 3


def test_retry_raises_after_exhausting():
    @retry(2)
    def always():
        raise RuntimeError("always")

    with pytest.raises(RuntimeError, match="always"):
        always()


def test_retry_rejects_bad_times():
    with pytest.raises(ValueError):
        retry(0)


def test_memoize_caches_results():
    calls = {"n": 0}

    @memoize
    def square(n):
        calls["n"] += 1
        return n * n

    assert square(4) == 16
    assert square(4) == 16
    assert calls["n"] == 1
    assert square.cache[(4,)] == 16


def test_base_can_be_instantiated():
    assert Base().describe() == "base"
