"""In-memory index implementation."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .models import Document, Index
from .ranker import tokenize


@dataclass
class InMemoryIndex(Index):
    """Simple in-memory inverted index."""

    _documents: Dict[str, Document]
    _term_frequencies: Dict[str, Dict[str, int]]
    _document_frequencies: Dict[str, int]
    _average_document_length: float

    def documents(self) -> Iterable[Document]:
        return self._documents.values()

    def term_frequencies(self, doc_id: str) -> Dict[str, int]:
        return self._term_frequencies.get(doc_id, {})

    def document_frequency(self, term: str) -> int:
        return self._document_frequencies.get(term, 0)

    def document_count(self) -> int:
        return len(self._documents)

    def average_document_length(self) -> float:
        return self._average_document_length


def build_in_memory_index(documents: Iterable[Document]) -> InMemoryIndex:
    """Build an in-memory index for the provided documents."""

    doc_map: Dict[str, Document] = {}
    term_frequencies: Dict[str, Dict[str, int]] = {}
    document_frequencies: Dict[str, int] = defaultdict(int)
    total_length = 0

    for doc in documents:
        doc_map[doc.doc_id] = doc
        tokens = tokenize(f"{doc.title} {doc.content}")
        total_length += len(tokens)
        counts = Counter(tokens)
        term_frequencies[doc.doc_id] = dict(counts)
        for term in counts:
            document_frequencies[term] += 1

    average_length = total_length / max(len(doc_map), 1)

    return InMemoryIndex(
        _documents=doc_map,
        _term_frequencies=term_frequencies,
        _document_frequencies=dict(document_frequencies),
        _average_document_length=average_length,
    )


__all__ = ["InMemoryIndex", "build_in_memory_index"]
