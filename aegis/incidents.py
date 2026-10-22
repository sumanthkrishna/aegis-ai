"""Deterministic operational investigation with constrained retrieval and tool boundaries.

Every record is synthetic. No real equipment command/control capability exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from aegis.retrieval import HybridIndex


@dataclass(frozen=True)
class TelemetrySample:
    asset_id: str
    timestamp: str
    battery_temp_c: float
    ambient_temp_c: float
    load_pct: float


@dataclass(frozen=True)
class Incident:
    incident_id: str
    asset_id: str
    summary: str
    category: str


class TelemetryStore:
    def __init__(self, samples: list[TelemetrySample]):
        self.samples = samples

    def for_asset(self, asset_id: str) -> list[TelemetrySample]:
        return sorted(
            (x for x in self.samples if x.asset_id == asset_id),
            key=lambda x: x.timestamp,
        )


def analyze_temperature(samples: list[TelemetrySample]) -> dict:
    """A transparent analytic signal, not an equipment fault diagnosis."""
    if len(samples) < 4:
        return {"signal": "insufficient_data", "reason": "Need at least four samples"}
    half = len(samples) // 2
    baseline = mean(x.battery_temp_c for x in samples[:half])
    recent = mean(x.battery_temp_c for x in samples[half:])
    delta = round(recent - baseline, 2)
    return {
        "signal": "rising_temperature" if delta >= 3.0 else "no_significant_rise",
        "baseline_mean_c": round(baseline, 2),
        "recent_mean_c": round(recent, 2),
        "delta_c": delta,
        "sample_count": len(samples),
        "rule": "recent_minus_baseline_gte_3c",
    }


class InvestigationOrchestrator:
    """Fixed-step workflow; no autonomous tool selection or write-capable actions."""

    def __init__(
        self, index: HybridIndex, telemetry: TelemetryStore,
        incidents: list[Incident],
    ):
        self.index = index
        self.telemetry = telemetry
        self.incidents = incidents

    def investigate(self, asset_id: str, question: str) -> dict:
        samples = self.telemetry.for_asset(asset_id)
        if not samples:
            return {
                "asset_id": asset_id,
                "status": "not_found",
                "summary": "No authorized synthetic telemetry found for this asset.",
                "evidence": [],
                "steps": ["lookup_telemetry"],
                "action_required": "human_review",
            }
        telemetry_analysis = analyze_temperature(samples)
        incident_matches = [
            x for x in self.incidents if x.asset_id == asset_id
        ]
        query = f"{question} UPS battery temperature airflow thermal incident"
        hits = self.index.search(query, k=3, allowed={"public"})
        citations = [
            {"document_id": h.document_id, "title": h.title, "source": h.source}
            for h in hits
        ]
        return {
            "asset_id": asset_id,
            "status": "investigated",
            "summary": "Deterministic telemetry analysis and related documents retrieved. "
                       "No root cause is asserted by the system.",
            "telemetry": telemetry_analysis,
            "historical_incidents": [
                {"incident_id": x.incident_id, "category": x.category,
                 "summary": x.summary} for x in incident_matches
            ],
            "evidence": citations,
            "steps": ["lookup_telemetry", "analyze_temperature",
                      "retrieve_prior_incidents", "retrieve_knowledge",
                      "prepare_human_review"],
            "action_required": "human_review",
            "automated_actions_executed": 0,
        }
