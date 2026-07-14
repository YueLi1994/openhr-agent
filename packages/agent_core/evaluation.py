from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from .models import AgentResponse, EvaluationCase, EvaluationResult, EvaluationSummary, HRRequest
from .retrieval import SOURCE_MANIFEST
from .workflow import HRAgentWorkflow

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = Path(__file__).parent / "data" / "evaluation_cases.json"
REPORTS_DIR = ROOT / "reports"


def load_cases(path: Path = DEFAULT_CASES_PATH) -> list[EvaluationCase]:
    return [EvaluationCase.model_validate(item) for item in json.loads(path.read_text("utf-8"))]


def validate_case_sources(cases: list[EvaluationCase]) -> None:
    known = {item[0] for item in SOURCE_MANIFEST}
    unknown = sorted({source for case in cases for source in case.expected_source_ids} - known)
    if unknown:
        raise ValueError(f"Unknown expected source IDs: {', '.join(unknown)}")


class EvaluationRunner:
    def __init__(self, workflow: HRAgentWorkflow | None = None) -> None:
        self.workflow = workflow or HRAgentWorkflow()
        self.known_sources = {item[0] for item in SOURCE_MANIFEST}

    async def run_case(self, case: EvaluationCase) -> EvaluationResult:
        started = perf_counter()
        response = await self.workflow.run(
            HRRequest(message=case.input_message, employee_id=case.employee_context)
        )
        latency = (perf_counter() - started) * 1000
        routing = response.structured_data.get("routing", {})
        source_ids = {source.source_id for source in response.sources}
        blocked = "request_blocked" in response.structured_data.get("workflow_steps", [])
        checks = {
            "routing": response.domain == case.expected_domain,
            "multi-intent": routing.get("is_multi_intent") == case.expected_multi_intent,
            "escalation": response.requires_human_review == case.expected_human_review,
            "blocking": blocked == case.expected_blocked,
            "citations": source_ids <= self.known_sources
            and set(case.expected_source_ids) <= source_ids,
            "grounding": all(
                claim.casefold() not in response.answer.casefold()
                for claim in case.forbidden_claims
            )
            and (
                bool(response.sources)
                or bool(response.missing_information)
                or "will not invent" in response.answer.lower()
                or case.expected_blocked
                or response.requires_human_review
            ),
        }
        try:
            AgentResponse.model_validate(response.model_dump())
            checks["structured output"] = True
        except ValidationError:
            checks["structured output"] = False
        failures = [f"{name} assertion failed" for name, passed in checks.items() if not passed]
        return EvaluationResult(
            case_id=case.id,
            category=case.category,
            passed=not failures,
            score=round(sum(checks.values()) / len(checks), 4),
            routing_correct=checks["routing"],
            multi_intent_correct=checks["multi-intent"],
            escalation_correct=checks["escalation"],
            blocking_correct=checks["blocking"],
            citations_valid=checks["citations"],
            grounded_answer=checks["grounding"],
            structured_output_valid=checks["structured output"],
            failures=failures,
            latency_ms=round(latency, 3),
            expected={
                "domain": case.expected_domain.value,
                "multi_intent": case.expected_multi_intent,
                "human_review": case.expected_human_review,
                "blocked": case.expected_blocked,
                "source_ids": case.expected_source_ids,
            },
            actual={
                "domain": response.domain.value,
                "multi_intent": routing.get("is_multi_intent"),
                "human_review": response.requires_human_review,
                "blocked": blocked,
                "source_ids": sorted(source_ids),
                "answer": response.answer,
            },
        )

    async def run(self, cases: list[EvaluationCase] | None = None) -> EvaluationSummary:
        selected = cases or load_cases()
        validate_case_sources(selected)
        results = [await self.run_case(case) for case in selected]
        total = len(results)

        def rate(attribute: str) -> float:
            return round(sum(bool(getattr(result, attribute)) for result in results) / total, 4)

        passed = sum(result.passed for result in results)
        return EvaluationSummary(
            total_cases=total,
            passed_cases=passed,
            failed_cases=total - passed,
            pass_rate=round(passed / total, 4),
            routing_accuracy=rate("routing_correct"),
            escalation_accuracy=rate("escalation_correct"),
            blocking_accuracy=rate("blocking_correct"),
            citation_validity_rate=rate("citations_valid"),
            grounded_answer_rate=rate("grounded_answer"),
            average_latency_ms=round(sum(result.latency_ms for result in results) / total, 3),
            results=results,
        )


def write_reports(summary: EvaluationSummary, directory: Path = REPORTS_DIR) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    json_path, md_path = directory / "evaluation-latest.json", directory / "evaluation-latest.md"
    json_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    rows = [
        "# OpenHR Agent Evaluation Report",
        "",
        "> Deterministic Mock Agent; synthetic data only.",
        "",
        f"- Cases: {summary.total_cases}",
        f"- Passed: {summary.passed_cases}",
        f"- Failed: {summary.failed_cases}",
        f"- Pass rate: {summary.pass_rate:.1%}",
        f"- Routing accuracy: {summary.routing_accuracy:.1%}",
        f"- Escalation accuracy: {summary.escalation_accuracy:.1%}",
        f"- Blocking accuracy: {summary.blocking_accuracy:.1%}",
        f"- Citation validity: {summary.citation_validity_rate:.1%}",
        f"- Grounded answer rate: {summary.grounded_answer_rate:.1%}",
        f"- Average latency: {summary.average_latency_ms:.3f} ms",
        "",
        "## Failures",
        "",
    ]
    failed = [result for result in summary.results if not result.passed]
    rows.extend(
        [f"- **{result.case_id}**: {', '.join(result.failures)}" for result in failed]
        or ["No failures."]
    )
    md_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic synthetic OpenHR evaluations")
    parser.add_argument("--reports-dir", type=Path, default=REPORTS_DIR)
    args = parser.parse_args()
    summary = asyncio.run(EvaluationRunner().run())
    json_path, md_path = write_reports(summary, args.reports_dir)
    print(
        f"Evaluation: {summary.passed_cases}/{summary.total_cases} passed ({summary.pass_rate:.1%})"
    )
    print(f"Reports: {json_path} | {md_path}")
    return 0 if summary.failed_cases == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
