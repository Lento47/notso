"""Command-line interface for the Notso search engine."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Sequence

from .engine import SearchResult, build_index, load_index, save_index, search_with_limits
from .ingest.loader import load_documents_from_json
from .resource_plan import ResourceLimits
from .sample_docs import SAMPLE_DOCUMENTS


DEFAULT_INDEX_PATH = Path("data/index.json")


def _print_results(results: Iterable[SearchResult]) -> None:
    for rank, result in enumerate(results, start=1):
        print(f"{rank}. {result.doc_id} [{result.score:.4f}] {result.text}")


def _handle_index(args: argparse.Namespace) -> int:
    documents = load_documents_from_json(Path(args.data)) if args.data else SAMPLE_DOCUMENTS
    index = build_index(documents)
    save_index(index, args.output)
    print(f"Indexed {index.document_count()} documents into {args.output}")
    return 0


def _handle_search(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    limits = ResourceLimits(
        max_seconds=args.max_seconds,
        max_memory_bytes=args.max_memory_kb * 1024 if args.max_memory_kb else None,
        max_documents=args.max_docs,
        max_query_terms=args.max_terms,
        term_block_size=args.term_block_size,
    )
    results, stop_reason = search_with_limits(index, args.query, top_k=args.top_k, limits=limits)
    if not results:
        print("No results found.")
        return 0
    _print_results(results)
    if stop_reason:
        print(f"Search stopped early: {stop_reason.reason} ({stop_reason.detail})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(prog="notso")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index sample documents")
    index_parser.add_argument(
        "--output",
        default=str(DEFAULT_INDEX_PATH),
        help="Output path for the index JSON",
    )
    index_parser.add_argument(
        "--data",
        default=None,
        help="Optional path to a JSON corpus file",
    )
    index_parser.set_defaults(func=_handle_index)

    search_parser = subparsers.add_parser("search", help="Search the index")
    search_parser.add_argument("query", help="Query string")
    search_parser.add_argument(
        "--index",
        default=str(DEFAULT_INDEX_PATH),
        help="Path to the index JSON",
    )
    search_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return",
    )
    search_parser.add_argument(
        "--max-seconds",
        type=float,
        default=None,
        help="Stop searching after this many seconds",
    )
    search_parser.add_argument(
        "--max-memory-kb",
        type=int,
        default=None,
        help="Stop searching after this many kilobytes of memory",
    )
    search_parser.add_argument(
        "--max-docs",
        type=int,
        default=None,
        help="Stop searching after scoring this many documents",
    )
    search_parser.add_argument(
        "--max-terms",
        type=int,
        default=None,
        help="Limit the number of query terms used for scoring",
    )
    search_parser.add_argument(
        "--term-block-size",
        type=int,
        default=None,
        help="Process query terms in blocks of this size",
    )
    search_parser.set_defaults(func=_handle_search)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Notso CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
