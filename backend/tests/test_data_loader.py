from app.data_loader import load_sources


def test_load_sources_placeholder():
    sources = load_sources()
    assert "github_prs" in sources
    assert "jira_tickets" in sources
    assert "docs" in sources
