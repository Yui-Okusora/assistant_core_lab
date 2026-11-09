"""Two small retrieval indexes with the same interface.

BM25Index   — keyword ranking (the classic IR baseline)
TfidfIndex  — cosine similarity of TF-IDF vectors (a toy stand-in for embeddings)
HybridIndex — reciprocal-rank fusion of both

In a real system you would swap TfidfIndex for dense embeddings in FAISS or Chroma;
the interface `search(query, k) -> list[Hit]` stays the same.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol

from assistant_core.rag.chunker import Chunk

STOP = frozenset(
    "a an and are at be by can do for from how i in is it my of on or the to what when where who with".split()
)


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"\w+", text.lower()) if t not in STOP]


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class Index(Protocol):
    def search(self, query: str, k: int = 3) -> list[Hit]: ...


class BM25Index:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks, self.k1, self.b = chunks, k1, b
        self.docs = [tokenize(c.title + " " + c.text) for c in chunks]
        self.avgdl = sum(map(len, self.docs)) / max(len(self.docs), 1)
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def search(self, query: str, k: int = 3) -> list[Hit]:
        q = tokenize(query)
        scores = []
        for i, tf in enumerate(self.tf):
            dl = len(self.docs[i])
            s = sum(
                self.idf.get(t, 0) * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
                for t in q
                if t in tf
            )
            scores.append(s)
        ranked = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [Hit(self.chunks[i], round(scores[i], 3)) for i in ranked if scores[i] > 0]


class TfidfIndex:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        docs = [tokenize(c.title + " " + c.text) for c in chunks]
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log((1 + n) / (1 + f)) + 1 for t, f in df.items()}
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        v = {t: c * self.idf.get(t, 0) for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def search(self, query: str, k: int = 3) -> list[Hit]:
        q = self._vec(tokenize(query))
        sims = [sum(w * v.get(t, 0) for t, w in q.items()) for v in self.vecs]
        ranked = sorted(range(len(sims)), key=lambda i: -sims[i])[:k]
        return [Hit(self.chunks[i], round(sims[i], 3)) for i in ranked if sims[i] > 0]


class HybridIndex:
    """Reciprocal-rank fusion: score = sum 1 / (60 + rank). Scores are for ranking only."""

    def __init__(self, chunks: list[Chunk]):
        self.bm25, self.tfidf = BM25Index(chunks), TfidfIndex(chunks)

    def search(self, query: str, k: int = 3) -> list[Hit]:
        fused: dict[str, float] = {}
        best: dict[str, Hit] = {}
        for hits in (self.bm25.search(query, 10), self.tfidf.search(query, 10)):
            for rank, h in enumerate(hits):
                fused[h.chunk.id] = fused.get(h.chunk.id, 0) + 1 / (60 + rank)
                best.setdefault(h.chunk.id, h)
        top = sorted(fused, key=lambda cid: -fused[cid])[:k]
        return [Hit(best[cid].chunk, best[cid].score) for cid in top]


def make_index(kind: str, chunks: list[Chunk]) -> Index:
    return {"bm25": BM25Index, "tfidf": TfidfIndex, "hybrid": HybridIndex}[kind](chunks)
