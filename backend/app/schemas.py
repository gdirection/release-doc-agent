from pydantic import BaseModel, Field


class ReleasePackage(BaseModel):
    changelog: list[str] = Field(default_factory=list)
    internal_release_notes: str = ""
    customer_release_notes: str = ""
    documentation_updates: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
