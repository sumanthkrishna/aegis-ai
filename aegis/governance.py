"""Minimal governance primitives: redacted audit records and untrusted-text guards.

This module does not provide enterprise identity, DLP or full prompt-injection defense.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4

SENSITIVE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"),
)
ADVERSARIAL_PATTERNS = (
    re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior|system)\s+instructions"),
    re.compile(r"(?i)(reveal|print|show)\s+(the\s+)?(system prompt|secrets|api key)"),
)


def redact(value: str) -> str:
    for pattern in SENSITIVE_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def untrusted_text_flags(value: str) -> list[str]:
    """Heuristic risk indicators, NOT a replacement for source isolation."""
    return ["potential_instruction_injection"] if any(p.search(value) for p in ADVERSARIAL_PATTERNS) else []


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    recorded_at: str
    operation: str
    request_digest: str
    outcome: str
    evidence_ids: tuple[str, ...]
    human_review_required: bool


def build_audit_event(operation: str, request: str, outcome: str,
                      evidence_ids: list[str] | None = None,
                      human_review_required: bool = True) -> dict:
    if operation not in {"knowledge_search", "incident_investigation", "retrieval_evaluation"}:
        raise ValueError("Operation not permitted")
    if outcome not in {"success", "insufficient_evidence", "error", "denied"}:
        raise ValueError("Invalid outcome")
    event = AuditEvent(
        event_id=str(uuid4()),
        recorded_at=datetime.now(timezone.utc).isoformat(),
        operation=operation,
        request_digest=hashlib.sha256(request.encode("utf-8")).hexdigest(),
        outcome=outcome,
        evidence_ids=tuple(evidence_ids or []),
        human_review_required=human_review_required,
    )
    return asdict(event)
