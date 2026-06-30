import re

from app.schemas import ChangeSummary, GithubPR, JiraTicket


STOPWORDS = {
    "a",
    "add",
    "an",
    "and",
    "as",
    "can",
    "for",
    "in",
    "is",
    "of",
    "so",
    "the",
    "their",
    "through",
    "to",
    "with",
}


def digest_artifacts(
    github_prs: list[GithubPR],
    jira_tickets: list[JiraTicket],
) -> list[ChangeSummary]:
    summaries: list[ChangeSummary] = []

    for ticket in jira_tickets:
        linked_prs = [pr for pr in github_prs if ticket.id in pr.linked_tickets]
        source_ids = [f"jira:{ticket.id}", *[pr.id for pr in linked_prs]]

        summaries.append(
            ChangeSummary(
                id=ticket.id,
                title=ticket.title,
                summary=_build_summary(ticket),
                source_ids=source_ids,
                affected_systems=ticket.affected_systems,
                customer_facing=ticket.customer_facing,
                risk_level=_risk_level(ticket),
                keywords=_keywords(ticket, linked_prs),
            )
        )

    return summaries


def _build_summary(ticket: JiraTicket) -> str:
    return f"{ticket.title}. {ticket.description}"


def _risk_level(ticket: JiraTicket) -> str:
    affects_auth = "Authentication Service" in ticket.affected_systems

    if ticket.customer_facing and affects_auth:
        return "medium"
    if not ticket.customer_facing:
        return "low"
    if ticket.type == "Bug" and affects_auth:
        return "medium"
    return "low"


def _keywords(ticket: JiraTicket, linked_prs: list[GithubPR]) -> list[str]:
    text_parts = [
        ticket.title,
        ticket.description,
        " ".join(ticket.affected_systems),
        *[pr.title for pr in linked_prs],
    ]
    words = re.findall(r"[a-z0-9]+", " ".join(text_parts).lower())

    keywords: list[str] = []
    for word in words:
        if word in STOPWORDS or word in keywords:
            continue
        keywords.append(word)

    return keywords
