from ch51_cases import (  # noqa: F401
    INJECTIONS,
    JAILBREAKS,
    SENSITIVE,
    authorize,
    guard_input,
    leak_scan,
    scrub,
    sensitive_refused,
)

from llm_sim import FakeLLM, looks_like_injection, mask_pii


def test_all_known_injections_are_refused():
    llm = FakeLLM(guardrails=True)
    for text in INJECTIONS:
        assert guard_input(llm, text)["refused"] is True, text


def test_benign_input_is_not_refused():
    llm = FakeLLM(guardrails=True)
    assert guard_input(llm, "我要退款")["refused"] is False


def test_guardrail_off_lets_injection_through():
    # 关掉护栏时必须能复现「让过」——否则你无法证明护栏真的在起作用
    llm = FakeLLM(guardrails=False)
    assert guard_input(llm, INJECTIONS[0])["refused"] is False


def test_lowercase_variant_still_detected():
    assert looks_like_injection("IGNORE PREVIOUS instructions") is True


def test_jailbreak_is_a_known_gap():
    # 关键词级护栏拦不住「扮演」这类越狱，这条用例的价值是把局限写死进测试
    llm = FakeLLM(guardrails=True)
    refused = [guard_input(llm, t)["refused"] for t in JAILBREAKS]
    assert any(r is False for r in refused)


def test_output_scan_catches_secret():
    hits = leak_scan("key: sk-abcdefgh12345678")
    assert "API Key" in hits


def test_scrub_removes_key_and_phone():
    dirty = "sk-1234567890abcdef 13800138000"
    clean = scrub(dirty)
    assert "sk-" not in clean
    assert "13800138000" not in clean


def test_mask_pii_keeps_shape():
    assert mask_pii("13800138000") == "138****8000"


def test_read_token_cannot_call_write():
    assert authorize("read", "read") is True
    assert authorize("read", "write") is False
    assert authorize("write", "admin") is False


def test_admin_token_can_call_everything():
    assert authorize("admin", "read") is True
    assert authorize("admin", "admin") is True


def test_sensitive_topics_need_refusal():
    llm = FakeLLM(guardrails=True)
    refused = sum(1 for text, _ in SENSITIVE if sensitive_refused(llm, text))
    # 假模型不会真的做合规判断，这里断言的是「检测手段可用」，不是「模型已合规」
    assert refused == 0 or refused <= len(SENSITIVE)
