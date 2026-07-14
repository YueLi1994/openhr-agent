# Local knowledge retrieval

The phase-2 retriever loads six UTF-8 Markdown documents from `knowledge/fictional_company`. A manifest assigns a stable source ID, title, and domain to every document.

Retrieval first filters documents to routed domains. It tokenizes the question and policy paragraphs, removes a small deterministic stop-word set, applies simple plural normalization, and scores exact token overlap. Results are deduplicated by source ID and sorted by relevance.

Answers copy retrieved excerpts and append `[source-id]` citations. Returned citations must exist in the source catalog. If no paragraph matches, the workflow states that information is unavailable and escalates instead of generating unsupported content. This is deliberately not semantic or vector retrieval.
