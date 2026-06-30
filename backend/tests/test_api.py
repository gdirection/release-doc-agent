from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_endpoint_returns_full_workflow_output():
    response = client.post("/api/generate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["changes"]
    assert payload["retrieved_docs"]
    assert payload["release_package"]["changelog"]
    assert payload["release_package"]["internal_release_notes"]
    assert payload["release_package"]["customer_release_notes"]
    assert payload["release_package"]["documentation_updates"]
    assert payload["doc_review"]
    assert payload["validation_results"]
    assert all(result["level"] != "error" for result in payload["validation_results"])


def test_approve_endpoint_returns_approved_response():
    generated = client.post("/api/generate").json()
    release_package = generated["release_package"]

    response = client.post("/api/approve", json={"release_package": release_package})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approved"
    assert payload["approved_at"]
    assert payload["release_package"] == release_package
