# AegisAI — Enterprise Operations & Reliability Intelligence

Architecture portfolio: retrieval-augmented operations knowledge, agentic incident intelligence, model evaluation, responsible AI and Azure observability. Uses synthetic and properly licensed public data only.

## Current phase: Enterprise Data & RAG Architecture

Implemented:
- Python/FastAPI health, search and evidence-answer endpoints
- Validated JSON document ingestion, source identifiers and classification metadata
- Lexical retrieval; **optional** SentenceTransformer dense embeddings with weighted hybrid ranking
- Source-linked evidence excerpts, explicit insufficient-evidence fallback, demo role-based filtering
- Synthetic UPS/cooling procedures and incident history, pytest tests and GitHub Actions CI

**Important:** The current response is retrieval-only; it does not yet use a generative model. The role header is a demonstration boundary, not enterprise authentication. See [architecture and run instructions](docs/architecture.md).

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn aegis.main:app --reload
pytest -q
```

Try the API at `http://localhost:8000/docs`. Set `AEGIS_EMBEDDINGS=sentence-transformers` to enable real embeddings (first run downloads a public model).

## Incident intelligence (current capability branch)

The `POST /v1/incidents/investigate` endpoint combines synthetic telemetry,
historical incidents and authorized knowledge retrieval. Calculations and routing
are deterministic, read-only and require human review. Optional LLM narrative
generation is opt-in, disabled by default. See
[incident orchestration architecture](docs/incident-orchestration.md).

Example:

```bash
curl -X POST http://localhost:8000/v1/incidents/investigate \
  -H 'Content-Type: application/json' \
  -H 'x-aegis-role: reader' \
  -d '{"asset_id":"UPS-101","question":"Investigate rising battery temperature"}'
```

## Model evaluation and governance

This capability adds reproducible retrieval metrics (Recall@k, Hit Rate@k,
MRR), incident structural safety checks, metadata-only audit event builders,
secret redaction helpers, and untrusted-text flags. Execute:

```bash
python -m scripts.evaluate
pytest -q
```

This is a labeled **synthetic** evaluation, not a benchmark of deployed models.
Model-to-model inference benchmarking is documented as a protocol and remains to
be implemented with provisioned models. See
[Model evaluation and governance](docs/model-evaluation-governance.md).

## Progressive branches

1. `feature/enterprise-data-rag-architecture` — ingestion, retrieval, cited evidence (**current**)
2. `feature/ai-inference-incident-orchestration` — synthetic incident analysis, controlled tools and optional AI summaries (**current**)
3. `feature/model-evaluation-governance` — retrieval evaluation, governance and model comparison protocol (**current**)
4. `feature/azure-deployment-observability` — Azure IaC, CI/CD, monitoring and cost assessment

Create each new capability branch from the completed preceding phase so the last phase carries the full implementation. Merge final capability branch into `develop` after checks, then promote `develop` to `master`.

## Confidentiality and safety

Never commit JPMC/Vertiv internal data or secrets. Synthetic outputs are educational only and must not be used to control real equipment. Document-based instructions are untrusted input; later phases will add threat-model tests and authenticated authorization.
