from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.digester import digest_artifacts
from app.agents.doc_reviewer import review_documentation
from app.agents.release_writer import generate_release_package
from app.data_loader import load_mock_dataset
from app.evaluation import evaluate_release_package
from app.llm.factory import create_llm_client
from app.retriever import retrieve_docs
from app.schemas import ApprovalRequest, ApprovalResponse
from app.validation import validate_release_package


app = FastAPI(title="Release Documentation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/generate")
def generate_release():
    changes, retrieved_docs, release_package = _run_workflow()
    llm = create_llm_client()
    doc_review = review_documentation(llm, release_package, retrieved_docs)
    validation_results = validate_release_package(release_package, changes, retrieved_docs)

    return {
        "changes": [_model_dump(change) for change in changes],
        "retrieved_docs": [_model_dump(doc) for doc in retrieved_docs],
        "release_package": _model_dump(release_package),
        "doc_review": [_model_dump(update) for update in doc_review],
        "validation_results": [_model_dump(result) for result in validation_results],
    }


@app.post("/api/evaluate")
def evaluate_release():
    changes, retrieved_docs, release_package = _run_workflow()
    report = evaluate_release_package(release_package, changes, retrieved_docs)

    return {
        "release_package": _model_dump(release_package),
        "evaluation": _model_dump(report),
    }


def _run_workflow():
    dataset = load_mock_dataset()
    changes = digest_artifacts(dataset.github_prs, dataset.jira_tickets)
    retrieved_docs = retrieve_docs(changes, dataset.doc_chunks)
    llm = create_llm_client()
    release_package = generate_release_package(llm, changes, retrieved_docs)
    return changes, retrieved_docs, release_package


@app.post("/api/approve", response_model=ApprovalResponse)
def approve_release(request: ApprovalRequest):
    return ApprovalResponse(
        status="approved",
        approved_at=datetime.now(timezone.utc).isoformat(),
        release_package=request.release_package,
    )


def _model_dump(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
