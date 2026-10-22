from fastapi.testclient import TestClient
from aegis.main import create_app
from aegis.retrieval import Document, HybridIndex


def client():
    return TestClient(create_app(HybridIndex([
        Document("a", "UPS manual", "UPS battery temperature and airflow", "public"),
        Document("b", "Restricted", "Secret high temperature", "restricted"),
    ])))


def test_health():
    assert client().get("/health").json()["documents"] == 2


def test_search_requires_demo_role():
    assert client().post("/v1/search", json={"query": "UPS"}).status_code == 403


def test_search_cites_authorized_sources_only():
    response = client().post("/v1/answer", headers={"x-aegis-role": "reader"},
                             json={"query": "UPS battery"})
    assert response.status_code == 200
    assert [x["document_id"] for x in response.json()["citations"]] == ["a"]
