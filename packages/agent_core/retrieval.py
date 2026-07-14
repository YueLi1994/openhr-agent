import re
from dataclasses import dataclass
from pathlib import Path

from packages.agent_core.models import HRDomain, RetrievedSource


@dataclass(frozen=True)
class KnowledgeDocument:
    source_id: str
    title: str
    domain: HRDomain
    path: Path
    content: str


SOURCE_MANIFEST: tuple[tuple[str, str, HRDomain], ...] = (
    ("general-workplace-policy", "General Workplace Policy", HRDomain.GENERAL_POLICY),
    ("leave-policy", "Leave Policy", HRDomain.LEAVE_AND_ATTENDANCE),
    ("attendance-policy", "Attendance Policy", HRDomain.LEAVE_AND_ATTENDANCE),
    ("benefits-policy", "Benefits Policy", HRDomain.BENEFITS),
    ("onboarding-guide", "Onboarding Guide", HRDomain.ONBOARDING),
    (
        "learning-development-policy",
        "Learning and Development Policy",
        HRDomain.LEARNING_AND_DEVELOPMENT,
    ),
)

STOP_WORDS = {
    "about",
    "acme",
    "available",
    "company",
    "corporation",
    "employees",
    "fictional",
    "full",
    "policy",
    "synthetic",
    "tell",
    "time",
    "what",
}


class LocalKnowledgeRetriever:
    def __init__(self, knowledge_dir: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.knowledge_dir = knowledge_dir or root / "knowledge" / "fictional_company"
        self.documents = self._load_documents()

    def _load_documents(self) -> list[KnowledgeDocument]:
        documents: list[KnowledgeDocument] = []
        for source_id, title, domain in SOURCE_MANIFEST:
            path = self.knowledge_dir / f"{source_id}.md"
            documents.append(
                KnowledgeDocument(source_id, title, domain, path, path.read_text(encoding="utf-8"))
            )
        return documents

    def list_sources(self) -> list[dict[str, str]]:
        return [
            {"source_id": doc.source_id, "title": doc.title, "domain": doc.domain.value}
            for doc in self.documents
        ]

    def retrieve(
        self, query: str, domains: list[HRDomain], limit: int = 4
    ) -> list[RetrievedSource]:
        terms = {
            term
            for term in re.findall(r"[a-z0-9]+", query.casefold())
            if len(term) > 2 and term not in STOP_WORDS
        }
        results: list[RetrievedSource] = []
        for document in self.documents:
            if document.domain not in domains:
                continue
            paragraphs = [
                part.strip()
                for part in document.content.split("\n\n")
                if part.strip() and not part.startswith(("#", ">"))
            ]
            for paragraph in paragraphs:
                paragraph_terms = {
                    token.rstrip("s") for token in re.findall(r"[a-z0-9]+", paragraph.casefold())
                }
                matches = sum(1 for term in terms if term.rstrip("s") in paragraph_terms)
                if matches == 0:
                    continue
                score = min(1.0, 0.35 + matches / max(len(terms), 1))
                results.append(
                    RetrievedSource(
                        source_id=document.source_id,
                        title=document.title,
                        domain=document.domain,
                        excerpt=paragraph[:500],
                        relevance_score=round(score, 3),
                    )
                )
        results.sort(key=lambda source: (-source.relevance_score, source.source_id))
        deduplicated: dict[str, RetrievedSource] = {}
        for result in results:
            deduplicated.setdefault(result.source_id, result)
        return list(deduplicated.values())[:limit]
