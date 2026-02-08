from pathlib import Path

from notso.ingest.loader import DEFAULT_SAMPLE_PATH, load_documents_from_json


def test_loads_sample_documents() -> None:
    docs = load_documents_from_json(DEFAULT_SAMPLE_PATH)
    assert len(docs) >= 5
    first = docs[0]
    assert first.doc_id == "doc-1"
    assert "  " not in first.title
    assert "  " not in first.content
    assert first.title == "Quick Brown Fox"


def test_can_load_from_explicit_path() -> None:
    docs = load_documents_from_json(Path("data/sample_docs.json"))
    assert docs
