from pathlib import Path

p = Path(__file__).resolve().parent.parent / "labs" / "ch50-rag-eval" / "ch50_cases.py"
s = p.read_text(encoding="utf-8")

old = '''    print("\\n== 无命中时不硬编 ==")
    print(answer_with_citations(store, "今天天气怎么样", threshold=0.3))'''
new = '''    print("\\n== 无关问题的得分（为什么阈值必须用真实语料标定）==")
    off = store.search("今天天气怎么样", top_k=3)
    print("无关问题 top3:", [(round(sc, 3), c.doc_id) for sc, c in off])
    print("阈值 0.3 时仍会命中 ->", answer_with_citations(store, "今天天气怎么样", threshold=0.3)["citations"])
    print("阈值 0.7 时才拒答 ->", answer_with_citations(store, "今天天气怎么样", threshold=0.7))'''
assert old in s
s = s.replace(old, new)

old2 = '''    print("\\n== 删除文档 ==")
    print("删除块数:", store.delete_document("policy"), "剩余命中:", len(store.search("退款要几天", top_k=3, threshold=0.1)))'''
new2 = '''    print("\\n== 删除文档后，剩的命中来自别的文档（不是幻觉，是检索变弱）==")
    removed = store.delete_document("policy")
    rest = store.search("退款要几天", top_k=3, threshold=0.1)
    print("删除块数:", removed, "剩余命中:", [(round(sc, 3), c.doc_id) for sc, c in rest])'''
assert old2 in s
p.write_text(s.replace(old2, new2), encoding="utf-8")
print("patched")
