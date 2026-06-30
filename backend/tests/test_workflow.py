from app.agents.digester import digest_artifacts
from app.agents.doc_reviewer import review_documentation
from app.agents.release_writer import write_release_package


def test_workflow_placeholders():
    changes = digest_artifacts({})
    package = write_release_package(changes, [])
    suggestions = review_documentation(package, [])

    assert changes == []
    assert package.changelog == []
    assert suggestions == []
