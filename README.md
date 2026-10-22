# AegisAI — Enterprise Operations & Reliability Intelligence

Architecture portfolio project demonstrating enterprise retrieval-augmented generation, incident intelligence, evaluation, responsible AI, and Azure operations using synthetic and properly licensed public data.

## Delivery roadmap

1. **Week 1 — RAG foundation:** document ingestion, hybrid retrieval, cited answers, FastAPI and UI.
2. **Week 2 — Incident intelligence:** synthetic telemetry, investigation tools, controlled agent workflow.
3. **Week 3 — Evaluation and governance:** model comparison, regression dataset, guardrails, audit logs.
4. **Week 4 — Azure deployment:** infrastructure as code, CI/CD, observability, cost and architecture documentation.

## Branching strategy

`master` (release) ← `develop` (integration) ← `feature/week-04-azure-production-readiness` ← `feature/week-03-evaluation-governance` ← `feature/week-02-agentic-incident-intelligence` ← `feature/week-01-rag-foundation`.

**Progressive branching rule:** Create each new weekly branch from the completed preceding week's HEAD, rather than pre-creating all branches at the same commit. Week 4 then contains the cumulative deliverables. Merge Week 4 into `develop`, test, then merge `develop` into `master`. Do not merge unfinished work.

GitHub initializes new repositories with `main` as the default branch; this project uses `master` as its requested release branch. Set `master` as the default in repository settings if desired.

No proprietary JPMC or Vertiv data, credentials or internal documentation may be committed.
