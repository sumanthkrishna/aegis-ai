from aegis.retrieval import Document, HybridIndex, cosine, evidence_answer
from aegis.main import load_documents


def test_cosine():
    assert round(cosine([1, 0], [1, 0]), 4) == 1
    assert cosine([1, 0], [0, 1]) == 0


def test_retrieval_ranks_relevant_evidence():
    index = HybridIndex(load_documents("data/documents.json"))
    hits = index.search("UPS battery temperature airflow", allowed={"public"})
    assert hits
    assert hits[0].document_id in {"OPS-001", "INC-0031"}
    assert all(h.document_id != "OPS-PRIVATE" for h in hits)


def test_authorization_filter_is_applied_before_scoring():
    docs = [Document("r", "Secret", "battery fault", "restricted")]
    assert not HybridIndex(docs).search("battery fault", allowed={"public"})


def test_insufficient_evidence_is_explicit():
    answer = evidence_answer("unknown", [])
    assert answer["citations"] == []
    assert "Insufficient evidence" in answer["answer"]
