import pytest

from app.agents.digester import digest_artifacts
from app.agents.release_writer import generate_release_package
from app.data_loader import load_mock_dataset
from app.llm.mock_client import MockLLMClient
from app.retriever import retrieve_docs
from app.schemas import ReleasePackage


def test_generate_release_package_with_mock_llm_returns_release_package():
    changes, retrieved_docs = _workflow_inputs()

    package = generate_release_package(MockLLMClient(), changes, retrieved_docs)

    assert isinstance(package, ReleasePackage)
    assert len(package.changelog) == 3
    assert package.internal_release_notes
    assert package.customer_release_notes
    assert len(package.documentation_updates) == 3
    assert package.evidence


def test_generate_release_package_customer_notes_avoid_internal_details():
    changes, retrieved_docs = _workflow_inputs()

    package = generate_release_package(MockLLMClient(), changes, retrieved_docs)

    assert "github:" not in package.customer_release_notes
    assert "jira:" not in package.customer_release_notes
    assert "auth/" not in package.customer_release_notes
    assert "stack trace" not in package.customer_release_notes.lower()


def test_generate_release_package_raises_value_error_for_invalid_llm_output():
    changes, retrieved_docs = _workflow_inputs()

    with pytest.raises(ValueError, match="invalid release package"):
        generate_release_package(BadLLMClient(), changes, retrieved_docs)


class BadLLMClient:
    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict | None = None) -> dict:
        return {"changelog": "not a valid changelog"}


def _workflow_inputs():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved_docs = retrieve_docs(changes, dataset.doc_chunks)
    return changes, retrieved_docs
