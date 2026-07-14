from packages.agent_core.models import HRDomain, HRRequest, RoutingResult
from packages.agent_core.safety import SafetyResult

DOMAIN_KEYWORDS: dict[HRDomain, tuple[str, ...]] = {
    HRDomain.GENERAL_POLICY: (
        "workplace",
        "remote work",
        "working hours",
        "code of conduct",
        "policy",
    ),
    HRDomain.LEAVE_AND_ATTENDANCE: (
        "leave",
        "vacation",
        "absence",
        "attendance",
        "late",
        "parental",
    ),
    HRDomain.BENEFITS: (
        "benefit",
        "health plan",
        "insurance",
        "wellbeing",
        "home office",
        "enrollment",
    ),
    HRDomain.ONBOARDING: ("onboarding", "new hire", "first day", "orientation"),
    HRDomain.LEARNING_AND_DEVELOPMENT: (
        "learning",
        "training",
        "course",
        "development",
        "certification",
    ),
    HRDomain.HR_SERVICE: ("hr ticket", "contact hr", "hr service", "case status"),
}

CONTEXT_PATTERNS = (
    "my balance",
    "leave balance",
    "my request",
    "am i eligible",
    "my enrollment",
    "my case",
)


class ControllerRouter:
    def route(self, request: HRRequest, safety: SafetyResult) -> RoutingResult:
        text = request.message.casefold()
        scores = {
            domain: sum(1 for keyword in keywords if keyword in text)
            for domain, keywords in DOMAIN_KEYWORDS.items()
        }
        detected = [domain for domain, score in scores.items() if score > 0]
        detected.sort(key=lambda domain: (-scores[domain], list(HRDomain).index(domain)))
        primary = detected[0] if detected else HRDomain.UNSUPPORTED
        requires_context = (
            any(pattern in text for pattern in CONTEXT_PATTERNS) and request.employee_id is None
        )
        review = safety.requires_human_review
        if safety.injection_detected:
            primary = HRDomain.UNSUPPORTED
            detected = [HRDomain.UNSUPPORTED]
        confidence = 0.95 if safety.injection_detected or review else (0.88 if detected else 0.2)
        summary = self._summary(primary, detected, requires_context, safety)
        return RoutingResult(
            primary_domain=primary,
            detected_domains=detected or [HRDomain.UNSUPPORTED],
            is_multi_intent=len(detected) > 1,
            confidence=confidence,
            requires_employee_context=requires_context,
            requires_human_review=review,
            reasoning_summary=summary,
        )

    @staticmethod
    def _summary(
        primary: HRDomain,
        detected: list[HRDomain],
        requires_context: bool,
        safety: SafetyResult,
    ) -> str:
        if safety.injection_detected:
            return (
                "Safety rules matched a prompt-injection pattern; instructions were not followed."
            )
        if safety.requires_human_review:
            return "Safety rules matched a high-risk or unauthorized request."
        if not detected:
            return "No supported HR domain keywords were found."
        suffix = " Employee context is missing." if requires_context else ""
        domain_names = ", ".join(domain.value for domain in detected)
        return f"Matched deterministic keywords for: {domain_names}.{suffix}"
