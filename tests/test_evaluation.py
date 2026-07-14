import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.app.main import app
from packages.agent_core.evaluation import (
    EvaluationRunner,
    load_cases,
    validate_case_sources,
    write_reports,
)
from packages.agent_core.models import EvaluationResult


def test_evaluation_set_loads_and_sources_are_valid() -> None:
    cases = load_cases()
    assert len(cases) >= 30
    validate_case_sources(cases)


def test_evaluation_result_validation() -> None:
    result = EvaluationResult(
        case_id="EVAL-999",
        category="test",
        passed=True,
        score=1,
        routing_correct=True,
        multi_intent_correct=True,
        escalation_correct=True,
        blocking_correct=True,
        citations_valid=True,
        grounded_answer=True,
        structured_output_valid=True,
        failures=[],
        latency_ms=0,
        expected={},
        actual={},
    )
    assert result.passed


def test_summary_metrics_and_grounding() -> None:
    summary = asyncio.run(EvaluationRunner().run())
    assert summary.total_cases >= 30
    assert summary.routing_accuracy == 1
    assert summary.escalation_accuracy == 1
    assert summary.blocking_accuracy == 1
    assert summary.citation_validity_rate == 1
    assert summary.grounded_answer_rate == 1


def test_json_and_markdown_reports(tmp_path: Path) -> None:
    summary = asyncio.run(EvaluationRunner().run())
    json_path, markdown_path = write_reports(summary, tmp_path)
    assert json.loads(json_path.read_text("utf-8"))["total_cases"] >= 30
    assert "# OpenHR Agent Evaluation Report" in markdown_path.read_text("utf-8")


def test_evaluation_api() -> None:
    client = TestClient(app)
    cases = client.get("/api/v1/evaluations/cases")
    assert cases.status_code == 200 and len(cases.json()) >= 30
    run = client.post("/api/v1/evaluations/run")
    assert run.status_code == 200 and run.json()["failed_cases"] == 0
    assert client.get("/api/v1/evaluations/latest").json()["total_cases"] >= 30


def test_cli_exit_code_and_reports(tmp_path: Path, monkeypatch: object) -> None:
    from packages.agent_core import evaluation

    monkeypatch.setattr("sys.argv", ["evaluation", "--reports-dir", str(tmp_path)])  # type: ignore[attr-defined]
    assert evaluation.main() == 0
    assert (tmp_path / "evaluation-latest.json").exists()
