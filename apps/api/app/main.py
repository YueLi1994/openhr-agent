from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from packages.agent_core import AgentResponse, HRAgentWorkflow, HRDomain, HRRequest


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


@app.post("/api/v1/chat", response_model=AgentResponse, tags=["agent"])
async def chat(request: HRRequest) -> AgentResponse:
    return await workflow.run(request)


@app.get("/api/v1/domains", response_model=list[str], tags=["agent"])
def domains() -> list[str]:
    return [domain.value for domain in HRDomain]


@app.get("/api/v1/knowledge/sources", response_model=list[dict[str, str]], tags=["knowledge"])
def knowledge_sources() -> list[dict[str, str]]:
    return workflow.retriever.list_sources()
