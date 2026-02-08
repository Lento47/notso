"""Sample documents for indexing demos."""
from __future__ import annotations

from pathlib import Path
from typing import List

from search.ingest import DEFAULT_SAMPLE_PATH, load_sample_documents
from search.models import Document as SearchDocument

from .engine import Document


def _as_engine_document(sample_doc: SearchDocument) -> Document:
    text = f"{sample_doc.title} {sample_doc.content}".strip()
    return Document(doc_id=sample_doc.doc_id, text=text)


def load_documents(path: Path | None = None) -> List[Document]:
    """Load sample documents for the Notso engine."""

    docs = load_sample_documents(path or DEFAULT_SAMPLE_PATH)
    return [_as_engine_document(doc) for doc in docs]


SAMPLE_DOCUMENTS: List[Document] = load_documents()
