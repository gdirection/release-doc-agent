import json
from pathlib import Path

from app.schemas import ChangeSummary, EvaluationReport, MetricResult, ReleasePackage, RetrievedDocChunk
from app.validation import _known_evidence_ids, _used_evidence_ids


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_expected_doc_chunk_ids() -> set[str]:
    path = DATA_DIR / "eval_expectations.json"
    with path.open() as file:
        data = json.load(file)
    return set(data.get("expected_doc_chunk_ids", []))


def evaluate_release_package(
    release_package: ReleasePackage,
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
    expected_doc_chunk_ids: set[str] | None = None,
) -> EvaluationReport:
    if expected_doc_chunk_ids is None:
        expected_doc_chunk_ids = load_expected_doc_chunk_ids()

    hallucination_rate, hallucination_detail = _hallucination_rate(release_package, changes, retrieved_docs)
    jira_coverage, coverage_detail = _jira_coverage(release_package, changes)
    precision, recall, f1, doc_detail = _doc_recommendation_accuracy(release_package, expected_doc_chunk_ids)

    metrics = [
        MetricResult(name="Hallucination rate", value=hallucination_rate, detail=hallucination_detail),
        MetricResult(name="Jira coverage", value=jira_coverage, detail=coverage_detail),
        MetricResult(name="Doc recommendation precision", value=precision, detail=doc_detail),
        MetricResult(name="Doc recommendation recall", value=recall, detail=doc_detail),
        MetricResult(name="Doc recommendation F1", value=f1, detail=doc_detail),
    ]

    return EvaluationReport(
        hallucination_rate=hallucination_rate,
        jira_coverage=jira_coverage,
        doc_recommendation_precision=precision,
        doc_recommendation_recall=recall,
        doc_recommendation_f1=f1,
        metrics=metrics,
    )


def _hallucination_rate(
    release_package: ReleasePackage,
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> tuple[float, str]:
    known = _known_evidence_ids(changes, retrieved_docs)

    generated_items: list[list[str]] = [item.evidence_ids for item in release_package.changelog]
    generated_items += [update.evidence_ids for update in release_package.documentation_updates]

    total = len(generated_items)
    if total == 0:
        return 0.0, "No generated items to evaluate."

    ungrounded = sum(
        1
        for evidence_ids in generated_items
        if not evidence_ids or any(evidence_id not in known for evidence_id in evidence_ids)
    )

    rate = ungrounded / total
    return rate, f"{ungrounded}/{total} generated items reference missing or absent evidence."


def _jira_coverage(
    release_package: ReleasePackage,
    changes: list[ChangeSummary],
) -> tuple[float, str]:
    expected = {
        source_id
        for change in changes
        for source_id in change.source_ids
        if source_id.startswith("jira:")
    }
    if not expected:
        return 1.0, "No Jira tickets to cover."

    covered = expected & _used_evidence_ids(release_package)
    coverage = len(covered) / len(expected)
    return coverage, f"{len(covered)}/{len(expected)} Jira tickets referenced in the release package."


def _doc_recommendation_accuracy(
    release_package: ReleasePackage,
    expected_doc_chunk_ids: set[str],
) -> tuple[float, float, float, str]:
    predicted = {update.doc_chunk_id for update in release_package.documentation_updates}
    golden = set(expected_doc_chunk_ids)
    true_positives = predicted & golden

    if predicted:
        precision = len(true_positives) / len(predicted)
    else:
        precision = 1.0 if not golden else 0.0

    if golden:
        recall = len(true_positives) / len(golden)
    else:
        recall = 1.0

    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    detail = f"{len(true_positives)} correct of {len(predicted)} suggested vs {len(golden)} expected docs."
    return precision, recall, f1, detail
