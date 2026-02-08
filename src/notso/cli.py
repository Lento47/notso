"""Command-line interface for the Notso search engine."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Sequence

from .engine import SearchResult, build_index, load_index, save_index, search
from .sample_docs import SAMPLE_DOCUMENTS


DEFAULT_INDEX_PATH = Path("data/index.json")


def _print_results(results: Iterable[SearchResult]) -> None:
    for rank, result in enumerate(results, start=1):
        print(f"{rank}. {result.doc_id} [{result.score:.4f}] {result.text}")


def _handle_index(args: argparse.Namespace) -> int:
    index = build_index(SAMPLE_DOCUMENTS)
    save_index(index, args.output)
    print(f"Indexed {len(index.documents)} documents into {args.output}")
    return 0


def _handle_search(args: argparse.Namespace) -> int:
    index = load_index(args.index)
    results = search(index, args.query, top_k=args.top_k)
    if not results:
        print("No results found.")
        return 0
    _print_results(results)
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
    search_parser.set_defaults(func=_handle_search)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Notso CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
