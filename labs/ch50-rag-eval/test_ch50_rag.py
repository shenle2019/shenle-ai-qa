from ch50_cases import (  # noqa: F401
    DOCS,
    QUERIES,
    build_store,
    recall_at,
)

from rag_sim import (
    VectorStore,
    answer_with_citations,
    bm25_search,
    chunk_text,
    hybrid_search,
    rerank,
)


def test_chunk_overlap_keeps_boundary_text():
    text = "abcdefghij" * 4
    parts = chunk_text(text, size=10, overlap=4)
    assert len(parts) > 1
    # 相邻块必须有重叠，否则答案跨块就找不到了
    assert parts[0][-4:] == parts[1][:4]


def test_chunk_rejects_invalid_overlap():
    try:
        chunk_text("abc", size=5, overlap=5)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("应当报错")


def test_threshold_up_recall_down():
    store = build_store()
    loose = recall_at(store, QUERIES, top_k=3, threshold=0.0)
    tight = recall_at(store, QUERIES, top_k=3, threshold=0.5)
    assert tight <= loose


def test_topk_up_recall_up_or_equal():
    store = build_store()
    one = recall_at(store, QUERIES, top_k=1, threshold=0.0)
    three = recall_at(store, QUERIES, top_k=3, threshold=0.0)
    assert three >= one


def test_vector_hit_returns_expected_doc():
    store = build_store()
    hits = store.search("发票什么时候开", top_k=1)
    assert hits and hits[0][1].doc_id == "invoice"


def test_keyword_search_finds_exact_term():
    store = build_store()
    hits = bm25_search(store.chunks, "生鲜", top_k=2)
    assert hits and hits[0][1].doc_id == "policy"


def test_hybrid_is_not_empty_for_both_kinds_of_query():
    store = build_store()
    assert hybrid_search(store, "退款要几天", top_k=2)
    assert hybrid_search(store, "生鲜", top_k=2)


def test_rerank_keeps_same_number_of_hits():
    store = build_store()
    raw = store.search("发票下载", top_k=3)
    out = rerank("发票下载", raw, top_k=3)
    assert len(out) == len(raw)


def test_no_hit_stays_ungrounded():
    store = build_store()
    ans = answer_with_citations(store, "今天天气怎么样", threshold=0.9)
    assert ans["grounded"] is False
    assert ans["citations"] == []


def test_hit_is_grounded_with_citations():
    store = build_store()
    ans = answer_with_citations(store, "退款要几天", threshold=0.05)
    assert ans["grounded"] is True
    assert ans["citations"]
    assert all("#" in c for c in ans["citations"])


def test_delete_document_removes_it_from_results():
    store = build_store()
    store.delete_document("policy")
    hits = store.search("退款要几天", top_k=5, threshold=0.0)
    assert all(c.doc_id != "policy" for _, c in hits)


def test_conflicting_docs_both_retrieved():
    store = VectorStore()
    store.add_document("old", "退货政策：30 天内可退，无需理由。", size=80)
    store.add_document("new", "退货政策：7 天内可退，需要理由。", size=80)
    hits = store.search("退货政策几天内", top_k=5)
    docs = {c.doc_id for _, c in hits}
    assert {"old", "new"} <= docs
