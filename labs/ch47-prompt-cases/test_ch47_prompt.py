from ch47_cases import (  # noqa: F401
    Case,
    check,
    coverage,
    multiround,
    persona_drift,
    run,
    stable_ratio,
)

from llm_sim import FakeLLM


def test_fixed_seed_is_repeatable():
    llm = FakeLLM()
    assert run(llm, "我要退款") == run(llm, "我要退款")


def test_jitter_makes_answers_unstable():
    llm = FakeLLM(jitter=0.9)
    assert stable_ratio(llm, "我要退款", rounds=10) < 1.0


def test_no_jitter_is_fully_stable():
    llm = FakeLLM(jitter=0.0)
    assert stable_ratio(llm, "我要退款", rounds=10) == 1.0


def test_empty_input_does_not_crash():
    llm = FakeLLM()
    reply = llm.answer("")
    assert reply.text
    assert reply.used_prompt_tokens == 0


def test_long_input_truncates_and_flags():
    llm = FakeLLM(context_limit=20)
    reply = llm.answer("退款" * 40)
    assert reply.truncated is True
    assert reply.used_prompt_tokens <= 20


def test_silent_policy_hides_the_truncation():
    # 两种策略都截断，但留下的部分不同；调用方必须靠 truncated 字段判断，不能靠比对文本
    loud = FakeLLM(context_limit=20, overflow_policy="truncate_head")
    quiet = FakeLLM(context_limit=20, overflow_policy="silent")
    prompt = "头部标记" + "退款" * 40 + "尾部标记"
    head, head_cut = loud.fit_context(prompt)
    tail, tail_cut = quiet.fit_context(prompt)
    assert head_cut is True and tail_cut is True
    assert head.startswith("头部标记")
    assert tail.endswith("尾部标记")
    assert head != tail


def test_error_policy_raises():
    llm = FakeLLM(context_limit=10, overflow_policy="error")
    try:
        llm.answer("退款" * 20)
    except ValueError as exc:
        assert "上下文溢出" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("应当抛错")


def test_multiround_keeps_history():
    llm = FakeLLM(memory_turns=5)
    outs = multiround(llm, ["查一下订单", "那退款呢"])
    assert len(outs) == 2
    assert len(llm.history()) == 2


def test_memory_window_evicts_old_turns():
    llm = FakeLLM(memory_turns=1)
    multiround(llm, ["查一下订单", "那退款呢", "再查一次订单"])
    assert len(llm.history()) == 1


def test_coverage_counts_features():
    cases = [Case("a", "我要退款", "退款"), Case("b", "查订单", "订单")]
    counts = coverage(cases, ["退款", "订单", "优惠券"])
    assert counts["退款"] == 1
    assert counts["优惠券"] == 0


def test_persona_drift_is_detectable():
    llm = FakeLLM()
    # 假模型不会自称客服，所以「必须保持人设」的用例应当被判为漂移
    assert persona_drift(llm, "客服", ["我想退款"]) is True
