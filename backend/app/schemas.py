from typing import Literal

from pydantic import BaseModel, Field


class JiraTicket(BaseModel):
    id: str
    title: str
    description: str
    status: Literal["To Do", "In Progress", "Done"]
    type: Literal["Feature", "Bug", "Task"]
    affected_systems: list[str]
    customer_facing: bool
    acceptance_criteria: list[str] = Field(default_factory=list)


class GithubCommit(BaseModel):
    sha: str
    message: str


class GithubPR(BaseModel):
    id: str
    number: int
    title: str
    description: str
    merged_at: str
    linked_tickets: list[str]
    files_changed: list[str]
    commits: list[GithubCommit]


class DocChunk(BaseModel):
    id: str
    doc_id: str
    path: str
    title: str
    heading: str
    content: str


class MockDataset(BaseModel):
    github_prs: list[GithubPR]
    jira_tickets: list[JiraTicket]
    doc_chunks: list[DocChunk]


class ChangeSummary(BaseModel):
    id: str
    title: str
    summary: str
    source_ids: list[str]
    affected_systems: list[str]
    customer_facing: bool
    risk_level: Literal["low", "medium", "high"]
    keywords: list[str] = Field(default_factory=list)


class RetrievedDocChunk(BaseModel):
    change_id: str
    doc_chunk_id: str
    doc_title: str
    path: str
    heading: str
    content_preview: str
    score: float
    matched_terms: list[str]


class ChangelogItem(BaseModel):
    title: str
    summary: str
    evidence_ids: list[str]


class DocumentationUpdate(BaseModel):
    doc_chunk_id: str
    doc_title: str
    section: str
    suggested_change: str
    reason: str
    evidence_ids: list[str]


class ReleasePackage(BaseModel):
    changelog: list[ChangelogItem]
    internal_release_notes: str
    customer_release_notes: str
    documentation_updates: list[DocumentationUpdate]
    evidence: list[str]


class ValidationResult(BaseModel):
    level: Literal["pass", "warning", "error"]
    code: str
    message: str


class MetricResult(BaseModel):
    name: str
    value: float
    detail: str


class EvaluationReport(BaseModel):
    hallucination_rate: float
    jira_coverage: float
    doc_recommendation_precision: float
    doc_recommendation_recall: float
    doc_recommendation_f1: float
    metrics: list[MetricResult]


class ApprovalRequest(BaseModel):
    release_package: ReleasePackage


class ApprovalResponse(BaseModel):
    status: Literal["approved"]
    approved_at: str
    release_package: ReleasePackage
