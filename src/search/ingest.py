"""Document ingestion utilities for the search engine."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List

from .models import Document


DEFAULT_SAMPLE_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_docs.json"


def _normalize_text(text: str) -> str:
    return " ".join(text.split())


def _normalize_metadata(raw: dict[str, Any] | None) -> dict[str, str] | None:
    if not raw:
        return None
    normalized: dict[str, str] = {}
    for key, value in raw.items():
        normalized[str(key)] = str(value)
    return normalized


def _normalize_document(raw: dict[str, Any], index: int) -> Document:
    doc_id = str(raw.get("id") or f"doc-{index + 1}")
    title = _normalize_text(str(raw.get("title") or "Untitled"))
    content = _normalize_text(str(raw.get("content") or ""))
    if not content:
        raise ValueError(f"Document {doc_id} is missing content")
    metadata = _normalize_metadata(raw.get("metadata"))
    return Document(doc_id=doc_id, title=title, content=content, metadata=metadata)


def load_documents_from_json(path: str | Path) -> List[Document]:
    """Load documents from a JSON corpus file."""

    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Corpus payload must be a JSON object")
    version = payload.get("version")
    if version != 1:
        raise ValueError(f"Unsupported corpus version: {version}")
    raw_documents = payload.get("documents")
    if not isinstance(raw_documents, list):
        raise ValueError("Corpus documents must be a list")
    return [_normalize_document(raw, index) for index, raw in enumerate(raw_documents)]


def load_sample_documents(path: str | Path | None = None) -> List[Document]:
    """Load the bundled sample documents."""

    resolved_path = Path(path) if path else DEFAULT_SAMPLE_PATH
    return load_documents_from_json(resolved_path)


def summarize_documents(documents: Iterable[Document]) -> list[str]:
    """Return display-friendly summaries for documents."""

    summaries: list[str] = []
    for doc in documents:
        summaries.append(f"{doc.doc_id}: {doc.title}")
    return summaries


__all__ = [
    "DEFAULT_SAMPLE_PATH",
    "load_documents_from_json",
    "load_sample_documents",
    "summarize_documents",
]
