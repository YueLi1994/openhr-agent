import asyncio

from packages.agent_core import HRRequest, MockProvider


def test_mock_provider_is_deterministic() -> None:
    provider = MockProvider()
    first = asyncio.run(provider.generate("fictional leave question"))
    second = asyncio.run(provider.generate("fictional leave question"))
    assert first == second
    assert first.model == "mock-v1"


def test_mock_provider_runs_grounded_hr_workflow() -> None:
    response = asyncio.run(
        MockProvider().respond(HRRequest(message="What benefits are available?"))
    )
    assert response.sources
    assert response.structured_data["provider"] == "mock-v2"
