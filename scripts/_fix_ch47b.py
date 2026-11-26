from pathlib import Path

test = Path(__file__).resolve().parent.parent / "labs" / "ch47-prompt-cases" / "test_ch47_prompt.py"
s = test.read_text(encoding="utf-8")
start = s.index("def test_silent_policy_hides_the_truncation")
end = s.index("def test_error_policy_raises")
block = '''def test_silent_policy_hides_the_truncation():
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


'''
test.write_text(s[:start] + block + s[end:], encoding="utf-8")
print("rewritten")
