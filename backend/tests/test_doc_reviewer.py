from app.agents.digester import digest_artifacts
from app.agents.doc_reviewer import review_documentation
from app.agents.release_writer import generate_release_package
from app.data_loader import load_mock_dataset
from app.llm.mock_client import MockLLMClient
from app.retriever import retrieve_docs


def test_review_documentation_returns_release_package_documentation_updates():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved_docs = retrieve_docs(changes, dataset.doc_chunks)
    llm = MockLLMClient()
    package = generate_release_package(llm, changes, retrieved_docs)

    updates = review_documentation(llm, package, retrieved_docs)

    assert updates == package.documentation_updates
    assert len(updates) == 3
