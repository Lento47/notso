"""Sample documents for indexing demos."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .ingest.loader import DEFAULT_SAMPLE_PATH, load_sample_documents
from .core.models import Document


def load_documents(path: Path | None = None) -> List[Document]:
    """Load sample documents for the Notso engine."""

    return load_sample_documents(path or DEFAULT_SAMPLE_PATH)


SAMPLE_DOCUMENTS: List[Document] = load_documents()
