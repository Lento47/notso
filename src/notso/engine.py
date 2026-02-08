"""Core search engine logic for building and querying an index."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .resource_plan import ResourceGuard, ResourceLimits, StopReason, plan_term_blocks

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Document:
    """Represents a document to index."""

    doc_id: str
    text: str


@dataclass(frozen=True)
class SearchIndex:
    """In-memory search index with TF-IDF weights and norms."""

    version: int
    documents: List[Document]
    idf: Dict[str, float]
    doc_vectors: Dict[str, Dict[str, float]]
    doc_norms: Dict[str, float]


@dataclass(frozen=True)
class SearchResult:
    """Search result containing document metadata and a score."""

    doc_id: str
    score: float
    text: str


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens."""

    return _TOKEN_RE.findall(text.lower())


def _term_frequencies(tokens: Sequence[str]) -> Dict[str, float]:
    counts: Dict[str, float] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0.0) + 1.0
    return counts


def build_index(documents: Iterable[Document]) -> SearchIndex:
    """Build a TF-IDF search index from documents."""

    docs = list(documents)
    tokenized = [tokenize(doc.text) for doc in docs]
    doc_freq: Dict[str, float] = {}
    for tokens in tokenized:
        seen = set(tokens)
        for token in seen:
            doc_freq[token] = doc_freq.get(token, 0.0) + 1.0
    total_docs = float(len(docs))
    idf = {
        term: math.log((1.0 + total_docs) / (1.0 + freq)) + 1.0
        for term, freq in doc_freq.items()
    }
    doc_vectors: Dict[str, Dict[str, float]] = {}
    doc_norms: Dict[str, float] = {}
    for doc, tokens in zip(docs, tokenized):
        tf = _term_frequencies(tokens)
        vector = {term: tf_val * idf[term] for term, tf_val in tf.items()}
        norm = math.sqrt(sum(weight * weight for weight in vector.values()))
        doc_vectors[doc.doc_id] = vector
        doc_norms[doc.doc_id] = norm
    return SearchIndex(
        version=1,
        documents=docs,
        idf=idf,
        doc_vectors=doc_vectors,
        doc_norms=doc_norms,
    )


def search_with_limits(
    index: SearchIndex,
    query: str,
    top_k: int = 5,
    limits: Optional[ResourceLimits] = None,
) -> Tuple[List[SearchResult], Optional[StopReason]]:
    """Search the index with optional resource limits."""

    tokens = tokenize(query)
    if not tokens:
        return [], None
    term_blocks = plan_term_blocks(tokens, index.idf, limits)
    if not term_blocks:
        return [], None

    guard = ResourceGuard(limits or ResourceLimits())
    guard.start()
    allowed_terms = {term for block in term_blocks for term in block}
    filtered_tokens = [term for term in tokens if term in allowed_terms]
    query_tf = _term_frequencies(filtered_tokens)
    query_vec = {
        term: query_tf_val * index.idf.get(term, 0.0)
        for term, query_tf_val in query_tf.items()
    }
    query_norm = math.sqrt(sum(weight * weight for weight in query_vec.values()))
    if query_norm == 0.0:
        return [], None
    results: List[SearchResult] = []
    stop_reason: Optional[StopReason] = None
    docs_processed = 0
    for doc in index.documents:
        stop_reason = guard.checkpoint(docs_processed=docs_processed, terms_processed=0)
        if stop_reason:
            break
        docs_processed += 1
        doc_vector = index.doc_vectors.get(doc.doc_id, {})
        score = 0.0
        terms_processed = 0
        for block in term_blocks:
            for term in block:
                q_weight = query_vec.get(term, 0.0)
                score += q_weight * doc_vector.get(term, 0.0)
            terms_processed += len(block)
            stop_reason = guard.checkpoint(
                docs_processed=docs_processed,
                terms_processed=terms_processed,
            )
            if stop_reason:
                break
        doc_norm = index.doc_norms.get(doc.doc_id, 0.0)
        if doc_norm > 0.0:
            score = score / (query_norm * doc_norm)
        else:
            score = 0.0
        if score > 0.0:
            results.append(SearchResult(doc_id=doc.doc_id, score=score, text=doc.text))
        if stop_reason:
            break
    results.sort(key=lambda item: item.score, reverse=True)
    return results[: max(1, top_k)], stop_reason


def search(index: SearchIndex, query: str, top_k: int = 5) -> List[SearchResult]:
    """Search the index for a query and return ranked results."""

    results, _stop_reason = search_with_limits(index, query, top_k=top_k)
    return results


def save_index(index: SearchIndex, path: str | Path) -> None:
    """Save the index to disk as JSON."""

    path = Path(path)
    payload = {
        "version": index.version,
        "documents": [{"id": doc.doc_id, "text": doc.text} for doc in index.documents],
        "idf": index.idf,
        "doc_vectors": index.doc_vectors,
        "doc_norms": index.doc_norms,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_index(path: str | Path) -> SearchIndex:
    """Load the index from disk."""

    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    documents = [Document(doc_id=item["id"], text=item["text"]) for item in payload["documents"]]
    return SearchIndex(
        version=payload["version"],
        documents=documents,
        idf={key: float(value) for key, value in payload["idf"].items()},
        doc_vectors={
            doc_id: {term: float(weight) for term, weight in weights.items()}
            for doc_id, weights in payload["doc_vectors"].items()
        },
        doc_norms={key: float(value) for key, value in payload["doc_norms"].items()},
    )
