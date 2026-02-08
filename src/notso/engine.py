"""Core search engine plumbing."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import List, Optional, Tuple

from .core.index import InMemoryIndex, build_in_memory_index
from .core.models import Document
from .core.ranker import HybridRanker, tokenize
from .resource_plan import ResourceGuard, ResourceLimits, StopReason, plan_query_terms


@dataclass(frozen=True)
class SearchResult:
    """Search result containing document metadata and a score."""

    doc_id: str
    score: float
    text: str


def build_index(documents: List[Document]) -> InMemoryIndex:
    """Build a search index from documents."""
    return build_in_memory_index(documents)


def search_with_limits(
    index: InMemoryIndex,
    query: str,
    top_k: int = 5,
    limits: Optional[ResourceLimits] = None,
) -> Tuple[List[SearchResult], Optional[StopReason]]:
    """Search the index with optional resource limits."""

    tokens = tokenize(query)
    if not tokens:
        return [], None

    # Calculate IDF for query planning
    idf_map = {}
    doc_count = index.document_count()
    if doc_count > 0:
        for term in set(tokens):
            df = index.document_frequency(term)
            # Standard IDF formula: log(N / df)
            # Using specific formula from ranker if needed, but a simple one here for planning
            if df > 0:
                import math
                idf_map[term] = math.log((doc_count - df + 0.5) / (df + 0.5) + 1.0)
            else:
                idf_map[term] = 0.0

    ordered_terms = plan_query_terms(tokens, idf_map, limits)
    if not ordered_terms:
         return [], None

    guard = ResourceGuard(limits or ResourceLimits())
    guard.start()

    ranker = HybridRanker()
    # Pre-calculate corpus stats
    avg_len = index.average_document_length()
    
    # We only need to score documents that contain at least one query term
    # Optimization: simple OR query retrieval
    candidate_doc_ids = set()
    for term in ordered_terms:
        # This is where we would ideally have an inverted index that gives us doc_ids easily
        # The InMemoryIndex has _term_frequencies: doc_id -> {term: count}
        # But not inverted index: term -> [doc_ids]
        # For this refactor, we iterate all docs (efficient enough for small scale)
        # OR we could rely on the fact the original engine iterated all docs.
        pass

    results: List[SearchResult] = []
    stop_reason: Optional[StopReason] = None
    docs_processed = 0
    
    # Optimization: In a real system we'd use an inverted index. 
    # For now, we iterate all docs to maintain behavior of original engine but use new ranker.
    
    for doc in index.documents():
        stop_reason = guard.checkpoint(docs_processed=docs_processed, terms_processed=0)
        if stop_reason:
            break
        docs_processed += 1
        
        tf = index.term_frequencies(doc.doc_id)
        
        # Check if doc has any of the query terms to avoid scoring irrelevant docs
        if not any(t in tf for t in ordered_terms):
             continue

        score = ranker.score(
            query_terms=ordered_terms,
            document=doc,
            term_frequencies=tf,
            average_document_length=avg_len,
            corpus_size=doc_count,
            document_frequency_lookup=index.document_frequency
        )

        if score > 0:
            results.append(SearchResult(doc_id=doc.doc_id, score=score, text=doc.content))

    results.sort(key=lambda item: item.score, reverse=True)
    return results[: max(1, top_k)], stop_reason


def search(index: InMemoryIndex, query: str, top_k: int = 5) -> List[SearchResult]:
    """Search the index for a query and return ranked results."""
    results, _ = search_with_limits(index, query, top_k=top_k)
    return results


def save_index(index: InMemoryIndex, path: str | Path) -> None:
    """Save the index to disk as JSON."""
    path = Path(path)
    # Reconstruct the payload format expected by InMemoryIndex or create a new one.
    # The original engine saved a specific format. We should try to respect a unified format.
    # Let's save enough to reconstruct the InMemoryIndex.
    
    payload = {
        "version": 2, # Bump version to signal change
        "documents": [{"id": doc.doc_id, "title": doc.title, "content": doc.content, "metadata": doc.metadata} for doc in index.documents()],
        # We can re-compute stats on load, so we just save documents for simplicity in this version,
        # OR we save the pre-computed stats if we want fast load.
        # Let's stick to saving documents for now as the 'source of truth' for the index.
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_index(path: str | Path) -> InMemoryIndex:
    """Load the index from disk."""
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    
    # Handle legacy version 1 (from original engine.py)
    if payload.get("version") == 1:
        documents = [Document(doc_id=item["id"], title="", content=item["text"], metadata={}) for item in payload["documents"]]
    else:
        documents = [Document(doc_id=item["id"], title=item.get("title", ""), content=item["content"], metadata=item.get("metadata")) for item in payload["documents"]]
        
    return build_in_memory_index(documents)
