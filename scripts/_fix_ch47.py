from pathlib import Path

root = Path(__file__).resolve().parent.parent
lib = root / "labs" / "_shared" / "llm_sim.py"
src = lib.read_text(encoding="utf-8")
old = """    def count_tokens(self, text: str) -> int:
        return len(tokenize(text))"""
new = '''    def count_tokens(self, text: str) -> int:
        if not text or not text.strip():
            return 0
        return len(tokenize(text))'''
assert old in src, "lib pattern missing"
lib.write_text(src.replace(old, new), encoding="utf-8")

test = root / "labs" / "ch47-prompt-cases" / "test_ch47_prompt.py"
s = test.read_text(encoding="utf-8")
old2 = '''    loud = FakeLLM(context_limit=20, overflow_policy="truncate_head")
    quiet = FakeLLM(context_limit=20, overflow_policy="silent")
    a = loud.answer("前缀" + "退款" * 40)
    b = quiet.answer("前缀" + "退款" * 40)
    assert a.text != b.text
    assert b.truncated is True'''
new2 = '''    loud = FakeLLM(context_limit=20, overflow_policy="truncate_head")
    quiet = FakeLLM(context_limit=20, overflow_policy="silent")
    prompt = "头部标记" + "退款" * 40 + "尾部标记"
    a = loud.answer(prompt)
    b = quiet.answer(prompt)
    # 截头留开头；静默丢头留结尾。调用方只能靠 truncated 字段区分这两种
    assert "头部标记" in a.text
    assert "尾部标记" not in a.text
    assert a.truncated is True
    assert b.truncated is True'''
assert old2 in s, "test pattern missing"
test.write_text(s.replace(old2, new2), encoding="utf-8")
print("patched")
