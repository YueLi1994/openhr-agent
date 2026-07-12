from typing import Protocol

from pydantic import BaseModel


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
