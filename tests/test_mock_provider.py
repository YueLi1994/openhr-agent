import asyncio

from packages.agent_core import MockProvider


def test_mock_provider_is_deterministic() -> None:
    provider = MockProvider()
    first = asyncio.run(provider.generate("fictional leave question"))
    second = asyncio.run(provider.generate("fictional leave question"))
    assert first == second
    assert first.model == "mock-v1"
