import pytest

from app.data_loader import load_mock_dataset
from app.schemas import MockDataset


@pytest.fixture
def dataset() -> MockDataset:
    return load_mock_dataset()


def test_dataset_loads_successfully(dataset):
    assert isinstance(dataset, MockDataset)


def test_dataset_has_at_least_one_github_pr(dataset):
    assert dataset.github_prs


def test_dataset_has_at_least_one_jira_ticket(dataset):
    assert dataset.jira_tickets


def test_dataset_has_at_least_one_doc_chunk(dataset):
    assert dataset.doc_chunks


def test_all_pr_linked_tickets_exist_in_jira_tickets(dataset):
    jira_ticket_ids = {ticket.id for ticket in dataset.jira_tickets}

    for pr in dataset.github_prs:
        assert set(pr.linked_tickets).issubset(jira_ticket_ids)


def test_every_jira_ticket_has_at_least_one_linked_pr(dataset):
    linked_ticket_ids = {ticket_id for pr in dataset.github_prs for ticket_id in pr.linked_tickets}

    for ticket in dataset.jira_tickets:
        assert ticket.id in linked_ticket_ids


def test_doc_chunk_ids_are_unique(dataset):
    doc_chunk_ids = [chunk.id for chunk in dataset.doc_chunks]

    assert len(doc_chunk_ids) == len(set(doc_chunk_ids))


def test_doc_chunk_ids_start_with_doc_prefix(dataset):
    assert all(chunk.id.startswith("doc:") for chunk in dataset.doc_chunks)


def test_authentication_docs_include_sso_configuration_chunk(dataset):
    auth_chunks = [chunk for chunk in dataset.doc_chunks if chunk.doc_id == "authentication"]

    assert any(chunk.heading == "SSO Configuration" for chunk in auth_chunks)


def test_billing_docs_exist_as_chunks_but_are_separate_from_auth_docs(dataset):
    billing_chunks = [chunk for chunk in dataset.doc_chunks if chunk.doc_id == "billing"]
    auth_chunks = [chunk for chunk in dataset.doc_chunks if chunk.doc_id == "authentication"]

    assert billing_chunks
    assert auth_chunks
    assert {chunk.doc_id for chunk in billing_chunks} == {"billing"}
    assert {chunk.doc_id for chunk in billing_chunks}.isdisjoint(
        {chunk.doc_id for chunk in auth_chunks}
    )
