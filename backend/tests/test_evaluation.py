from app.agents.digester import digest_artifacts
from app.agents.release_writer import generate_release_package
from app.data_loader import load_mock_dataset
from app.evaluation import evaluate_release_package, load_expected_doc_chunk_ids
from app.llm.mock_client import MockLLMClient
from app.retriever import retrieve_docs
from app.schemas import ChangelogItem, DocumentationUpdate


def _workflow_output():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved_docs = retrieve_docs(changes, dataset.doc_chunks)
    package = generate_release_package(MockLLMClient(), changes, retrieved_docs)
    return package, changes, retrieved_docs


def test_locked_mock_output_is_fully_grounded_and_covered():
    package, changes, retrieved_docs = _workflow_output()

    report = evaluate_release_package(package, changes, retrieved_docs)

    assert report.hallucination_rate == 0.0
    assert report.jira_coverage == 1.0
    assert report.doc_recommendation_precision == 1.0
    assert report.doc_recommendation_recall == 1.0
    assert report.doc_recommendation_f1 == 1.0
    assert len(report.metrics) == 5


def test_ungrounded_changelog_item_raises_hallucination_rate():
    package, changes, retrieved_docs = _workflow_output()
    package.changelog.append(
        ChangelogItem(
            title="Fabricated feature",
            summary="Not supported by any source.",
            evidence_ids=["github:pr-999"],
        )
    )

    report = evaluate_release_package(package, changes, retrieved_docs)

    assert report.hallucination_rate > 0.0


def test_missing_jira_reference_lowers_coverage():
    package, changes, retrieved_docs = _workflow_output()
    package.changelog = [
        item for item in package.changelog if "jira:AUTH-124" not in item.evidence_ids
    ]
    package.documentation_updates = [
        update for update in package.documentation_updates if "jira:AUTH-124" not in update.evidence_ids
    ]
    package.evidence = [evidence_id for evidence_id in package.evidence if evidence_id != "jira:AUTH-124"]

    report = evaluate_release_package(package, changes, retrieved_docs)

    assert report.jira_coverage < 1.0


def test_missing_expected_doc_lowers_recall():
    package, changes, retrieved_docs = _workflow_output()
    expected = load_expected_doc_chunk_ids()
    package.documentation_updates = package.documentation_updates[:1]

    report = evaluate_release_package(package, changes, retrieved_docs, expected_doc_chunk_ids=expected)

    assert report.doc_recommendation_recall < 1.0
    assert report.doc_recommendation_precision == 1.0


def test_unexpected_doc_suggestion_lowers_precision():
    package, changes, retrieved_docs = _workflow_output()
    package.documentation_updates.append(
        DocumentationUpdate(
            doc_chunk_id="doc:billing.md#overview",
            doc_title="Billing Guide",
            section="Overview",
            suggested_change="Irrelevant change.",
            reason="Not part of this release.",
            evidence_ids=["jira:AUTH-123"],
        )
    )

    report = evaluate_release_package(package, changes, retrieved_docs)

    assert report.doc_recommendation_precision < 1.0
    assert report.doc_recommendation_recall == 1.0
