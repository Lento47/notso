"""Search package exposing the main engine."""

from .engine import Document, SearchEngine
from .index import InMemoryIndex, build_in_memory_index

__all__ = ["Document", "SearchEngine", "InMemoryIndex", "build_in_memory_index"]
