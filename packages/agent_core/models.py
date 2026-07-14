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
