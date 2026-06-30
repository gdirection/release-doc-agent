from app.agents.digester import digest_artifacts
from app.agents.doc_reviewer import review_documentation
from app.agents.release_writer import generate_release_package
from app.data_loader import load_mock_dataset
from app.llm.mock_client import MockLLMClient
from app.retriever import retrieve_docs
from app.validation import validate_release_package


def test_workflow_generates_release_package_with_mock_llm():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved_docs = retrieve_docs(changes, dataset.doc_chunks)
    llm = MockLLMClient()
    package = generate_release_package(llm, changes, retrieved_docs)
    validation_results = validate_release_package(package, changes, retrieved_docs)
    suggestions = review_documentation(llm, package, retrieved_docs)

    assert len(changes) == 3
    assert len(retrieved_docs) == 9
    assert len(package.changelog) == 3
    assert package.internal_release_notes
    assert package.customer_release_notes
    assert all(result.level != "error" for result in validation_results)
    assert suggestions == package.documentation_updates
