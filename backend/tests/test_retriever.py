import pytest

from app.agents.digester import digest_artifacts
from app.data_loader import load_mock_dataset
from app.retriever import retrieve_docs


@pytest.fixture
def retrieval_context():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved = retrieve_docs(changes, dataset.doc_chunks)
    return dataset, changes, retrieved


def test_retriever_returns_at_least_one_result(retrieval_context):
    _, _, retrieved = retrieval_context

    assert retrieved


def test_auth_123_okta_sso_retrieves_authentication_sso_docs(retrieval_context):
    dataset, changes, _ = retrieval_context
    change = next(change for change in changes if change.id == "AUTH-123")

    retrieved = retrieve_docs([change], dataset.doc_chunks)
    retrieved_ids = [chunk.doc_chunk_id for chunk in retrieved]

    assert "doc:authentication.md#sso-configuration" in retrieved_ids


def test_enterprise_identity_provider_retrieval_includes_enterprise_onboarding(
    retrieval_context,
):
    dataset, changes, _ = retrieval_context
    change = next(change for change in changes if change.id == "AUTH-123")

    retrieved = retrieve_docs([change], dataset.doc_chunks, top_k=5)

    assert any("enterprise_onboarding.md" in chunk.doc_chunk_id for chunk in retrieved)


def test_auth_125_sso_callback_error_handling_retrieves_troubleshooting_docs(
    retrieval_context,
):
    dataset, changes, _ = retrieval_context
    change = next(change for change in changes if change.id == "AUTH-125")

    retrieved = retrieve_docs([change], dataset.doc_chunks)

    assert any("troubleshooting_login.md" in chunk.doc_chunk_id for chunk in retrieved)


def test_billing_docs_do_not_appear_for_auth_only_changes(retrieval_context):
    _, _, retrieved = retrieval_context

    assert all("billing.md" not in chunk.doc_chunk_id for chunk in retrieved)


def test_every_retrieved_doc_chunk_id_exists_in_dataset(retrieval_context):
    dataset, _, retrieved = retrieval_context
    actual_doc_chunk_ids = {chunk.id for chunk in dataset.doc_chunks}

    assert {chunk.doc_chunk_id for chunk in retrieved}.issubset(actual_doc_chunk_ids)


def test_every_retrieved_result_has_positive_score(retrieval_context):
    _, _, retrieved = retrieval_context

    assert all(chunk.score > 0 for chunk in retrieved)


def test_every_retrieved_result_has_at_least_one_matched_term(retrieval_context):
    _, _, retrieved = retrieval_context

    assert all(chunk.matched_terms for chunk in retrieved)


def test_retriever_is_deterministic():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)

    first = retrieve_docs(changes, dataset.doc_chunks)
    second = retrieve_docs(changes, dataset.doc_chunks)

    assert first == second
