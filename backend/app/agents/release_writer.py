from app.schemas import ReleasePackage


def write_release_package(changes, retrieved_docs):
    return ReleasePackage(
        changelog=[],
        internal_release_notes="",
        customer_release_notes="",
        documentation_updates=[],
        evidence=[],
    )
