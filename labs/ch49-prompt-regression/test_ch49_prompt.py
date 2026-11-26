from ch49_cases import (  # noqa: F401
    TEMPLATE,
    PromptVersion,
    ab_assign,
    bucket,
    pass_rate,
    regression,
    render,
    stability,
)

from llm_sim import FakeLLM


def test_render_substitutes_all_placeholders():
    out = render(TEMPLATE, role="客服", question="怎么退款", rule="只答流程")
    assert "{question}" not in out
    assert "怎么退款" in out


def test_render_reports_missing_variable():
    try:
        render(TEMPLATE, role="客服")
    except KeyError as exc:
        assert "question" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("缺变量必须报错")


def test_clear_prompt_is_not_worse_than_vague():
    llm = FakeLLM()
    clear = pass_rate(llm, [("请用三句话说明退款流程，并列出需要的材料。", "退款")])
    vague = pass_rate(llm, [("退款", "退款")])
    assert clear >= vague


def test_stability_is_one_when_jitter_off():
    assert stability(FakeLLM(), "我要退款") == 1.0


def test_stability_drops_with_jitter():
    assert stability(FakeLLM(jitter=0.9), "我要退款", rounds=10) < 1.0


def test_bucket_is_stable_for_same_user():
    assert bucket("user-42") == bucket("user-42")


def test_bucket_spreads_users_across_buckets():
    counts = ab_assign([f"user-{i}" for i in range(200)])
    assert set(counts) == {0, 1}
    assert all(60 <= c <= 140 for c in counts.values())


def test_regression_separates_broke_and_fixed():
    r = regression({"a": True, "b": True, "c": False}, {"a": True, "b": False, "c": True})
    assert r["broke"] == ["b"]
    assert r["fixed"] == ["c"]
    assert r["passed"] == ["a"]


def test_version_switch_changes_pass_rate():
    old = PromptVersion("v1", "退款")
    new = PromptVersion("v2", "请说明退款流程与所需材料")
    llm = FakeLLM()
    assert pass_rate(llm, [(old.body, "退款")]) >= 0.0
    assert pass_rate(llm, [(new.body, "退款")]) == 1.0
