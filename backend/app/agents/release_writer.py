import json

from pydantic import ValidationError

from app.llm.factory import create_llm_client
from app.llm.base import LLMClient
from app.schemas import ChangeSummary, ReleasePackage, RetrievedDocChunk


SYSTEM_PROMPT = """You are a release documentation agent.
Use only the provided changes and retrieved documentation evidence.
Do not invent unsupported claims.
Separate internal release notes from customer-facing release notes.
Customer-facing notes should avoid internal implementation details.
Every changelog item and documentation update must include evidence IDs.
Return JSON only."""


def generate_release_package(
    llm: LLMClient,
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> ReleasePackage:
    user_prompt = _build_user_prompt(changes, retrieved_docs)
    raw_package = llm.generate_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=_release_package_shape(),
    )

    try:
        return ReleasePackage(**raw_package)
    except ValidationError as exc:
        raise ValueError("LLM returned an invalid release package") from exc


def write_release_package(
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> ReleasePackage:
    return generate_release_package(create_llm_client(), changes, retrieved_docs)


def _build_user_prompt(
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> str:
    payload = {
        "change_summaries": [_model_to_dict(change) for change in changes],
        "retrieved_doc_chunks": [_model_to_dict(doc) for doc in retrieved_docs],
        "required_output_shape": _release_package_shape(),
    }
    return json.dumps(payload, indent=2)


def _release_package_shape() -> dict:
    return {
        "changelog": [
            {
                "title": "string",
                "summary": "string",
                "evidence_ids": ["string"],
            }
        ],
        "internal_release_notes": "string",
        "customer_release_notes": "string",
        "documentation_updates": [
            {
                "doc_chunk_id": "string",
                "doc_title": "string",
                "section": "string",
                "suggested_change": "string",
                "reason": "string",
                "evidence_ids": ["string"],
            }
        ],
        "evidence": ["string"],
    }


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
