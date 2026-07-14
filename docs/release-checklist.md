# v0.1.0 release checklist

## Code and verification

- [ ] Branch reviewed; working tree contains only intended public changes.
- [ ] Frontend install, lint, typecheck, tests, and production build pass.
- [ ] Backend Ruff, mypy, and pytest pass.
- [ ] All deterministic cases pass; JSON and Markdown reports generate.
- [ ] Secret, personal-data, real-company, and tracked-artifact scans pass.
- [ ] Apache-2.0 `LICENSE` is unchanged.

## Public release review

- [ ] README files, changelog, architecture, evaluation, safety, demo, roadmap, and limitations are current.
- [ ] Fixtures are synthetic Acme Corporation content only.
- [ ] No production-readiness or employment-decision claims.
- [ ] Maintainer manually creates tag/release only after review (not performed by this task).

## Suggested release

**Title:** OpenHR Agent v0.1.0 — Deterministic Mock Agent and Evaluation Suite

**Body:** This first public reference release includes the API-key-free deterministic Agent workflow, fictional Acme Corporation policy retrieval with citations, safety and human-review boundaries, React Agent Demo, and a 32-case synthetic evaluation suite available through the Dashboard, API, CLI, and keyless CI. All data and policies are synthetic. This educational project is not a production HR system and does not provide legal, HR, or employment-decision advice.

**Known limitations:** English phrase rules, lexical retrieval, in-memory evaluation state, no authentication or persistence, no real-model integration, and no production privacy or regulatory validation.

**Topics:** `ai-agents`, `hr-tech`, `fastapi`, `react`, `typescript`, `python`, `rag`, `evaluation`, `synthetic-data`, `responsible-ai`.

**First issues:** expand adversarial safety cases; add accessibility audit; add Chinese evaluation fixtures; version fictional policies; document reference authorization; add evaluation trend comparison without production claims.
