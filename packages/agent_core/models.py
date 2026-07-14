from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class HRDomain(StrEnum):
    GENERAL_POLICY = "general_policy"
    LEAVE_AND_ATTENDANCE = "leave_and_attendance"
    BENEFITS = "benefits"
    ONBOARDING = "onboarding"
    LEARNING_AND_DEVELOPMENT = "learning_and_development"
    HR_SERVICE = "hr_service"
    UNSUPPORTED = "unsupported"


class HRRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)
    employee_id: str | None = Field(default=None, pattern=r"^SYN-[0-9]{3}$")
    locale: str = Field(default="en-US", min_length=2, max_length=20)
    conversation_id: str | None = Field(default=None, max_length=100)

    @field_validator("message")
    @classmethod
    def message_must_have_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must contain non-whitespace characters")
        return value


class RoutingResult(StrictModel):
    primary_domain: HRDomain
    detected_domains: list[HRDomain]
    is_multi_intent: bool
    confidence: float = Field(ge=0, le=1)
    requires_employee_context: bool
    requires_human_review: bool
    reasoning_summary: str


class RetrievedSource(StrictModel):
    source_id: str
    title: str
    domain: HRDomain
    excerpt: str
    relevance_score: float = Field(ge=0, le=1)


class AgentResponse(StrictModel):
    answer: str
    domain: HRDomain
    sources: list[RetrievedSource]
    confidence: float = Field(ge=0, le=1)
    missing_information: list[str]
    requires_human_review: bool
    escalation_reason: str | None
    structured_data: dict[str, Any]


class EvaluationCase(StrictModel):
    id: str = Field(pattern=r"^EVAL-[0-9]{3}$")
    category: str
    input_message: str = Field(min_length=1, max_length=4000)
    employee_context: str | None = Field(default=None, pattern=r"^SYN-[0-9]{3}$")
    expected_domain: HRDomain
    expected_multi_intent: bool
    expected_human_review: bool
    expected_blocked: bool
    expected_source_ids: list[str]
    forbidden_claims: list[str]
    notes: str


class EvaluationResult(StrictModel):
    case_id: str
    category: str
    passed: bool
    score: float = Field(ge=0, le=1)
    routing_correct: bool
    multi_intent_correct: bool
    escalation_correct: bool
    blocking_correct: bool
    citations_valid: bool
    grounded_answer: bool
    structured_output_valid: bool
    failures: list[str]
    latency_ms: float = Field(ge=0)
    expected: dict[str, Any]
    actual: dict[str, Any]


class EvaluationSummary(StrictModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    routing_accuracy: float
    escalation_accuracy: float
    blocking_accuracy: float
    citation_validity_rate: float
    grounded_answer_rate: float
    average_latency_ms: float
    results: list[EvaluationResult]
