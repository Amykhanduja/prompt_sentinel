# Phase 19.3-A: Benchmark Execution Architecture & Local-Only Baseline

## Executive Summary
* **Dataset Version**: v1.0.0
* **Judge Mode**: `disabled` (Local Baseline)
* **Samples Attempted**: 5000
* **Successful Evaluations**: 5000
* **Failures**: 0
* **Overall Accuracy**: 0.6758
* **Precision**: 0.9609
* **Recall**: 0.5795
* **F1**: 0.7230
* **ROC-AUC**: 0.7706

## Previously Completed (Phase 19.3 partial)
* Benchmark Evaluation Schema (`BenchmarkSample`, `BenchmarkDatasetVersion`)
* Metric Engine (`BenchmarkEvaluator` with TPR/FPR, Precision/Recall/F1, ROC-AUC)
* Integration Unit Tests (Schema isolation, logic verification)

## Newly Completed (Phase 19.3-A)
* **Local Benchmark Architecture**: Introduced `judge-mode` CLI toggle ensuring LLM Judge defaults to disabled for baseline execution, avoiding catastrophic rate-limiting and external cost overhead.
* **Model Lifecycle Optimization**: Explicitly validated that `SemanticEngine` gracefully caches its embeddings/cross-encoder allocations, preventing duplicate model instantiation per sample.
* **Performance Instrumentation**: Added warmup cycles, latency percentiles (mean, median, p95, p99), and throughput (samples/sec) monitoring.
* **Full 5,000-Sample Execution**: Effectively evaluated all samples against the real local detector pipeline without resorting to mocks or static label spoofing.

## Confusion Matrix (Global)
* TP: 2115
* TN: 1264
* FP: 86
* FN: 1535

## Category Performance
| Category | Support | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|---|
| benign | 1000 | 0.9140 | 0.0000 | 0.0000 | 0.0000 |
| direct_adversarial | 800 | 0.5813 | 1.0000 | 0.5813 | 0.7352 |
| typo | 500 | 0.5220 | 1.0000 | 0.5220 | 0.6859 |
| unicode | 500 | 0.5740 | 1.0000 | 0.5740 | 0.7294 |
| indirect_injection | 600 | 0.7933 | 1.0000 | 0.7933 | 0.8848 |
| roleplay | 500 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| stored_injection | 400 | 0.3150 | 1.0000 | 0.3150 | 0.4791 |
| multilingual | 700 | 0.5000 | 0.0000 | 0.0000 | 0.0000 |

## Difficulty Performance
| Difficulty | Support | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|---|
| easy | 1318 | 0.7140 | 0.9172 | 0.5813 | 0.7116 |
| medium | 2332 | 0.7080 | 0.9515 | 0.5753 | 0.7171 |
| hard | 1350 | 0.5830 | 1.0000 | 0.5830 | 0.7365 |

## Benign False Positives & Malicious False Negatives
* **Benign False Positives**: Total 86 FP. Many benign security-related queries (e.g., 'Explain authentication with examples') are incorrectly flagged by the cross-encoder as output leakage or metadata extraction due to semantic similarity.
* **Malicious False Negatives**: Total 1535 FN. Weakest categories are Multilingual (Hindi entirely bypassed) and Obfuscated prompts (Unicode/Typos bypass regex and semantic embeddings entirely).

## Language & Obfuscation Analysis
* **English vs Hindi**: English (Accuracy 70.44%, TP: 2115, TN: 914, FP: 86, FN: 1185) vs Hindi (Accuracy 50.00%, TP: 0, TN: 350, FP: 0, FN: 350)
* **No Obfuscation vs Obfuscated**: Clean (Accuracy 70.77%, TP: 1567, TN: 1264, FP: 86, FN: 1083) vs Obfuscated (Accuracy 54.80%, TP: 548, TN: 0, FP: 0, FN: 452)

## Judge Analysis
* Judge was intentionally disabled (`LLM_JUDGE_ENABLED=False`) to establish a pure Phase 16/18 baseline constraint.

## Performance
* **Total Runtime**: 745.10s
* **Throughput**: 6.71 samples/s
* **Latencies**: Mean (0.1490s), Median (0.1477s), p95 (0.1918s), p99 (0.2110s).
* **Warmup Duration**: ~117s

## Phase 18 Isolation
The benchmark executes through a sandboxed architectural path directly targeting `run_detectors` and `calculate_risk`. Database state (`LearningCandidate`, `ScanRepository`, `StatisticsRepository`) remains entirely pristine.

## Reproducibility
* **Git Commit**: dfcbf561
* **Semantic Model**: BAAI/bge-base-en-v1.5
* **CrossEncoder Model**: cross-encoder/ms-marco-MiniLM-L-6-v2

