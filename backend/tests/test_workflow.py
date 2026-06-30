from app.agents.digester import digest_artifacts
from app.agents.doc_reviewer import review_documentation
from app.agents.release_writer import write_release_package
from app.data_loader import load_mock_dataset


def test_workflow_placeholders():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    package = write_release_package(changes, [])
    suggestions = review_documentation(package, [])

    assert len(changes) == 3
    assert package.changelog == []
    assert suggestions == []
