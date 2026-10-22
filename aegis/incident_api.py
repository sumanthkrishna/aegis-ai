"""Read-only incident analysis API router."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from aegis.incidents import Incident, InvestigationOrchestrator, TelemetrySample, TelemetryStore
from aegis.inference import configured_provider
from aegis.retrieval import HybridIndex

router = APIRouter(prefix="/v1/incidents", tags=["incidents"])


class InvestigationRequest(BaseModel):
    asset_id: str = Field(min_length=1, max_length=64)
    question: str = Field(default="Investigate the telemetry pattern", max_length=1000)
    include_llm_narrative: bool = False


def load_synthetic_operations(path: Path) -> tuple[TelemetryStore, list[Incident]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples = [TelemetrySample(**item) for item in data["telemetry"]]
    incidents = [Incident(**item) for item in data["incidents"]]
    return TelemetryStore(samples), incidents


def create_incident_router(index: HybridIndex, telemetry: TelemetryStore,
                           incidents: list[Incident]) -> APIRouter:
    api = APIRouter(prefix="/v1/incidents", tags=["incidents"])
    orchestrator = InvestigationOrchestrator(index, telemetry, incidents)

    @api.post("/investigate")
    def investigate(req: InvestigationRequest,
                    x_aegis_role: str | None = Header(default=None)) -> dict:
        # Demo auth boundary only. Later replace with verified identity and asset permissions.
        if x_aegis_role != "reader":
            raise HTTPException(status_code=403, detail="Demo reader role required")
        result = orchestrator.investigate(req.asset_id, req.question)
        if req.include_llm_narrative and result["status"] == "investigated":
            provider = configured_provider()
            result["narrative"] = provider.summarize(result)
            result["narrative_is_model_generated"] = (
                provider.__class__.__name__ != "DisabledNarrativeProvider"
            )
        return result

    return api
