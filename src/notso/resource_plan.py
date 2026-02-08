"""Resource governance helpers for safe, deterministic search."""
from __future__ import annotations

from dataclasses import dataclass
import time
import tracemalloc
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set


@dataclass(frozen=True)
class ResourceLimits:
    """Limits that control how much work a search can perform."""

    max_seconds: Optional[float] = None
    max_memory_bytes: Optional[int] = None
    max_documents: Optional[int] = None
    max_query_terms: Optional[int] = None
    term_block_size: Optional[int] = None


@dataclass(frozen=True)
class StopReason:
    """Reason the search stopped early."""

    reason: str
    detail: str


class ResourceGuard:
    """Tracks resource usage and stops work when limits are reached."""

    def __init__(
        self,
        limits: ResourceLimits,
        *,
        clock: Callable[[], float] = time.monotonic,
        memory_reader: Optional[Callable[[], int]] = None,
    ) -> None:
        self._limits = limits
        self._clock = clock
        self._memory_reader = memory_reader
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """Start tracking resource usage."""

        self._start_time = self._clock()
        if self._limits.max_memory_bytes is not None and self._memory_reader is None:
            tracemalloc.start()

            def _default_memory_reader() -> int:
                current, _peak = tracemalloc.get_traced_memory()
                return current

            self._memory_reader = _default_memory_reader

    def checkpoint(self, *, docs_processed: int, terms_processed: int) -> Optional[StopReason]:
        """Return a stop reason if any limit has been exceeded."""

        if self._limits.max_documents is not None and docs_processed >= self._limits.max_documents:
            return StopReason(
                reason="max_documents",
                detail=f"Processed {docs_processed} documents (limit {self._limits.max_documents}).",
            )
        if self._start_time is not None and self._limits.max_seconds is not None:
            elapsed = self._clock() - self._start_time
            if elapsed >= self._limits.max_seconds:
                return StopReason(
                    reason="max_seconds",
                    detail=f"Elapsed {elapsed:.4f}s (limit {self._limits.max_seconds:.4f}s).",
                )
        if self._limits.max_memory_bytes is not None and self._memory_reader is not None:
            memory_used = self._memory_reader()
            if memory_used >= self._limits.max_memory_bytes:
                return StopReason(
                    reason="max_memory_bytes",
                    detail=(
                        f"Memory {memory_used} bytes (limit {self._limits.max_memory_bytes} bytes)."
                    ),
                )
        if self._limits.max_query_terms is not None and terms_processed >= self._limits.max_query_terms:
            return StopReason(
                reason="max_query_terms",
                detail=f"Processed {terms_processed} query terms (limit {self._limits.max_query_terms}).",
            )
        return None


def _order_terms(terms: Iterable[str], idf_lookup: Dict[str, float]) -> List[str]:
    unique_terms: Set[str] = set(terms)
    return sorted(
        unique_terms,
        key=lambda term: (idf_lookup.get(term, 0.0), term),
        reverse=True,
    )


def plan_query_terms(
    terms: Sequence[str],
    idf_lookup: Dict[str, float],
    limits: Optional[ResourceLimits],
) -> List[str]:
    """Return terms filtered and ordered to fit the requested limits."""

    ordered = _order_terms(terms, idf_lookup)
    if limits and limits.max_query_terms is not None:
        allowed = set(ordered[: limits.max_query_terms])
        return [term for term in ordered if term in allowed]
    return ordered


def plan_term_blocks(
    terms: Sequence[str],
    idf_lookup: Dict[str, float],
    limits: Optional[ResourceLimits],
) -> List[List[str]]:
    """Split ordered query terms into deterministic blocks."""

    ordered = plan_query_terms(terms, idf_lookup, limits)
    if not ordered:
        return []
    block_size = len(ordered)
    if limits and limits.term_block_size:
        block_size = max(1, limits.term_block_size)
    return [ordered[i : i + block_size] for i in range(0, len(ordered), block_size)]


__all__ = [
    "ResourceGuard",
    "ResourceLimits",
    "StopReason",
    "plan_query_terms",
    "plan_term_blocks",
]
