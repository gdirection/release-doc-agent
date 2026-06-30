import pytest

from app.data_loader import (
    load_mock_dataset,
    load_sources,
    slugify,
    validate_cross_source_consistency,
)
from app.schemas import DocChunk, GithubPR, JiraTicket, MockDataset


def test_load_mock_dataset_returns_valid_dataset():
    dataset = load_mock_dataset()

    assert isinstance(dataset, MockDataset)
    assert len(dataset.github_prs) == 4
    assert len(dataset.jira_tickets) == 3
    assert len(dataset.doc_chunks) == 12


def test_load_sources_compatibility_wrapper():
    sources = load_sources()

    assert "github_prs" in sources
    assert "jira_tickets" in sources
    assert "docs" in sources
    assert len(sources["docs"]) == 12


def test_markdown_chunks_have_stable_ids_and_paths():
    dataset = load_mock_dataset()
    chunk_ids = {chunk.id for chunk in dataset.doc_chunks}

    assert "doc:authentication.md#sso-configuration" in chunk_ids
    assert "doc:enterprise_onboarding.md#identity-provider-setup" in chunk_ids
    assert "doc:troubleshooting_login.md#sso-login-failures" in chunk_ids

    sso_chunk = next(
        chunk for chunk in dataset.doc_chunks if chunk.id == "doc:authentication.md#sso-configuration"
    )
    assert sso_chunk.path == "data/docs/authentication.md"
    assert sso_chunk.title == "Authentication Setup Guide"
    assert "SAML-based single sign-on" in sso_chunk.content


def test_slugify_is_deterministic():
    assert slugify("SSO Configuration") == "sso-configuration"
    assert slugify(" Identity Provider Setup ") == "identity-provider-setup"
    assert slugify("Expired Login Sessions!") == "expired-login-sessions"


def test_validate_cross_source_consistency_rejects_unknown_linked_ticket():
    github_prs = [_github_pr(linked_tickets=["AUTH-999"])]
    jira_tickets = [_jira_ticket("AUTH-123")]

    with pytest.raises(ValueError, match="unknown Jira tickets: AUTH-999"):
        validate_cross_source_consistency(github_prs, jira_tickets, [_doc_chunk()])


def test_validate_cross_source_consistency_rejects_unlinked_jira_ticket():
    github_prs = [_github_pr(linked_tickets=["AUTH-123"])]
    jira_tickets = [_jira_ticket("AUTH-123"), _jira_ticket("AUTH-124")]

    with pytest.raises(ValueError, match="not linked by any PR: AUTH-124"):
        validate_cross_source_consistency(github_prs, jira_tickets, [_doc_chunk()])


def test_validate_cross_source_consistency_rejects_duplicate_ids():
    github_prs = [_github_pr(id="github:pr-1"), _github_pr(id="github:pr-1")]
    jira_tickets = [_jira_ticket("AUTH-123")]

    with pytest.raises(ValueError, match="Duplicate GitHub PR IDs: github:pr-1"):
        validate_cross_source_consistency(github_prs, jira_tickets, [_doc_chunk()])


def _github_pr(id: str = "github:pr-1", linked_tickets: list[str] | None = None) -> GithubPR:
    return GithubPR(
        id=id,
        number=1,
        title="Test PR",
        description="Test PR description",
        merged_at="2026-06-01T10:15:00Z",
        linked_tickets=linked_tickets or ["AUTH-123"],
        files_changed=["auth/test.py"],
        commits=[],
    )


def _jira_ticket(id: str) -> JiraTicket:
    return JiraTicket(
        id=id,
        title="Test ticket",
        description="Test ticket description",
        status="Done",
        type="Feature",
        affected_systems=["Authentication Service"],
        customer_facing=True,
    )


def _doc_chunk(id: str = "doc:test.md#section") -> DocChunk:
    return DocChunk(
        id=id,
        doc_id="test",
        path="data/docs/test.md",
        title="Test Doc",
        heading="Section",
        content="Test content",
    )
