"""Core data structures and interfaces for search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class Document:
    """A minimal document representation for indexing and retrieval."""

    doc_id: str
    title: str
    content: str
    metadata: dict[str, str] | None = None


class Index(Protocol):
    """Protocol for index implementations used by the search engine."""

    def documents(self) -> Iterable[Document]:
        ...

    def term_frequencies(self, doc_id: str) -> dict[str, int]:
        ...

    def document_frequency(self, term: str) -> int:
        ...

    def document_count(self) -> int:
        ...

    def average_document_length(self) -> float:
        ...


__all__ = ["Document", "Index"]
