import json
import re
from pathlib import Path

from app.schemas import DocChunk, GithubPR, JiraTicket, MockDataset


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return normalized.strip("-")


def load_github_prs(path: Path) -> list[GithubPR]:
    with path.open() as file:
        records = json.load(file)
    return [GithubPR(**record) for record in records]


def load_jira_tickets(path: Path) -> list[JiraTicket]:
    with path.open() as file:
        records = json.load(file)
    return [JiraTicket(**record) for record in records]


def load_markdown_docs(docs_dir: Path) -> list[DocChunk]:
    chunks: list[DocChunk] = []

    for doc_path in sorted(docs_dir.glob("*.md")):
        doc_id = doc_path.stem
        relative_path = doc_path.relative_to(DATA_DIR.parent).as_posix()
        title = ""
        current_heading = ""
        current_content: list[str] = []

        def append_current_chunk() -> None:
            if not current_heading:
                return
            chunks.append(
                DocChunk(
                    id=f"doc:{doc_path.name}#{slugify(current_heading)}",
                    doc_id=doc_id,
                    path=relative_path,
                    title=title,
                    heading=current_heading,
                    content="\n".join(current_content).strip(),
                )
            )

        for line in doc_path.read_text().splitlines():
            if line.startswith("# "):
                title = line.removeprefix("# ").strip()
                continue

            if line.startswith("## "):
                append_current_chunk()
                current_heading = line.removeprefix("## ").strip()
                current_content = []
                continue

            if current_heading:
                current_content.append(line)

        append_current_chunk()

    return chunks


def validate_cross_source_consistency(
    github_prs: list[GithubPR],
    jira_tickets: list[JiraTicket],
    doc_chunks: list[DocChunk],
) -> None:
    pr_ids = [pr.id for pr in github_prs]
    _raise_if_duplicates(pr_ids, "GitHub PR ID")

    ticket_ids = [ticket.id for ticket in jira_tickets]
    _raise_if_duplicates(ticket_ids, "Jira ticket ID")

    doc_chunk_ids = [chunk.id for chunk in doc_chunks]
    _raise_if_duplicates(doc_chunk_ids, "Doc chunk ID")

    ticket_id_set = set(ticket_ids)
    linked_ticket_ids = {ticket_id for pr in github_prs for ticket_id in pr.linked_tickets}

    missing_ticket_ids = sorted(linked_ticket_ids - ticket_id_set)
    if missing_ticket_ids:
        raise ValueError(f"PRs link to unknown Jira tickets: {', '.join(missing_ticket_ids)}")

    unlinked_ticket_ids = sorted(ticket_id_set - linked_ticket_ids)
    if unlinked_ticket_ids:
        raise ValueError(f"Jira tickets are not linked by any PR: {', '.join(unlinked_ticket_ids)}")


def load_mock_dataset() -> MockDataset:
    github_prs = load_github_prs(DATA_DIR / "github_prs.json")
    jira_tickets = load_jira_tickets(DATA_DIR / "jira_tickets.json")
    doc_chunks = load_markdown_docs(DATA_DIR / "docs")

    validate_cross_source_consistency(github_prs, jira_tickets, doc_chunks)

    return MockDataset(
        github_prs=github_prs,
        jira_tickets=jira_tickets,
        doc_chunks=doc_chunks,
    )


def load_sources():
    dataset = load_mock_dataset()
    return {
        "github_prs": dataset.github_prs,
        "jira_tickets": dataset.jira_tickets,
        "docs": dataset.doc_chunks,
    }


def _raise_if_duplicates(values: list[str], label: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise ValueError(f"Duplicate {label}s: {', '.join(duplicates)}")
