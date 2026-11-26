"""第 50 章用例：RAG 的检索层与生成层怎么测。

要能回答：
1. 阈值调高，召回是不是掉了？（阈值 vs 召回的取舍）
2. TopK 调大，召回上去了，噪声也上去了吗？
3. 向量检索、关键词检索、混合检索，什么时候谁更好？
4. 知识库里没有答案时，系统会不会硬编一个（幻觉）？
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))

from rag_sim import (  # noqa: E402
    VectorStore,
    answer_with_citations,
    bm25_search,
    chunk_text,
    hybrid_search,
    rerank,
)

DOCS = {
    "policy": "退款政策：签收后 7 天内可无理由退款，需要提供订单号与商品照片。生鲜类商品不支持无理由退款。",
    "shipping": "物流时效：华东地区 24 小时内发货，偏远地区 72 小时。超时未发货可申请补偿。",
    "invoice": "发票说明：电子发票在订单完成后 3 个工作日内开具，可在订单详情页下载。",
}


def build_store(size: int = 60, overlap: int = 10) -> VectorStore:
    store = VectorStore()
    for doc_id, text in DOCS.items():
        store.add_document(doc_id, text, size=size, overlap=overlap)
    return store


def recall_at(store: VectorStore, queries: dict[str, str], top_k: int, threshold: float = 0.0) -> float:
    """每条 query 命中期望文档即算召回成功。"""
    hit = 0
    for query, expect_doc in queries.items():
        hits = store.search(query, top_k=top_k, threshold=threshold)
        if any(c.doc_id == expect_doc for _, c in hits):
            hit += 1
    return round(hit / len(queries), 2)


QUERIES = {
    "退款要几天": "policy",
    "生鲜能退吗": "policy",
    "几天能发货": "shipping",
    "发票什么时候开": "invoice",
}


def demo() -> None:
    print("== 分块 ==")
    parts = chunk_text("一二三四五六七八九十" * 10, size=20, overlap=5)
    print("块数:", len(parts), "首块:", parts[0][:12], "尾块:", parts[-1][:12])

    store = build_store()
    print("\n== 阈值 vs 召回（TopK=3）==")
    for t in (0.0, 0.15, 0.3, 0.5):
        print(f"threshold={t}: recall={recall_at(store, QUERIES, top_k=3, threshold=t)}")

    print("\n== TopK vs 召回（阈值 0.1）==")
    for k in (1, 2, 3):
        print(f"top_k={k}: recall={recall_at(store, QUERIES, top_k=k, threshold=0.1)}")

    print("\n== 三种检索对同一 query ==")
    q = "生鲜类商品退款"
    print("向量:", [(round(s, 3), c.doc_id, c.chunk_id) for s, c in store.search(q, top_k=3)])
    print("关键词:", [(round(s, 3), c.doc_id, c.chunk_id) for s, c in bm25_search(store.chunks, q, top_k=3)])
    print("混合:", [(round(s, 3), c.doc_id, c.chunk_id) for s, c in hybrid_search(store, q, top_k=3)])

    print("\n== 重排 ==")
    raw = store.search("发票下载", top_k=3)
    print("重排前:", [(round(s, 3), c.doc_id) for s, c in raw])
    print("重排后:", [(round(s, 3), c.doc_id) for s, c in rerank("发票下载", raw, top_k=3)])

    print("\n== 无关问题的得分（为什么阈值必须用真实语料标定）==")
    off = store.search("今天天气怎么样", top_k=3)
    print("无关问题 top3:", [(round(sc, 3), c.doc_id) for sc, c in off])
    print("阈值 0.3 时仍会命中 ->", answer_with_citations(store, "今天天气怎么样", threshold=0.3)["citations"])
    print("阈值 0.7 时才拒答 ->", answer_with_citations(store, "今天天气怎么样", threshold=0.7))
    print("有命中带引用:", answer_with_citations(store, "退款要几天", threshold=0.1))

    print("\n== 删除文档后，剩的命中来自别的文档（不是幻觉，是检索变弱）==")
    removed = store.delete_document("policy")
    rest = store.search("退款要几天", top_k=3, threshold=0.1)
    print("删除块数:", removed, "剩余命中:", [(round(sc, 3), c.doc_id) for sc, c in rest])


if __name__ == "__main__":
    demo()
