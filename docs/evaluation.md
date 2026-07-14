# Deterministic evaluation

The versioned JSON dataset contains 32 independently authored synthetic cases spanning all domains, single and multi-intent routing, missing context and knowledge, injection, unauthorized access, high-risk decisions, medical/discriminatory/legal requests, and ambiguity.

`EvaluationRunner` invokes the same Mock Agent used by the demo and asserts domain, multi-intent status, human review, blocking, citation-manifest validity, no unsupported claims, and Pydantic output validity. It records local latency and aggregates accuracy rates. It never calls a model, network service, or external API.

Run `python -m packages.agent_core.evaluation`; reports go to ignored `reports/`. Or use `POST /api/v1/evaluations/run`, `GET /api/v1/evaluations/cases`, and `GET /api/v1/evaluations/latest`. The run endpoint accepts no body and must never be adapted to accept real employee data.

Adding a case requires an `EVAL-NNN` ID, synthetic input, explicit expectations, known source IDs, forbidden claims, notes, and tests. A passing score means these bounded deterministic assertions passed—not that the system is suitable for production HR work.
