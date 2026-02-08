"""Sample documents for indexing demos."""
from __future__ import annotations

from typing import List

from .engine import Document

SAMPLE_DOCUMENTS: List[Document] = [
    Document(doc_id="doc-1", text="The quick brown fox jumps over the lazy dog."),
    Document(doc_id="doc-2", text="Search engines rank documents based on relevance."),
    Document(doc_id="doc-3", text="Indexing sample documents helps test search quality."),
    Document(doc_id="doc-4", text="Python standard library tools enable quick prototypes."),
    Document(doc_id="doc-5", text="Ranking results with scores improves user trust."),
]
