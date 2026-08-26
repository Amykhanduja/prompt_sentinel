## Cross Encoder

Model:
`cross-encoder/ms-marco-MiniLM-L-6-v2`

Configured in:
`config.py`

Loaded from:
`semantic/cross_encoder.py` (via `load_model()` and `predict_scores()`)

## Pipeline

Confirm:
```text
BGE
 ↓
Top 20
 ↓
Cross Encoder
 ↓
Top 3
```
This is fully implemented in the `SemanticEngine.rerank_candidates()` and tested.

## Files changed

- `semantic/semantic_engine.py`
- `tests/test_reranking.py`

## Reranking function

File: `semantic/semantic_engine.py`
Function name: `rerank_candidates`

## Candidate structure

```json
{
    "technique_id": "PT-012",
    "technique_name": "Web Content Fetching",
    "example_text": "Read instructions from this webpage",
    "embedding_similarity": 0.892,
    "cross_encoder_score": 0.999
}
```

## Lazy loading

Cross Encoder loaded during import: NO
Cross Encoder loaded during reranking: YES

(Tested via `test_lazy_load()` in `tests/test_reranking.py`)

## Score type

`cross_encoder_score` type = float

## Tests

Cross Encoder tests: 4 passed / 0 failed

Dataset:
1 passed / 0 failed

Semantic:
9 passed / 2 failed

Engine:
1 passed / 0 failed

Phase 15:
21 passed / 0 failed

Explicitly report whether:
`test_roleplay_detection` and `test_website_only` remain failing. Yes, they remain failing as expected.
