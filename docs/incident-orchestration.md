# AI Inference & Incident Orchestration

## Objective

Extend the enterprise knowledge API with an auditable, read-only incident
investigation workflow. All operational data is synthetic and disconnected from
actual control systems.

## Implemented workflow

1. Validate the caller's demo reader role.
2. Retrieve samples for the requested synthetic asset ID.
3. Compute baseline and recent battery temperature averages using Python.
4. Retrieve synthetic historical incidents.
5. Search the permitted knowledge collection, returning document IDs.
6. Produce structured findings requiring human review.
7. Optionally summarize using a hosted model (explicit environment opt-in).

The workflow is **deterministic orchestration**, not autonomous multi-agent
planning. Its sequential stages are separable tool responsibilities. Future
iterations may introduce LangGraph state routing and a safe agent planner
after retrieval evaluation, identity and policy boundaries are established.

## Endpoint

`POST /v1/incidents/investigate`

Headers: `x-aegis-role: reader` (demonstration only).

Payload: `{"asset_id":"UPS-101","question":"Why is battery temperature rising?"}`

The response contains numerical signals, matching historical incidents, retrieval
citations, executed steps, a human-review flag and a zero-action count.

## Optional language-model summary

Install `pip install -e '.[llm]'` and set:
- `AEGIS_LLM_ENABLED=true`
- `AEGIS_LLM_MODEL=<model-available-to-your-account>`
- `OPENAI_API_KEY=<private-secret>`

Then send `include_llm_narrative: true`. Never commit API keys.
Leave model inference disabled for offline and CI tests.

## Security constraints and follow-up work

The header-based role is not secure authentication. No tenant-bound asset ACLs,
prompt injection defenses, signed identity, real-time telemetry integrations,
or production retention controls have been implemented. No remediation
commands or external write tools are exposed. Generative summaries may be wrong;
deterministic calculations and citations remain the audit source of record.
