# Release Documentation Agent

MVP scaffold for an automated release documentation agent.

The product flow is:

```text
Locked mock data -> Source Loader -> Artifact Digester -> Document Retriever
-> Release Writer Agent -> Documentation Reviewer Agent -> Validation Engine
-> Review UI -> Approval
```

## Local Setup

### Backend

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload
```

The backend defaults to the mock LLM provider. Copy `.env.example` to `.env` only if
you want to configure environment variables.

Run backend tests with:

```bash
cd backend
uv run pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Status

This repository currently contains the initial skeleton only. Business logic,
workflow orchestration, and UI behavior will be implemented in later steps.
