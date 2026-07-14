# Architecture

OpenHR Agent is a small monorepo with independently testable web, API, and deterministic Agent Core layers.

```mermaid
flowchart LR
  Web[React demo] -->|POST /api/v1/chat| API[FastAPI + Pydantic]
  API --> WF[HR Agent workflow]
  WF --> Safe[Safety rules]
  WF --> Route[Controller Router]
  WF --> Retrieve[Keyword retriever]
  Retrieve --> KB[Acme fictional Markdown]
  WF --> Mock[Deterministic Mock Agent]
  WF --> Validate[Citation and risk validation]
  Validate --> Response[Structured AgentResponse]
```

## Request lifecycle

```mermaid
flowchart TD
  A[Validate HRRequest] --> B[Prompt-injection check]
  B -->|blocked| J[Safe refusal]
  B --> C[Domain routing]
  C --> D{High risk or private data?}
  D -->|yes| K[Neutral response + human escalation]
  D -->|no| E{Employee context missing?}
  E -->|yes| L[Request missing information]
  E -->|no| F[Split detected intents]
  F --> G[Domain-filtered keyword retrieval]
  G --> H{Grounded sources?}
  H -->|no| K
  H -->|yes| I[Generate cited deterministic answer]
  I --> M[Validate citations and return AgentResponse]
```

The web application owns presentation. FastAPI owns transport and validation. `agent_core` owns strict models, routing, safety, retrieval, and workflow orchestration. Markdown policies are local and reviewable. No model or external network call occurs in the default path.

See [routing](routing.md), [safety](safety.md), and [retrieval](retrieval.md).
