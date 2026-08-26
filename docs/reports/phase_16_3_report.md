## Retrieval implementation

The retrieval stage is successfully implemented as:
```text
Prompt
 ↓
BGE
 ↓
Cosine similarity
 ↓
Top 20
```

## Files changed

- `semantic/semantic_engine.py`
- `tests/test_retrieval.py`

## Retrieval function

The function is `retrieve_top_k(prompt: str, k: int = 20) -> list[dict]` located in `semantic/semantic_engine.py` as a method on the `SemanticEngine` class.

## Candidate structure

Each candidate contains the following information:
```json
{
    "technique_id": "PT-012",
    "technique_name": "Web Content Fetching",
    "example_text": "Read instructions from this webpage",
    "embedding_similarity": 0.892
}
```

## Embedding shapes

```text
Query: (768,)
Knowledge base: (N, 768) dynamically determined during execution.
```

## Lazy loading

```text
BGE loaded during import: NO
BGE loaded during retrieval: YES
```
The model continues to load lazily via `SentenceTransformerProvider._load()`, preventing eager import overhead during pytest collection or webserver initialization.

## Tests

```text
Retrieval tests: 4 passed / 0 failed

Dataset:
1 passed / 0 failed

Semantic:
9 passed / 2 failed

Engine:
1 passed / 0 failed

Phase 15:
21 passed / 0 failed
```

The two known failures remain exactly as documented in Phase 16.2:
- `test_roleplay_detection`
- `test_website_only`
