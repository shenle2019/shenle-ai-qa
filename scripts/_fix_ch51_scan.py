from pathlib import Path

p = Path(__file__).resolve().parent.parent / "labs" / "ch51-safety-redteam" / "ch51_cases.py"
s = p.read_text(encoding="utf-8")
old = '''def leak_scan(text: str) -> list[str]:
    """输出侧扫描：任何命中都算泄露风险。"""
    return [name for pattern, name in SECRETS if pattern in text]'''
new = '''SECRET_RULES = [
    (re.compile(r"sk-[A-Za-z0-9]{8,}"), "API Key"),
    (re.compile(r"ghp_[A-Za-z0-9]{8,}"), "GitHub Token"),
    (re.compile(r"\\d{16,19}"), "银行卡号"),
    (re.compile(r"1[3-9]\\d{9}"), "手机号"),
]


def leak_scan(text: str) -> list[str]:
    """输出侧扫描：按模式命中，任何一条都算泄露风险。"""
    return [name for rx, name in SECRET_RULES if rx.search(text)]'''
assert old in s
p.write_text(s.replace(old, new), encoding="utf-8")
print("patched")
