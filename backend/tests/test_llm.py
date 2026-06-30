import pytest

from app.llm.factory import create_llm_client
from app.llm.mock_client import MockLLMClient
from app.schemas import ReleasePackage


def test_mock_llm_returns_release_package_shaped_json():
    client = MockLLMClient()

    result = client.generate_json("system", "user")
    package = ReleasePackage(**result)

    assert len(package.changelog) == 3
    assert package.changelog[0].title == "Added Okta SSO support"
    assert "jira:AUTH-123" in package.changelog[0].evidence_ids
    assert "github:pr-42" in package.evidence
    assert "doc:authentication.md#sso-configuration" in package.evidence


def test_mock_customer_release_notes_do_not_include_internal_ids():
    result = MockLLMClient().generate_json("system", "user")
    customer_notes = result["customer_release_notes"]

    assert "github:" not in customer_notes
    assert "jira:" not in customer_notes
    assert "PR" not in customer_notes
    assert "stack trace" not in customer_notes.lower()


def test_mock_documentation_updates_include_doc_evidence_ids():
    result = MockLLMClient().generate_json("system", "user")

    for update in result["documentation_updates"]:
        assert update["doc_chunk_id"] in update["evidence_ids"]


def test_create_llm_client_defaults_to_mock(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    client = create_llm_client()

    assert isinstance(client, MockLLMClient)


def test_create_llm_client_uses_mock_for_unknown_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unknown")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    client = create_llm_client()

    assert isinstance(client, MockLLMClient)


def test_create_llm_client_requires_key_for_gemini(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is required"):
        create_llm_client()
