# Model Evaluation, Retrieval Quality & AI Governance

## Implemented and measured metrics

The local, labeled synthetic fixture supports Recall@k, Hit Rate@k and MRR for
retrieval quality. Run `python -m scripts.evaluate` after installing
`pip install -e '.[dev]'`. Never present fixture performance as real-world model
accuracy or operational performance.

The incident-quality gate tests: required human review, zero automated actions,
visible processing steps, evidence field and absence of a formulaic root-cause
claim. This is a structural check, NOT a validated correctness assessment.

Governance primitives include SHA-256 request digests in audit records,
time-stamped event IDs, authorized operation enums, a basic secrets-redaction
helper, and heuristic flags for untrusted document instructions. These are
prototype controls; they do not constitute full enterprise logging, DLP, policy
enforcement, authentication or prompt-injection protection.

## Model comparison protocol

The optional LLM adapter was introduced in the prior phase. Model-to-model
benchmarking is **specified but not automated**:

1. Freeze a labeled dataset of expected facts, evidence documents and forbidden actions.
2. Compare at least two provisioned models on exactly the same inputs.
3. Log model ID, timestamp, prompt revision, latency, token usage, cost and errors.
4. Independently score citation validity, answer correctness, refusal quality and
   operational safety using human-reviewed labels.
5. Report confidence intervals and failures; do not select based on a single score.

Never invent baseline numbers, tool-call accuracy or cost estimates.

## Risk controls and limitations

- No production identity, asset-scoped RBAC, tenant isolation or persistence yet.
- Do not send secrets or proprietary records to remote LLMs.
- Retrieved documents are untrusted instructions; no automated write/control tools.
- Log only safe metadata and hashes; do not store raw prompts indiscriminately.
- Gate `develop` merges on automated tests and a human architecture review.
