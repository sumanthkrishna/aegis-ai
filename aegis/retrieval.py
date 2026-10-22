"""Local hybrid retrieval: deterministic lexical scores + optional real embeddings.

No remote model is called without explicit configuration. All example records are synthetic.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Protocol

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


class EmbeddingProvider(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


class SentenceTransformerEmbeddings:
    """True dense vector embeddings, loaded lazily to avoid import-time downloads."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


@dataclass(frozen=True)
class Document:
    document_id: str
    title: str
    text: str
    classification: str = "public"
    source: str = "synthetic"


@dataclass(frozen=True)
class Hit:
    document_id: str
    title: str
    excerpt: str
    score: float
    source: str


def cosine(a: list[float], b: list[float]) -> float:
    denom = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / denom if denom else 0.0


class HybridIndex:
    """In-memory index suitable for small pilot corpora; replace with Azure AI Search at scale."""

    def __init__(self, documents: list[Document], embedder: EmbeddingProvider | None = None):
        self.documents = documents
        self.embedder = embedder
        self.vectors = embedder.encode([f"{d.title}\n{d.text}" for d in documents]) if embedder else []

    def search(self, query: str, k: int = 5, allowed: set[str] | None = None) -> list[Hit]:
        if not query.strip():
            return []
        query_tokens = tokens(query)
        qvector = self.embedder.encode([query])[0] if self.embedder else None
        ranked = []
        for i, doc in enumerate(self.documents):
            if allowed is not None and doc.classification not in allowed:
                continue  # authorization before retrieval, not after generation
            dtokens = tokens(f"{doc.title} {doc.text}")
            lexical = len(query_tokens & dtokens) / max(len(query_tokens), 1)
            dense = max(0.0, cosine(qvector, self.vectors[i])) if qvector else 0.0
            score = (0.45 * lexical + 0.55 * dense) if qvector else lexical
            if score > 0:
                ranked.append(Hit(doc.document_id, doc.title, doc.text[:450], round(score, 5), doc.source))
        return sorted(ranked, key=lambda h: (-h.score, h.document_id))[:k]


def evidence_answer(question: str, hits: list[Hit]) -> dict:
    """Safe retrieval-only fallback: never fabricate an LLM-synthesized explanation."""
    if not hits:
        return {"answer": "Insufficient evidence in the authorized knowledge collection.",
                "citations": [], "mode": "retrieval-only"}
    return {
        "answer": "Relevant evidence was retrieved. Review the cited excerpts; no generative conclusion was made.",
        "citations": [{"document_id": h.document_id, "title": h.title,
                       "source": h.source, "excerpt": h.excerpt} for h in hits],
        "mode": "retrieval-only",
    }
