"""可复现的 RAG 模拟器：分块、向量检索、关键词检索、混合、重排、阈值。

向量用「字符袋 + 固定哈希」实现，不依赖任何模型和网络；同一文本永远同一向量，
所以阈值、TopK、召回率这些都可以在测试里精确断言。
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

DIM = 64


def _tokens(text: str) -> list[str]:
    """中文按 2-gram + 单字，英文按词。够把「退款时效」这类词变成可匹配的向量。"""
    text = text.lower()
    words = re.findall(r"[a-z0-9]+", text)
    han = re.findall(r"[\u4e00-\u9fff]", text)
    bigrams = [text[i : i + 2] for i in range(len(text) - 1) if re.match(r"[\u4e00-\u9fff]", text[i]) and re.match(r"[\u4e00-\u9fff]", text[i + 1])]
    return words + han + bigrams


def embed(text: str) -> list[float]:
    vec = [0.0] * DIM
    for tok in _tokens(text):
        h = 0
        for ch in tok:
            h = (h * 131 + ord(ch)) % 1000003
        vec[h % DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class Chunk:
    doc_id: str
    chunk_id: int
    text: str
    vector: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.vector:
            self.vector = embed(self.text)


def chunk_text(text: str, size: int = 120, overlap: int = 20) -> list[str]:
    """滑窗分块。overlap 用来防止「答案被切在两块中间」。"""
    text = text.strip()
    if size <= overlap:
        raise ValueError("overlap 必须小于 size")
    if len(text) <= size:
        return [text] if text else []
    out: list[str] = []
    start = 0
    while start < len(text):
        out.append(text[start : start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return out


class VectorStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add_document(self, doc_id: str, text: str, size: int = 120, overlap: int = 20) -> int:
        parts = chunk_text(text, size=size, overlap=overlap)
        for i, part in enumerate(parts):
            self.chunks.append(Chunk(doc_id=doc_id, chunk_id=i, text=part))
        return len(parts)

    def delete_document(self, doc_id: str) -> int:
        before = len(self.chunks)
        self.chunks = [c for c in self.chunks if c.doc_id != doc_id]
        return before - len(self.chunks)

    def search(self, query: str, top_k: int = 3, threshold: float = 0.0) -> list[tuple[float, Chunk]]:
        qv = embed(query)
        scored = [(cosine(qv, c.vector), c) for c in self.chunks]
        scored = [(s, c) for s, c in scored if s >= threshold]
        scored.sort(key=lambda x: (-x[0], x[1].doc_id, x[1].chunk_id))
        return scored[:top_k]


def bm25_search(chunks: list[Chunk], query: str, top_k: int = 3, k1: float = 1.5, b: float = 0.75) -> list[tuple[float, Chunk]]:
    """极简 BM25：关键词检索的替身，用来和向量检索对比召回差异。"""
    q_terms = set(_tokens(query))
    if not chunks:
        return []
    avg_len = sum(len(_tokens(c.text)) for c in chunks) / len(chunks) or 1.0
    scored: list[tuple[float, Chunk]] = []
    for c in chunks:
        terms = _tokens(c.text)
        tf: dict[str, int] = {}
        for t in terms:
            tf[t] = tf.get(t, 0) + 1
        score = 0.0
        for term in q_terms:
            if term not in tf:
                continue
            df = sum(1 for c2 in chunks if term in _tokens(c2.text)) or 1
            idf = math.log(1 + (len(chunks) - df + 0.5) / (df + 0.5))
            freq = tf[term]
            denom = freq + k1 * (1 - b + b * len(terms) / avg_len)
            score += idf * freq * (k1 + 1) / denom
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1].doc_id, x[1].chunk_id))
    return scored[:top_k]


def hybrid_search(
    store: VectorStore,
    query: str,
    top_k: int = 3,
    threshold: float = 0.0,
    alpha: float = 0.5,
) -> list[tuple[float, Chunk]]:
    """向量分与 BM25 分归一化后加权。alpha=1 全向量，alpha=0 全关键词。"""
    vec = store.search(query, top_k=len(store.chunks) or 1, threshold=0.0)
    bm = bm25_search(store.chunks, query, top_k=len(store.chunks) or 1)
    vmax = max((s for s, _ in vec), default=1.0) or 1.0
    bmax = max((s for s, _ in bm), default=1.0) or 1.0
    merged: dict[tuple[str, int], float] = {}
    chunks: dict[tuple[str, int], Chunk] = {}
    for s, c in vec:
        key = (c.doc_id, c.chunk_id)
        merged[key] = merged.get(key, 0.0) + alpha * (s / vmax)
        chunks[key] = c
    for s, c in bm:
        key = (c.doc_id, c.chunk_id)
        merged[key] = merged.get(key, 0.0) + (1 - alpha) * (s / bmax)
        chunks[key] = c
    out = [(s, chunks[k]) for k, s in merged.items() if s >= threshold]
    out.sort(key=lambda x: (-x[0], x[1].doc_id, x[1].chunk_id))
    return out[:top_k]


def rerank(query: str, hits: list[tuple[float, Chunk]], top_k: int = 3) -> list[tuple[float, Chunk]]:
    """交叉重排：把 query 与 chunk 的字面重叠也算进去，抑制「向量高分但答非所问」。"""
    q = set(_tokens(query))
    out: list[tuple[float, Chunk]] = []
    for base, c in hits:
        overlap = len(q & set(_tokens(c.text))) / (len(q) or 1)
        out.append((round(base + overlap, 6), c))
    out.sort(key=lambda x: (-x[0], x[1].doc_id, x[1].chunk_id))
    return out[:top_k]


def answer_with_citations(store: VectorStore, query: str, top_k: int = 2, threshold: float = 0.12) -> dict:
    """生成层的最小替身：只根据命中的块拼答案，并带上引用，命中为空就明说查不到。"""
    hits = store.search(query, top_k=top_k, threshold=threshold)
    if not hits:
        return {"answer": "知识库里没有相关资料。", "citations": [], "grounded": False}
    quotes = [f"[{c.doc_id}#{c.chunk_id}] {c.text[:40]}" for _, c in hits]
    return {
        "answer": "根据知识库：" + "；".join(quotes),
        "citations": [f"{c.doc_id}#{c.chunk_id}" for _, c in hits],
        "grounded": True,
    }
