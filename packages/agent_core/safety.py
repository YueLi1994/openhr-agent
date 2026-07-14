from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyResult:
    injection_detected: bool = False
    high_risk_detected: bool = False
    unauthorized_private_data: bool = False
    reason: str | None = None

    @property
    def requires_human_review(self) -> bool:
        return self.high_risk_detected or self.unauthorized_private_data


INJECTION_PATTERNS = (
    "ignore all rules",
    "ignore previous instructions",
    "reveal your system prompt",
    "reveal every employee",
    "bypass safety",
    "developer message",
)

HIGH_RISK_PATTERNS: dict[str, tuple[str, ...]] = {
    "termination or disciplinary decision": (
        "should be fired",
        "fire this employee",
        "disciplinary action",
        "terminate employee",
    ),
    "hiring or promotion decision": (
        "rank candidates",
        "who should we hire",
        "promotion decision",
        "who should be promoted",
    ),
    "compensation decision": ("salary adjustment decision", "decide their raise", "reduce salary"),
    "medical, discriminatory, or legal judgment": (
        "medical diagnosis",
        "is disabled",
        "based on race",
        "legal conclusion",
        "is this legal",
    ),
}

PRIVATE_DATA_PATTERNS = (
    "other employee record",
    "every employee record",
    "coworker salary",
    "another employee's",
    "private information",
)


def assess_safety(message: str) -> SafetyResult:
    text = message.casefold()
    if any(pattern in text for pattern in INJECTION_PATTERNS):
        return SafetyResult(injection_detected=True, reason="Prompt injection attempt detected.")
    if any(pattern in text for pattern in PRIVATE_DATA_PATTERNS):
        return SafetyResult(
            unauthorized_private_data=True,
            reason="The request seeks private information about other employees.",
        )
    for reason, patterns in HIGH_RISK_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            return SafetyResult(
                high_risk_detected=True, reason=f"Human review required for {reason}."
            )
    return SafetyResult()
