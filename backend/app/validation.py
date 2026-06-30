from app.schemas import ChangeSummary, ReleasePackage, RetrievedDocChunk, ValidationResult


INTERNAL_DETAIL_TERMS = [
    "github:pr",
    "jira:",
    "stack trace",
    "database migration",
    "internal service",
    "auth/okta_callback.py",
    "auth/saml_config.py",
]


def validate_release_package(
    release_package: ReleasePackage,
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> list[ValidationResult]:
    results = []

    results.append(_validate_evidence_ids(release_package, changes, retrieved_docs))
    results.append(_validate_jira_coverage(release_package, changes))
    results.append(_validate_documentation_references(release_package, retrieved_docs))
    results.append(_validate_customer_notes(release_package))
    results.extend(_validate_required_sections(release_package))

    return results


def _validate_evidence_ids(
    release_package: ReleasePackage,
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> ValidationResult:
    known_evidence_ids = _known_evidence_ids(changes, retrieved_docs)
    used_evidence_ids = _used_evidence_ids(release_package)
    invalid_ids = sorted(used_evidence_ids - known_evidence_ids)

    if invalid_ids:
        return ValidationResult(
            level="error",
            code="INVALID_EVIDENCE_ID",
            message=f"Unknown evidence IDs: {', '.join(invalid_ids)}",
        )

    return ValidationResult(
        level="pass",
        code="VALID_EVIDENCE_IDS",
        message="All evidence IDs are valid.",
    )


def _validate_jira_coverage(
    release_package: ReleasePackage,
    changes: list[ChangeSummary],
) -> ValidationResult:
    expected_jira_ids = {
        source_id for change in changes for source_id in change.source_ids if source_id.startswith("jira:")
    }
    used_jira_ids = {source_id for source_id in _used_evidence_ids(release_package) if source_id.startswith("jira:")}
    missing_jira_ids = sorted(expected_jira_ids - used_jira_ids)

    if missing_jira_ids:
        return ValidationResult(
            level="warning",
            code="MISSING_JIRA_COVERAGE",
            message=f"Missing Jira coverage: {', '.join(missing_jira_ids)}",
        )

    return ValidationResult(
        level="pass",
        code="JIRA_COVERAGE",
        message="All Jira tickets are covered.",
    )


def _validate_documentation_references(
    release_package: ReleasePackage,
    retrieved_docs: list[RetrievedDocChunk],
) -> ValidationResult:
    retrieved_doc_ids = {doc.doc_chunk_id for doc in retrieved_docs}
    invalid_doc_ids = sorted(
        update.doc_chunk_id
        for update in release_package.documentation_updates
        if update.doc_chunk_id not in retrieved_doc_ids
    )

    if invalid_doc_ids:
        return ValidationResult(
            level="error",
            code="INVALID_DOCUMENTATION_REFERENCE",
            message=f"Documentation updates reference non-retrieved docs: {', '.join(invalid_doc_ids)}",
        )

    return ValidationResult(
        level="pass",
        code="VALID_DOCUMENTATION_REFERENCES",
        message="All documentation updates reference retrieved docs.",
    )


def _validate_customer_notes(release_package: ReleasePackage) -> ValidationResult:
    customer_notes = release_package.customer_release_notes.lower()
    suspicious_terms = sorted(term for term in INTERNAL_DETAIL_TERMS if term in customer_notes)

    if suspicious_terms:
        return ValidationResult(
            level="warning",
            code="CUSTOMER_NOTES_INTERNAL_DETAIL",
            message=f"Customer notes may contain internal details: {', '.join(suspicious_terms)}",
        )

    return ValidationResult(
        level="pass",
        code="CUSTOMER_NOTES_CLEAN",
        message="Customer-facing notes do not contain obvious internal details.",
    )


def _validate_required_sections(release_package: ReleasePackage) -> list[ValidationResult]:
    results = []

    if not release_package.changelog:
        results.append(
            ValidationResult(
                level="error",
                code="EMPTY_CHANGELOG",
                message="Changelog must not be empty.",
            )
        )

    if not release_package.internal_release_notes.strip():
        results.append(
            ValidationResult(
                level="warning",
                code="EMPTY_INTERNAL_RELEASE_NOTES",
                message="Internal release notes must not be empty.",
            )
        )

    if not release_package.customer_release_notes.strip():
        results.append(
            ValidationResult(
                level="warning",
                code="EMPTY_CUSTOMER_RELEASE_NOTES",
                message="Customer release notes must not be empty.",
            )
        )

    return results


def _known_evidence_ids(
    changes: list[ChangeSummary],
    retrieved_docs: list[RetrievedDocChunk],
) -> set[str]:
    return {
        *[source_id for change in changes for source_id in change.source_ids],
        *[doc.doc_chunk_id for doc in retrieved_docs],
    }


def _used_evidence_ids(release_package: ReleasePackage) -> set[str]:
    evidence_ids = set(release_package.evidence)

    for changelog_item in release_package.changelog:
        evidence_ids.update(changelog_item.evidence_ids)

    for update in release_package.documentation_updates:
        evidence_ids.update(update.evidence_ids)

    return evidence_ids
