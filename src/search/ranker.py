"""Ranking utilities for the search engine."""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Callable, Iterable, List

from .models import Document


@dataclass(frozen=True)
class RankedResult:
    doc_id: str
    title: str
    score: float
    metadata: dict[str, str]


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase terms."""

    return [token.lower() for token in text.split() if token.strip()]


class HybridRanker:
    """Hybrid ranker combining lexical and custom signal scoring."""

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b

    def score(
        self,
        *,
        query_terms: Iterable[str],
        document: Document,
        term_frequencies: dict[str, int],
        average_document_length: float,
        corpus_size: int,
        document_frequency_lookup: Callable[[str], int],
    ) -> float:
        """Return a hybrid lexical + custom rank score."""
        terms = list(query_terms)
        doc_len = max(sum(term_frequencies.values()), 1)
        avg_len = average_document_length or 1.0
        lexical_score = 0.0
        matched_terms = 0

        for term in terms:
            tf = term_frequencies.get(term, 0)
            if tf == 0:
                continue
            matched_terms += 1
            df = document_frequency_lookup(term)
            idf = log((corpus_size - df + 0.5) / (df + 0.5) + 1.0)
            denom = tf + self._k1 * (1 - self._b + self._b * (doc_len / avg_len))
            lexical_score += idf * (tf * (self._k1 + 1) / denom)

        if matched_terms == 0:
            return 0.0

        proximity_bonus = self._proximity_bonus(document, terms)
        coverage_bonus = matched_terms / max(len(terms), 1)
        title_boost = 1.0 + 0.2 * self._title_match_ratio(document.title, terms)

        return (lexical_score + proximity_bonus + coverage_bonus) * title_boost

    def _proximity_bonus(self, document: Document, query_terms: Iterable[str]) -> float:
        tokens = tokenize(document.content)
        term_positions = {
            term: [idx for idx, token in enumerate(tokens) if token == term]
            for term in query_terms
        }
        positions = [pos for plist in term_positions.values() for pos in plist]
        if len(positions) < 2:
            return 0.0
        span = max(positions) - min(positions) + 1
        return 1.0 / span

    def _title_match_ratio(self, title: str, query_terms: Iterable[str]) -> float:
        title_terms = set(tokenize(title))
        if not title_terms:
            return 0.0
        matches = len(title_terms.intersection(query_terms))
        return matches / len(title_terms)


__all__ = ["HybridRanker", "RankedResult", "tokenize"]
