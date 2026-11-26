from ch48_cases import (  # noqa: F401
    cold_start,
    degrade_curve,
    one_request,
    simulate_load,
)

from llm_sim import FakeLLM, stream_tokens


def test_ttft_equals_configured_latency():
    llm = FakeLLM(latency_ms=120, tpot_ms=18)
    r = one_request(llm, "总结一下", max_tokens=10)
    assert r["ttft"] == 120


def test_total_is_ttft_plus_tpot_times_gaps():
    llm = FakeLLM(latency_ms=100, tpot_ms=20)
    r = one_request(llm, "总结一下", max_tokens=6)
    assert r["total"] == 100 + 20 * (r["tokens"] - 1)


def test_stream_tokens_timeline_matches_ttft():
    llm = FakeLLM(latency_ms=100, tpot_ms=20)
    reply = llm.answer("总结一下", max_tokens=5)
    timeline = stream_tokens(reply)
    assert timeline[0][0] == 100
    assert timeline[-1][0] == 100 + 20 * (len(timeline) - 1)


def test_more_tokens_means_longer_total():
    llm = FakeLLM(latency_ms=100, tpot_ms=20)
    short = one_request(llm, "总结一下", max_tokens=4)
    long = one_request(llm, "总结一下", max_tokens=16)
    assert long["total"] > short["total"]


def test_concurrency_below_capacity_has_no_queueing():
    load = simulate_load(n=4, capacity=4)
    assert load.avg == load.p95


def test_queueing_appears_when_concurrency_exceeds_capacity():
    load = simulate_load(n=12, capacity=4)
    assert load.p95 > load.avg


def test_high_concurrency_breaks_timeout():
    # QPS 上去了，但由于排队，成功率掉了：这正是「不能只看 QPS」的证据
    heavy = simulate_load(n=16, capacity=4, timeout_ms=800)
    light = simulate_load(n=4, capacity=4, timeout_ms=800)
    assert heavy.rate < light.rate


def test_degrade_curve_is_monotonic():
    curve = degrade_curve([500, 4000, 32000])
    assert curve[0][1] < curve[1][1] < curve[2][1]


def test_cold_start_penalty_is_visible():
    c = cold_start(first=950, warm=130)
    assert c["penalty"] == 820


def test_cost_grows_with_tokens():
    from eval_sim import tokens_cost

    cheap = tokens_cost(1000, 200)
    pricey = tokens_cost(4000, 800)
    assert pricey > cheap
