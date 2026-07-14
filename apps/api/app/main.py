from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from packages.agent_core import (
    AgentResponse,
    EvaluationCase,
    EvaluationSummary,
    HRAgentWorkflow,
    HRDomain,
    HRRequest,
)
from packages.agent_core.evaluation import EvaluationRunner, load_cases


class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str


app = FastAPI(title="OpenHR Agent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="openhr-agent-api", provider="mock")


workflow = HRAgentWorkflow()
evaluation_runner = EvaluationRunner(workflow)
latest_evaluation: EvaluationSummary | None = None


@app.post("/api/v1/chat", response_model=AgentResponse, tags=["agent"])
async def chat(request: HRRequest) -> AgentResponse:
    return await workflow.run(request)


@app.get("/api/v1/domains", response_model=list[str], tags=["agent"])
def domains() -> list[str]:
    return [domain.value for domain in HRDomain]


@app.get("/api/v1/knowledge/sources", response_model=list[dict[str, str]], tags=["knowledge"])
def knowledge_sources() -> list[dict[str, str]]:
    return workflow.retriever.list_sources()


@app.get("/api/v1/evaluations/cases", response_model=list[EvaluationCase], tags=["evaluation"])
def evaluation_cases() -> list[EvaluationCase]:
    """Return only the repository's built-in synthetic cases."""
    return load_cases()


@app.post("/api/v1/evaluations/run", response_model=EvaluationSummary, tags=["evaluation"])
async def run_evaluation() -> EvaluationSummary:
    """Run built-in cases; the endpoint intentionally accepts no employee-data body."""
    global latest_evaluation
    latest_evaluation = await evaluation_runner.run()
    return latest_evaluation


@app.get("/api/v1/evaluations/latest", response_model=EvaluationSummary, tags=["evaluation"])
async def get_latest_evaluation() -> EvaluationSummary:
    global latest_evaluation
    if latest_evaluation is None:
        latest_evaluation = await evaluation_runner.run()
    return latest_evaluation
