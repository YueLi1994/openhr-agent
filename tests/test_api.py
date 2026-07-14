from fastapi.testclient import TestClient

from apps.api.app.main import app

client = TestClient(app)


def test_chat_endpoint_returns_agent_response() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"message": "What benefits are available?", "locale": "en-US"},
    )
    assert response.status_code == 200
    assert response.json()["domain"] == "benefits"


def test_domain_and_source_catalogs() -> None:
    domains = client.get("/api/v1/domains")
    sources = client.get("/api/v1/knowledge/sources")
    assert "unsupported" in domains.json()
    assert {item["source_id"] for item in sources.json()} >= {"leave-policy", "benefits-policy"}
