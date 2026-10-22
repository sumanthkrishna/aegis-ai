"""Run local evaluation: python -m scripts.evaluate [--output evaluation-results.json]."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aegis.evaluation import RetrievalCase, evaluate_retrieval
from aegis.main import load_documents
from aegis.retrieval import HybridIndex


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    docs = load_documents(root / "data" / "documents.json")
    raw = json.loads((root / "data" / "retrieval-evaluation.json").read_text())
    cases = [RetrievalCase(case_id=c["case_id"], question=c["question"],
                           relevant_document_ids=tuple(c["relevant_document_ids"]),
                           k=c.get("k", 3)) for c in raw]
    report = evaluate_retrieval(HybridIndex(docs), cases)
    body = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(body, encoding="utf-8")
    print(body)


if __name__ == "__main__":
    main()
