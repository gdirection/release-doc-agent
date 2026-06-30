from app.agents.digester import digest_artifacts
from app.agents.release_writer import generate_release_package
from app.data_loader import load_mock_dataset
from app.llm.mock_client import MockLLMClient
from app.retriever import retrieve_docs
from app.schemas import (
    ChangelogItem,
    DocumentationUpdate,
    ReleasePackage,
)
from app.validation import validate_release_package


def test_valid_mock_output_has_no_error_results():
    package, changes, retrieved_docs = _valid_workflow_output()

    results = validate_release_package(package, changes, retrieved_docs)

    assert results
    assert all(result.level != "error" for result in results)
    assert _codes(results) >= {
        "VALID_EVIDENCE_IDS",
        "JIRA_COVERAGE",
        "VALID_DOCUMENTATION_REFERENCES",
        "CUSTOMER_NOTES_CLEAN",
    }


def test_invalid_evidence_ids_are_caught():
    package, changes, retrieved_docs = _valid_workflow_output()
    package.evidence.append("jira:DOES-NOT-EXIST")

    results = validate_release_package(package, changes, retrieved_docs)

    assert _result_for(results, "INVALID_EVIDENCE_ID").level == "error"


def test_documentation_updates_referencing_non_retrieved_docs_are_caught():
    package, changes, retrieved_docs = _valid_workflow_output()
    package.documentation_updates[0].doc_chunk_id = "doc:missing.md#unknown"

    results = validate_release_package(package, changes, retrieved_docs)

    assert _result_for(results, "INVALID_DOCUMENTATION_REFERENCE").level == "error"


def test_missing_jira_coverage_is_caught():
    package, changes, retrieved_docs = _valid_workflow_output()
    package.changelog = [
        item for item in package.changelog if "jira:AUTH-124" not in item.evidence_ids
    ]
    package.documentation_updates = [
        update
        for update in package.documentation_updates
        if "jira:AUTH-124" not in update.evidence_ids
    ]
    package.evidence = [evidence_id for evidence_id in package.evidence if evidence_id != "jira:AUTH-124"]

    results = validate_release_package(package, changes, retrieved_docs)

    assert _result_for(results, "MISSING_JIRA_COVERAGE").level == "warning"


def test_customer_notes_internal_detail_is_warned():
    package, changes, retrieved_docs = _valid_workflow_output()
    package.customer_release_notes = "Customers can review jira:AUTH-123 for stack trace details."

    results = validate_release_package(package, changes, retrieved_docs)

    assert _result_for(results, "CUSTOMER_NOTES_INTERNAL_DETAIL").level == "warning"


def test_empty_sections_are_reported():
    package, changes, retrieved_docs = _valid_workflow_output()
    package.changelog = []
    package.internal_release_notes = ""
    package.customer_release_notes = ""

    results = validate_release_package(package, changes, retrieved_docs)

    assert _result_for(results, "EMPTY_CHANGELOG").level == "error"
    assert _result_for(results, "EMPTY_INTERNAL_RELEASE_NOTES").level == "warning"
    assert _result_for(results, "EMPTY_CUSTOMER_RELEASE_NOTES").level == "warning"


def test_evidence_ids_on_changelog_and_documentation_updates_are_checked():
    package, changes, retrieved_docs = _valid_workflow_output()
    package.changelog.append(
        ChangelogItem(
            title="Unsupported item",
            summary="Unsupported summary",
            evidence_ids=["github:missing"],
        )
    )
    package.documentation_updates.append(
        DocumentationUpdate(
            doc_chunk_id="doc:authentication.md#sso-configuration",
            doc_title="Authentication Setup Guide",
            section="SSO Configuration",
            suggested_change="Unsupported update",
            reason="Unsupported reason",
            evidence_ids=["doc:missing.md#unknown"],
        )
    )

    results = validate_release_package(package, changes, retrieved_docs)

    result = _result_for(results, "INVALID_EVIDENCE_ID")
    assert result.level == "error"
    assert "github:missing" in result.message
    assert "doc:missing.md#unknown" in result.message


def _valid_workflow_output() -> tuple[ReleasePackage, list, list]:
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved_docs = retrieve_docs(changes, dataset.doc_chunks)
    package = generate_release_package(MockLLMClient(), changes, retrieved_docs)
    return package, changes, retrieved_docs


def _codes(results) -> set[str]:
    return {result.code for result in results}


def _result_for(results, code: str):
    return next(result for result in results if result.code == code)
