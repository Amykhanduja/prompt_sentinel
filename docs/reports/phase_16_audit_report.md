# Phase 16 Semantic Architecture Audit

## 1. Current semantic architecture
The current pipeline splits into two mutually exclusive paths based on the `SEMANTIC_MODE` configuration setting:

```text
app.py::scan()
  ↓
detectors/engine.py::run_detectors()
  ↓
semantic/semantic_engine.py::detect_semantic()
  ↓
semantic.embeddings.py::get_embedding()
  ↓
(SentenceTransformerProvider returns NumPy ndarray)
  ↓
IF SEMANTIC_MODE == "classifier":
   semantic/classifier.py::predict(embedding) (Scikit-Learn LogisticRegression/SVC/MLP)
ELSE:
   semantic/semantic_engine.py::_detect_nearest_neighbor()
     ↓
   Global cosine similarity across all techniques
     ↓
   Top-20 retrieved
     ↓
   IF ENABLE_CROSS_ENCODER:
       semantic/cross_encoder.py::predict_scores()
     ↓
   Top-3 retained
     ↓
   Detection generated based on threshold / confidence
```

## 2. Files involved

| File | Responsibility |
| ---- | -------------- |
| `app.py` | Orchestrates API routes and prompts the `scan_text` function. |
| `detectors/engine.py` | Combines Regex detectors with `detect_semantic` and fuses results. |
| `semantic/semantic_engine.py` | The main semantic logic hub managing similarity, reranking, and classification paths. |
| `semantic/embeddings.py` | API facade for embedding providers and global singleton caching. |
| `semantic/providers.py` | Concrete provider classes (`MiniLMProvider`, `BGEProvider`, `GTEProvider`). |
| `semantic/similarity.py` | Mathematical utilities (`numpy.dot`) for cosine similarity scoring. |
| `semantic/cross_encoder.py` | Handles lazy initialization and prediction using `SentenceTransformer CrossEncoder`. |
| `semantic/classifier.py` | Dynamically trains and predicts using Scikit-Learn (`LogisticRegression`, `SVC`, or `MLP`). |
| `semantic/knowledge_base.py` | Loads and validates semantic examples from JSON files. |
| `config.py` | Houses toggles (`ENABLE_CROSS_ENCODER`, `SEMANTIC_MODE`) and model identifiers. |

## 3. Current MiniLM implementation
- **Model name**: `sentence-transformers/all-MiniLM-L6-v2` (Set in `config.py` and strictly referenced by `MiniLMProvider`).
- **Loading location**: Lazily loaded via `SentenceTransformerProvider._load()` inside `semantic/providers.py`.
- **Embedding generation**: Handled natively by `SentenceTransformer.encode(..., convert_to_numpy=True, normalize_embeddings=True)`.
- **Dimensions**: Implicitly 384 dimensions (dictated by the MiniLM architecture).
- **Normalization**: PyTorch/SentenceTransformers L2 normalization is applied automatically.
- **Caching**: The model remains cached in the `_model` attribute of the provider singleton until `unload()` is called.

## 4. Current retrieval
- **Dataset**: Technique-specific JSON definitions located in `semantic/examples/*.json`.
- **Similarity algorithm**: Simple Dot Product (Cosine Similarity because inputs are normalized), implemented in `semantic/similarity.py`.
- **Current Top-K**: The engine fetches the global Top-20 candidates for cross-encoder reranking, then truncates to a strict Top-3.
- **Nearest-example behavior**: Confidence is calculated by evaluating the highest similarity score against a `negative_similarity` baseline penalty and a technique-specific `threshold`.

## 5. Current classifier
A true classifier **DOES exist**. `semantic/classifier.py` implements a dynamically-trained Scikit-Learn classifier (`LogisticRegression`, `SVC`, or `MLPClassifier`). It extracts embeddings from the semantic knowledge base on engine initialization, assigns them labels (or "SAFE" for negative examples), and fits a model. It returns top 3 classes and a calculated confidence. However, it currently acts as a complete alternative to nearest-neighbor search, rather than a final layer in a combined pipeline.

## 6. Current lazy-loading architecture
Lazy loading is rigorously enforced across all machine learning components:
- **Embedding Models**: `sentence_transformers.SentenceTransformer` is imported and instantiated exclusively inside the `_load()` method of `SentenceTransformerProvider`.
- **Cross Encoder**: `sentence_transformers.CrossEncoder` is imported and instantiated exclusively inside `load_model()` in `semantic/cross_encoder.py`.
- **Classifier**: The Scikit-Learn `_CLASSIFIER` is fit inside `train_classifier()` only when `detect_semantic` attempts to use it (or when explicitly called).

## 7. Configuration
Configuration resides in `config.py`. 
Supporting `BAAI/bge-base-en-v1.5` simply requires updating:
`EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"`
Because `semantic/embeddings.py::set_provider()` already dynamically maps the substring "bge" to instantiate `BGEProvider`.

## 8. Dependencies
All necessary dependencies are already installed in the environment:
- **BGE Provider / Cross Encoder**: `sentence-transformers==5.6.0`, `torch==2.13.0+cpu`
- **Classifier**: `scikit-learn==1.9.0`

## 9. Tests
Relevant integration tests include:
- `tests/test_semantic.py`
- `tests/test_engine.py`
- `tests/phase16/test_phase16_detection_context.py`
- `tests/phase16/test_phase16_risk.py`
- `tests/phase16/test_phase16_frontend.py`
They assert on API stability, integration context, threshold behavior, and risk output. They do not tightly couple to `384` dimensions or hardcode "MiniLM".

## 10. Recommended Phase 16 architecture
To accomplish the unified target pipeline:
```text
BGE -> Top 20 -> Cross Encoder -> Top 3 -> Classifier -> Detection
```

The minimum necessary refactor involves:
1. **`config.py`**: Update `EMBEDDING_MODEL` to the BGE model. Deprecate the exclusive `SEMANTIC_MODE` toggle.
2. **`semantic/semantic_engine.py`**: Consolidate `_detect_nearest_neighbor` and `_detect_classifier` into a single, unified `detect` flow. 
   - Extract the Top-20 candidates using BGE Cosine Similarity.
   - Rerank using the Cross Encoder and slice the Top-3.
   - Forward those Top-3 attributes (and/or the BGE embedding) to the Classifier to render a final verdict.
3. **`semantic/classifier.py`**: Update the Scikit-Learn logic to optionally consume the unified pipeline's output (either directly consuming the embedding, or training as an ensemble over Cross-Encoder probabilities).

## 11. Risks
- **`list` object has no attribute `size`**: This previous regression could resurface if the pipeline inadvertently routes raw Cross Encoder similarity scores (which are sometimes scalar lists or floats) into legacy code anticipating a NumPy array. The `convert_to_numpy=True` safeguard on `SentenceTransformerProvider` successfully mitigates this for embeddings.
- **pytest startup latency**: If BGE or the Cross Encoder is instantiated at the module level during the refactor, the test suite will block on model instantiation before executing tests. The lazy `load_model()` and `_load()` encapsulation must be strictly maintained.
