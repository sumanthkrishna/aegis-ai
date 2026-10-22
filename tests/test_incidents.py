from pathlib import Path

from fastapi.testclient import TestClient

from aegis.incident_api import create_incident_router, load_synthetic_operations
from aegis.incidents import TelemetrySample, analyze_temperature
from aegis.main import create_app
from aegis.retrieval import Document, HybridIndex


def test_temperature_detects_sustained_rise():
    points = [
        TelemetrySample("x", str(i), temp, 20, 50)
        for i, temp in enumerate([24, 25, 26, 31, 33, 35])
    ]
    report = analyze_temperature(points)
    assert report["signal"] == "rising_temperature"
    assert report["delta_c"] >= 3


def test_temperature_requires_minimum_history():
    assert analyze_temperature([])["signal"] == "insufficient_data"


def make_client():
    index = HybridIndex([Document("d1", "UPS thermal guidance",
                                  "battery temperature airflow thermal incident")])
    telemetry, incidents = load_synthetic_operations(Path("data/operations.json"))
    api = create_app(index)
    api.include_router(create_incident_router(index, telemetry, incidents))
    return TestClient(api)


def test_investigation_requires_reader():
    response = make_client().post("/v1/incidents/investigate",
                                  json={"asset_id": "UPS-101"})
    assert response.status_code == 403


def test_investigation_evidence_is_read_only():
    response = make_client().post(
        "/v1/incidents/investigate",
        headers={"x-aegis-role": "reader"},
        json={"asset_id": "UPS-101", "question": "Why did temperature rise?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["telemetry"]["signal"] == "rising_temperature"
    assert body["evidence"][0]["document_id"] == "d1"
    assert body["action_required"] == "human_review"
    assert body["automated_actions_executed"] == 0


def test_unknown_asset_is_not_hallucinated():
    response = make_client().post(
        "/v1/incidents/investigate",
        headers={"x-aegis-role": "reader"},
        json={"asset_id": "DOES-NOT-EXIST"},
    )
    assert response.json()["status"] == "not_found"
