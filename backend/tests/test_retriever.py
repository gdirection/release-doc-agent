from app.agents.digester import digest_artifacts
from app.data_loader import load_mock_dataset
from app.retriever import normalize_terms, retrieve_docs, score_chunk


def test_normalize_terms_lowercases_tokenizes_and_removes_stopwords():
    terms = normalize_terms("Using the SSO Configuration in Authentication!")

    assert terms == {"sso", "configuration", "authentication"}


def test_score_chunk_matches_title_heading_and_content():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    change = next(change for change in changes if change.id == "AUTH-123")
    chunk = next(chunk for chunk in dataset.doc_chunks if chunk.id == "doc:authentication.md#sso-configuration")

    score, matched_terms = score_chunk(change, chunk)

    assert score > 0
    assert "sso" in matched_terms
    assert "authentication" in matched_terms


def test_retrieve_docs_is_deterministic():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)

    first = retrieve_docs(changes, dataset.doc_chunks)
    second = retrieve_docs(changes, dataset.doc_chunks)

    assert first == second


def test_okta_sso_change_retrieves_authentication_sso_docs():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    change = next(change for change in changes if change.id == "AUTH-123")

    retrieved = retrieve_docs([change], dataset.doc_chunks)
    retrieved_ids = [chunk.doc_chunk_id for chunk in retrieved]

    assert "doc:authentication.md#sso-configuration" in retrieved_ids


def test_enterprise_sso_change_retrieves_enterprise_identity_provider_docs():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    change = next(change for change in changes if change.id == "AUTH-123")

    retrieved = retrieve_docs([change], dataset.doc_chunks, top_k=5)
    retrieved_ids = [chunk.doc_chunk_id for chunk in retrieved]

    assert "doc:enterprise_onboarding.md#identity-provider-setup" in retrieved_ids


def test_sso_error_handling_retrieves_troubleshooting_sso_login_docs():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    change = next(change for change in changes if change.id == "AUTH-125")

    retrieved = retrieve_docs([change], dataset.doc_chunks)
    retrieved_ids = [chunk.doc_chunk_id for chunk in retrieved]

    assert "doc:troubleshooting_login.md#sso-login-failures" in retrieved_ids


def test_auth_only_changes_do_not_retrieve_billing_docs_in_top_results():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)

    retrieved = retrieve_docs(changes, dataset.doc_chunks)

    assert all("billing.md" not in chunk.doc_chunk_id for chunk in retrieved)


def test_retrieved_doc_chunk_ids_match_actual_doc_chunk_ids():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    actual_doc_chunk_ids = {chunk.id for chunk in dataset.doc_chunks}

    retrieved = retrieve_docs(changes, dataset.doc_chunks)

    assert retrieved
    assert {chunk.doc_chunk_id for chunk in retrieved}.issubset(actual_doc_chunk_ids)
