"""Search engine entry point and core interfaces."""

from __future__ import annotations

from typing import List

from .models import Document, Index
from .ranker import HybridRanker, RankedResult, tokenize


class SearchEngine:
    """Search engine that scores documents using a hybrid ranker."""

    def __init__(self, index: Index) -> None:
        self._index = index
        self._ranker = HybridRanker()

    def search(self, query: str, top_k: int = 5) -> List[RankedResult]:
        """Search the index and return ranked results."""

        terms = tokenize(query)
        if not terms:
            return []

        results: List[RankedResult] = []
        avg_len = self._index.average_document_length()
        corpus_size = self._index.document_count()

        for doc in self._index.documents():
            term_freqs = self._index.term_frequencies(doc.doc_id)
            score = self._ranker.score(
                query_terms=terms,
                document=doc,
                term_frequencies=term_freqs,
                average_document_length=avg_len,
                corpus_size=corpus_size,
                document_frequency_lookup=self._index.document_frequency,
            )
            if score > 0:
                results.append(
                    RankedResult(
                        doc_id=doc.doc_id,
                        title=doc.title,
                        score=score,
                        metadata=doc.metadata or {},
                    )
                )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[: max(top_k, 0)]


__all__ = ["Document", "Index", "SearchEngine"]
