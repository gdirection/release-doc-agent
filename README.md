# Automated Release Documentation Agent

This is an MVP that turns locked mock GitHub, Jira, and documentation artifacts
into a reviewable release package. It generates a changelog, internal release
notes, customer-facing release notes, and documentation update suggestions.

[Design.md](Design.md) is the design document and source of the architecture
decisions.

## Workflow

```text
Ingest -> Digest -> Retrieve -> Generate -> Validate -> Review / Approve
```

## Stack

- Python + FastAPI backend
- Pydantic schemas
- pytest tests
- Mock LLM by default
- Optional Gemini adapter
- React + Vite frontend

## Setup

### Backend

Recommended `uv` workflow:

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8000
```

Equivalent `pip` workflow:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The backend must also be running on:

```text
http://localhost:8000
```

## Tests

Recommended `uv` workflow:

```bash
cd backend
uv run pytest
```

Equivalent active-venv workflow:

```bash
cd backend
pytest
```

Frontend build check:

```bash
cd frontend
npm run build
```

## LLM Modes

Default mock mode:

```env
LLM_PROVIDER=mock
```

Optional Gemini mode:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

Mock mode is deterministic and requires no external credentials. Gemini mode is
optional; the adapter is isolated behind the same LLM client interface.

## Implementation Notes

- Mock data is a locked golden fixture.
- The document retriever is deterministic local Markdown retrieval.
- LLM output is parsed into structured Pydantic models.
- Validation checks evidence references, Jira coverage, documentation references,
  customer-facing notes, and required (non-empty) sections.
- The UI supports review, editing internal/customer notes, and approval.

## Known Limitations

- No real GitHub or Jira integration.
- No database persistence.
- No authentication.
- No vector database.
- No multi-user approval workflow.
- Evaluation is lightweight and validation-based, not a full hallucination
  benchmark.
