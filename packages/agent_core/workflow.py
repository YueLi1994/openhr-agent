from time import perf_counter

from packages.agent_core.models import AgentResponse, HRDomain, HRRequest, RetrievedSource
from packages.agent_core.retrieval import LocalKnowledgeRetriever
from packages.agent_core.router import ControllerRouter
from packages.agent_core.safety import SafetyResult, assess_safety


class HRAgentWorkflow:
    def __init__(self) -> None:
        self.router = ControllerRouter()
        self.retriever = LocalKnowledgeRetriever()

    async def run(self, request: HRRequest) -> AgentResponse:
        started = perf_counter()
        safety = assess_safety(request.message)
        routing = self.router.route(request, safety)
        steps = ["input_validation", "safety_check", "domain_routing"]

        if safety.injection_detected:
            return self._safe_response(
                routing.primary_domain,
                "I cannot follow instructions that attempt to override safety rules "
                "or reveal private records.",
                safety,
                routing,
                steps + ["request_blocked"],
                started,
            )
        if safety.requires_human_review:
            return self._safe_response(
                routing.primary_domain,
                "I cannot make or recommend this employment decision. I can create a neutral "
                "summary for an authorized HR professional.",
                safety,
                routing,
                steps + ["human_escalation"],
                started,
            )
        if routing.requires_employee_context:
            return self._response(
                answer=(
                    "I need a synthetic employee ID before I can answer this "
                    "employee-specific question."
                ),
                domain=routing.primary_domain,
                sources=[],
                confidence=0.45,
                missing=["employee_id"],
                review=False,
                reason=None,
                routing=routing,
                steps=steps + ["context_check"],
                started=started,
            )
        if routing.primary_domain is HRDomain.UNSUPPORTED:
            return self._response(
                answer=(
                    "I could not find a supported Acme Corporation policy for this question. "
                    "I will not invent an answer; please contact an HR professional."
                ),
                domain=HRDomain.UNSUPPORTED,
                sources=[],
                confidence=0.2,
                missing=["A relevant fictional Acme Corporation policy"],
                review=True,
                reason="No supported domain or grounded policy source was found.",
                routing=routing,
                steps=steps + ["no_supported_domain", "human_escalation"],
                started=started,
            )

        domains: list[HRDomain] = [
            domain for domain in routing.detected_domains if domain is not HRDomain.UNSUPPORTED
        ]
        sources = self.retriever.retrieve(request.message, domains)
        steps.extend(
            [
                "multi_intent_split" if routing.is_multi_intent else "single_intent",
                "knowledge_retrieval",
            ]
        )
        if not sources:
            return self._response(
                answer=(
                    "The available fictional Acme Corporation policies do not contain this "
                    "information. I will not invent an answer; please contact HR."
                ),
                domain=routing.primary_domain,
                sources=[],
                confidence=0.3,
                missing=["Grounded policy information matching the question"],
                review=True,
                reason="No relevant knowledge source was found.",
                routing=routing,
                steps=steps + ["grounding_failure", "human_escalation"],
                started=started,
            )

        answer = self._grounded_answer(sources)
        steps.extend(
            ["answer_generation", "citation_validation", "risk_check", "structured_output"]
        )
        return self._response(
            answer=answer,
            domain=routing.primary_domain,
            sources=sources,
            confidence=round(
                min(routing.confidence, max(source.relevance_score for source in sources)), 2
            ),
            missing=[],
            review=False,
            reason=None,
            routing=routing,
            steps=steps,
            started=started,
        )

    @staticmethod
    def _grounded_answer(sources: list[RetrievedSource]) -> str:
        statements = [f"{source.excerpt} [{source.source_id}]" for source in sources]
        return "Based on the fictional Acme Corporation policies:\n\n" + "\n\n".join(statements)

    def _safe_response(
        self,
        domain: HRDomain,
        answer: str,
        safety: SafetyResult,
        routing: object,
        steps: list[str],
        started: float,
    ) -> AgentResponse:
        return self._response(
            answer,
            domain,
            [],
            0.95,
            [],
            safety.requires_human_review,
            safety.reason,
            routing,
            steps,
            started,
        )

    @staticmethod
    def _response(
        answer: str,
        domain: HRDomain,
        sources: list[RetrievedSource],
        confidence: float,
        missing: list[str],
        review: bool,
        reason: str | None,
        routing: object,
        steps: list[str],
        started: float,
    ) -> AgentResponse:
        from packages.agent_core.models import RoutingResult

        if not isinstance(routing, RoutingResult):
            raise TypeError("routing must be a RoutingResult")
        return AgentResponse(
            answer=answer,
            domain=domain,
            sources=sources,
            confidence=confidence,
            missing_information=missing,
            requires_human_review=review,
            escalation_reason=reason,
            structured_data={
                "routing": routing.model_dump(mode="json"),
                "workflow_steps": steps,
                "execution_ms": round((perf_counter() - started) * 1000, 3),
                "provider": "mock-v2",
            },
        )
