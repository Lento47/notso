# Notso Search Engine

A tiny, standard-library-only search engine with a CLI, minimal HTTP API, and web UI. It indexes documents into a compact JSON format and ranks results with a custom TF-IDF + cosine similarity scorer.

## Setup

This repo uses only the Python standard library.

```bash
python --version
```

Run commands from the repo root so the `src/` package layout resolves correctly.

## Quickstart

Index the bundled sample documents (default output `data/index.json`):

```bash
python -m notso.cli index
```

Search the index:

```bash
python -m notso.cli search "search terms"
```

## Indexing (CLI)

Create an index from a custom JSON corpus and write to a specific path:

```bash
python -m notso.cli index --data path/to/corpus.json --output data/custom-index.json
```

Expected corpus schema (JSON list of objects):

```json
[
  {"id": "doc-1", "text": "Document text here."},
  {"id": "doc-2", "text": "More document text."}
]
```

## Querying (CLI)

Search a specific index and control the number of results:

```bash
python -m notso.cli search "search terms" --index data/custom-index.json --top-k 10
```

Resource limits can stop searches early (time, memory, docs, terms):

```bash
python -m notso.cli search "search terms" --max-seconds 0.25 --max-docs 50
```

If you install the project, the console script is also available:

```bash
notso search "search terms"
```

## HTTP API + Web UI

Run the minimal web UI server (defaults to `http://127.0.0.1:8080`):

```bash
python -m notso.web.app
```

Endpoints:

- `GET /` renders the search form.
- `GET /search?q=your+query` renders results.

The UI is plain HTML/CSS/JS served via Python’s `http.server`.

## Index Storage Format (versioned)

Indexes are stored as JSON with a version tag and TF-IDF components:

```json
{
  "version": 1,
  "documents": [{"id": "doc-1", "text": "..."}],
  "idf": {"term": 1.23},
  "doc_vectors": {"doc-1": {"term": 0.45}},
  "doc_norms": {"doc-1": 0.67}
}
```

If you change scoring or schema, increment the `version` and document the change to preserve backward compatibility.

## Ranking Algorithm Overview

Ranking is implemented in `src/notso/engine.py`:

1. **Tokenization**: Lowercase alphanumeric token extraction.
2. **TF-IDF weighting**: Build document vectors with log-smoothed IDF.
3. **Cosine similarity**: Score each document against the query vector.
4. **Resource guards**: Optional limits to cap time, memory, terms, or documents during search.

This keeps scoring deterministic and fast for small corpora.

### Extending or improving ranking

You can evolve the custom ranker without adding dependencies:

- **Change weighting**: Replace TF-IDF with BM25-style scoring or add field boosts.
- **Add query expansion**: Use a synonym map or simple stemming rules before scoring.
- **Blend extra signals**: Add recency or curated boosts to the final score.
- **Improve tokenization**: Update the tokenizer regex or add language-specific normalization.

When adjusting scoring, keep the index schema versioned and update the storage format section above.
