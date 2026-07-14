from typing import Protocol

from pydantic import BaseModel

from packages.agent_core.models import AgentResponse, HRRequest


class ProviderResponse(BaseModel):
    text: str
    model: str


class ModelProvider(Protocol):
    """Minimal interface implemented by all model providers."""

    async def generate(self, prompt: str) -> ProviderResponse: ...


class MockProvider:
    """Deterministic, offline provider used by default."""

    async def generate(self, prompt: str) -> ProviderResponse:
        normalized = " ".join(prompt.split())
        return ProviderResponse(
            text=f"Mock response for: {normalized}" if normalized else "Mock response.",
            model="mock-v1",
        )

    async def respond(self, request: HRRequest) -> AgentResponse:
        """Run the rule-based, knowledge-grounded HR workflow without a model call."""
        from packages.agent_core.workflow import HRAgentWorkflow

        return await HRAgentWorkflow().run(request)
