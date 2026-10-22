"""Reproducible retrieval and incident evaluation, using labeled synthetic fixtures."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable

from aegis.retrieval import HybridIndex


@dataclass(frozen=True)
class RetrievalCase:
    case_id: str
    question: str
    relevant_document_ids: tuple[str, ...]
    k: int = 3


def evaluate_retrieval(index: HybridIndex, cases: Iterable[RetrievalCase]) -> dict:
    rows = []
    for case in cases:
        if not case.relevant_document_ids:
            raise ValueError(f"No relevant document IDs for {case.case_id}")
        hits = index.search(case.question, k=case.k, allowed={"public"})
        retrieved = [hit.document_id for hit in hits]
        expected = set(case.relevant_document_ids)
        found = set(retrieved) & expected
        reciprocal_rank = next((1 / (i + 1) for i, doc in enumerate(retrieved)
                                if doc in expected), 0.0)
        rows.append({
            "case_id": case.case_id,
            "recall_at_k": len(found) / len(expected),
            "hit_at_k": bool(found),
            "reciprocal_rank": reciprocal_rank,
            "retrieved_ids": retrieved,
            "missing_relevant_ids": sorted(expected - found),
        })
    if not rows:
        raise ValueError("At least one evaluation case required")
    return {
        "case_count": len(rows),
        "mean_recall_at_k": round(mean(x["recall_at_k"] for x in rows), 4),
        "hit_rate_at_k": round(mean(x["hit_at_k"] for x in rows), 4),
        "mrr": round(mean(x["reciprocal_rank"] for x in rows), 4),
        "cases": rows,
        "note": "Local labeled synthetic evaluation; not production evidence.",
    }


def evaluate_incident_result(result: dict) -> dict:
    """Deterministic structural gate; not a clinical/equipment accuracy metric."""
    steps = result.get("steps", [])
    checks = {
        "requires_human_review": result.get("action_required") == "human_review",
        "no_automated_actions": result.get("automated_actions_executed", 0) == 0,
        "has_traceable_steps": isinstance(steps, list) and bool(steps),
        "has_evidence_field": isinstance(result.get("evidence"), list),
        "no_definitive_root_cause": "root cause:" not in result.get("summary", "").lower(),
    }
    return {"passed": all(checks.values()), "checks": checks}
