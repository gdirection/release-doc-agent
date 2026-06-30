from app.agents.digester import digest_artifacts
from app.data_loader import load_mock_dataset


def test_digest_artifacts_creates_one_change_summary_per_jira_ticket():
    dataset = load_mock_dataset()

    summaries = digest_artifacts(dataset.github_prs, dataset.jira_tickets)

    assert [summary.id for summary in summaries] == ["AUTH-123", "AUTH-124", "AUTH-125"]


def test_digest_artifacts_is_deterministic():
    dataset = load_mock_dataset()

    first = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    second = digest_artifacts(dataset.github_prs, dataset.jira_tickets)

    assert first == second


def test_auth_123_creates_customer_facing_okta_sso_change():
    dataset = load_mock_dataset()
    summaries = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    summary = next(summary for summary in summaries if summary.id == "AUTH-123")

    assert summary.title == "Add Okta SSO support"
    assert summary.customer_facing is True
    assert summary.risk_level == "medium"
    assert summary.source_ids == ["jira:AUTH-123", "github:pr-41", "github:pr-42"]
    assert "okta" in summary.keywords
    assert "sso" in summary.keywords


def test_auth_124_creates_internal_audit_logging_change():
    dataset = load_mock_dataset()
    summaries = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    summary = next(summary for summary in summaries if summary.id == "AUTH-124")

    assert summary.title == "Add audit logging for SSO login events"
    assert summary.customer_facing is False
    assert summary.risk_level == "low"
    assert summary.source_ids == ["jira:AUTH-124", "github:pr-43"]
    assert "audit" in summary.keywords
    assert "logging" in summary.keywords


def test_auth_125_creates_customer_facing_sso_error_handling_change():
    dataset = load_mock_dataset()
    summaries = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    summary = next(summary for summary in summaries if summary.id == "AUTH-125")

    assert summary.title == "Improve SSO callback error handling"
    assert summary.customer_facing is True
    assert summary.risk_level == "medium"
    assert summary.source_ids == ["jira:AUTH-125", "github:pr-42", "github:pr-44"]
    assert "sso" in summary.keywords
    assert "callback" in summary.keywords


def test_every_source_id_is_valid():
    dataset = load_mock_dataset()
    summaries = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    valid_source_ids = {f"jira:{ticket.id}" for ticket in dataset.jira_tickets}
    valid_source_ids.update(pr.id for pr in dataset.github_prs)

    for summary in summaries:
        assert set(summary.source_ids).issubset(valid_source_ids)


def test_keywords_are_lowercase_deduplicated_and_stopwords_removed():
    dataset = load_mock_dataset()
    summaries = digest_artifacts(dataset.github_prs, dataset.jira_tickets)

    for summary in summaries:
        assert summary.keywords == list(dict.fromkeys(summary.keywords))
        assert all(keyword == keyword.lower() for keyword in summary.keywords)
        assert "and" not in summary.keywords
        assert "the" not in summary.keywords
