from app.retriever import retrieve_docs


def test_retrieve_docs_placeholder():
    assert retrieve_docs("authentication") == []
