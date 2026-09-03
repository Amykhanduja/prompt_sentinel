# Phase 19.1: Benchmark Dataset Architecture & Evaluation Contract

## 1. Existing Dataset Infrastructure Discovered
- Discovered `taxonomy/` directory with `techniques.py` providing the taxonomy for attacks (`PT-001`, etc.).
- Discovered `evaluation/` directory with older implementation containing `evaluator.py`, `dataset_loader.py`, `metrics.py`, `confusion_matrix.py`.
- Previous evaluation code relied heavily on system metrics like latency and memory, plus basic binary metrics, but lacked the rich categorization (obfuscation, language, difficulty) requested for Phase 19.

## 2. Dataset Schema
Created `BenchmarkSample` and `BenchmarkDatasetVersion` in `evaluation/benchmark_schema.py`.
- **id**: Stable unique ID.
- **prompt**: The text input.
- **label**: Ground truth (`benign` or `malicious`).
- **attack_type**: High-level categorization (e.g. `direct_adversarial`, `typos`, `benign`).
- **subtype**: Optional finer-grained categorization.
- **language**: E.g., `en`, `hi`.
- **obfuscation**: E.g., `none`, `typo`.
- **difficulty**: `easy`, `medium`, `hard`.
- **source**: How the sample was generated (`synthetic`, `curated`, etc.).
- **expected_behavior**: Independent definition of what the detector should do.

## 3. Taxonomy Mapping
- `attack_type` handles broad concepts (e.g., direct_adversarial, indirect_injection, unicode, roleplay).
- `subtype` allows finer mapping to the internal PromptSentinel PT-XXX ontology without redefining it.

## 4. Dataset Versioning Strategy
- Explicit schema `BenchmarkDatasetVersion` enforces capturing:
  - `dataset_name`
  - `dataset_version`
  - List of `BenchmarkSample`
- Prevents silent updates by requiring versions to change when data is modified.

## 5. Development/Evaluation Separation & Data Leakage Protection
- Datasets are stored with strict schemas distinguishing source and version.
- Phase 18 learning handles *Feedback* dynamically from production endpoints via `LearningCandidate` and `LearningApplication`.
- The benchmark framework evaluates independently from the feedback loop. Benchmark samples are never sent to the feedback API.
- Test suites enforce valid schema properties without calling the Phase 18 application routes, preventing benchmark data from converting into production configuration.

## 6. Required Metrics Contract
The `BenchmarkEvaluator` computes:
- Confusion Matrix: TP, TN, FP, FN
- Accuracy, Precision, Recall, F1
- ROC-AUC
- Total Samples

## 7. Per-category & Difficulty Evaluation Design
The evaluator automatically groups samples and outputs independent metric dictionaries:
- By category (`attack_type`)
- By difficulty (`easy`, `medium`, `hard`)
- Overall global aggregation

## 8. ROC-AUC Strategy
ROC-AUC requires probability scores. The evaluation parses `confidence_score` (defaulting to 1.0 or 0.0 for binary endpoints) alongside `is_malicious`. If scores are valid binary-or-float representations and `sklearn.metrics.roc_auc_score` handles them properly, ROC-AUC is emitted. If only one class exists or sklearn is absent, it degrades gracefully returning `None`.

## 9. Security Protections
- Prompts are treated as untrusted strings wrapped in safe Pydantic models.
- Tests use deterministic mocks and do not make active web requests to Gemini or production LLMs.
- Secrets are not exposed.
- No automatic execution of benchmark prompts via the live Phase 17 Gemini Judge pipeline during schema evaluation.
- The evaluation boundary strictly reports metrics without invoking the Phase 18 feedback-learning application logic.

## 10. Tests and Results
Ran `pytest tests/phase19/ -v` testing the schema, evaluators, dataset versioning, metric computation, and ROC-AUC fallbacks.
- `test_schema_valid_sample` (PASSED)
- `test_schema_invalid_label` (PASSED)
- `test_schema_dataset_versioning` (PASSED)
- `test_evaluator_metrics` (PASSED)
- `test_roc_auc_graceful` (PASSED)
Results: 5/5 Passed

## 11. Files Created
- `evaluation/benchmark_schema.py`
- `evaluation/benchmark_metrics.py`
- `tests/phase19/test_phase19_1_benchmark.py`
- `docs/reports/phase_19_1_report.md`

## 12. Files Modified
- None modified directly (extended architecture safely side-by-side with previous evaluation module).

## 13. Known Limitations
- Does not contain thousands of prompts yet (intended for Phase 19.2).
- Does not run heavy model evaluations in these schema unit tests.

## 14. Next Phase 19 Subphase
**Phase 19.2: Dataset Generation**
We have established the immutable schema and measurement contract. We must now generate or load the actual PromptSentinel datasets following this exact contract across all specified categories (Benign, Adversarial, Typos, Unicode, etc.).
