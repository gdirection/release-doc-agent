from app.llm.base import LLMClient
from app.schemas import DocumentationUpdate, ReleasePackage, RetrievedDocChunk


def review_documentation(
    llm: LLMClient,
    release_package: ReleasePackage,
    retrieved_docs: list[RetrievedDocChunk],
) -> list[DocumentationUpdate]:
    return release_package.documentation_updates
