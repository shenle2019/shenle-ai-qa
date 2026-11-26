from pathlib import Path

p = Path(__file__).resolve().parent.parent / "labs" / "ch54-model-eval" / "test_ch54_eval.py"
s = p.read_text(encoding="utf-8")
old = '''def test_confusion_metrics_match_hand_count():
    # GOLD 里 good 的 tp=2 fp=1 fn=0 -> precision 2/3 recall 1.0
    p, r, f1 = precision_recall_f1(GOLD, "good")
    assert p == 0.6667
    assert r == 1.0
    assert f1 > 0.79'''
new = '''def test_confusion_metrics_match_hand_count():
    # GOLD 里 good：tp=2（1、4 条）、fp=1（第 5 条把 bad 判成 good）、fn=1（第 2 条）
    p, r, f1 = precision_recall_f1(GOLD, "good")
    assert p == 0.6667
    assert r == 0.6667
    assert f1 == 0.6667'''
assert old in s
p.write_text(s.replace(old, new), encoding="utf-8")
print("patched")
