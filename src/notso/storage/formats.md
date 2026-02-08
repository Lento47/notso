# Storage Formats

## Index Format (version 1)

The index is stored as JSON with the following structure:

```json
{
  "version": 1,
  "documents": [{"id": "doc-1", "text": "..."}],
  "idf": {"term": 1.23},
  "doc_vectors": {"doc-1": {"term": 0.45}},
  "doc_norms": {"doc-1": 0.78}
}
```

### Field descriptions

- `version`: Storage format version for the index.
- `documents`: Array of document metadata (id + full text).
- `idf`: Inverse document frequency per term.
- `doc_vectors`: TF-IDF weights per document and term.
- `doc_norms`: Precomputed vector norms for cosine similarity.
