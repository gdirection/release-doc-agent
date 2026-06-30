import re

from app.schemas import ChangeSummary, DocChunk, RetrievedDocChunk


STOPWORDS = {
    "a",
    "and",
    "are",
    "can",
    "for",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "using",
    "with",
}


def normalize_terms(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if len(token) >= 2 and token not in STOPWORDS}


def score_chunk(change: ChangeSummary, chunk: DocChunk) -> tuple[float, list[str]]:
    query_terms = _change_terms(change)
    title_terms = normalize_terms(chunk.title)
    heading_terms = normalize_terms(chunk.heading)
    content_terms = normalize_terms(chunk.content)
    affected_system_terms = normalize_terms(" ".join(change.affected_systems))

    matched_terms: set[str] = set()
    score = 0.0

    title_matches = query_terms & title_terms
    if title_matches:
        matched_terms.update(title_matches)
        score += 4 * len(title_matches)

    heading_matches = query_terms & heading_terms
    if heading_matches:
        matched_terms.update(heading_matches)
        score += 3 * len(heading_matches)

    affected_system_matches = affected_system_terms & (title_terms | heading_terms)
    if affected_system_matches:
        matched_terms.update(affected_system_matches)
        score += 3 * len(affected_system_matches)

    content_matches = query_terms & content_terms
    if content_matches:
        matched_terms.update(content_matches)
        score += len(content_matches)

    return score, sorted(matched_terms)


def retrieve_docs(
    changes: list[ChangeSummary],
    doc_chunks: list[DocChunk],
    top_k: int = 3,
) -> list[RetrievedDocChunk]:
    retrieved: list[RetrievedDocChunk] = []

    for change in changes:
        scored_chunks = []
        for chunk in doc_chunks:
            score, matched_terms = score_chunk(change, chunk)
            if score > 0:
                scored_chunks.append((score, chunk.id, chunk, matched_terms))

        for score, _, chunk, matched_terms in sorted(scored_chunks, key=lambda item: (-item[0], item[1]))[
            :top_k
        ]:
            retrieved.append(
                RetrievedDocChunk(
                    change_id=change.id,
                    doc_chunk_id=chunk.id,
                    doc_title=chunk.title,
                    path=chunk.path,
                    heading=chunk.heading,
                    content_preview=chunk.content[:240],
                    score=score,
                    matched_terms=matched_terms,
                )
            )

    return retrieved


def _change_terms(change: ChangeSummary) -> set[str]:
    query_text = " ".join(
        [
            change.title,
            change.summary,
            " ".join(change.affected_systems),
            " ".join(change.keywords),
        ]
    )
    return normalize_terms(query_text)
