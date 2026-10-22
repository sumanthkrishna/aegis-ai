"""AegisAI ingestion and retrieval HTTP API (synthetic/public documents only)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from aegis.retrieval import Document, HybridIndex, SentenceTransformerEmbeddings, evidence_answer


def load_documents(path: str | Path) -> list[Document]:
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"document_id", "title", "text"}
    if not isinstance(records, list) or any(not required.issubset(x) for x in records):
        raise ValueError("Document dataset must be a list of records with document_id/title/text")
    ids = [x["document_id"] for x in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate document IDs")
    return [Document(**x) for x in records]


def create_app(index: HybridIndex | None = None) -> FastAPI:
    app = FastAPI(title="AegisAI Knowledge API", version="0.1.0")
    if index is None:
        path = os.getenv("AEGIS_DOCUMENT_PATH", str(Path(__file__).parents[1] / "data" / "documents.json"))
        mode = os.getenv("AEGIS_EMBEDDINGS", "lexical").lower()
        if mode not in {"lexical", "sentence-transformers"}:
            raise ValueError("AEGIS_EMBEDDINGS must be lexical or sentence-transformers")
        embedder = SentenceTransformerEmbeddings() if mode == "sentence-transformers" else None
        index = HybridIndex(load_documents(path), embedder)
    app.state.index = index

    class SearchRequest(BaseModel):
        query: str = Field(min_length=1, max_length=2000)
        k: int = Field(default=5, ge=1, le=20)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "documents": len(app.state.index.documents)}

    @app.post("/v1/search")
    def search(request: SearchRequest, x_aegis_role: str | None = Header(default=None)) -> dict:
        # Demo access boundary only. Production must verify signed identity and document ACLs.
        if x_aegis_role != "reader":
            raise HTTPException(status_code=403, detail="Demo reader role required")
        hits = app.state.index.search(request.query, k=request.k, allowed={"public"})
        return {"hits": [hit.__dict__ for hit in hits]}

    @app.post("/v1/answer")
    def answer(request: SearchRequest, x_aegis_role: str | None = Header(default=None)) -> dict:
        if x_aegis_role != "reader":
            raise HTTPException(status_code=403, detail="Demo reader role required")
        hits = app.state.index.search(request.query, k=request.k, allowed={"public"})
        return evidence_answer(request.query, hits)

    return app


app = create_app()
