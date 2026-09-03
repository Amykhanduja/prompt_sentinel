# Phase 19.10 — Benchmark Baseline Reconciliation & Final Validation

## 1. Objective
Reconcile an unexplained regression in benchmark metrics between Phase 19.6 and Phase 19.8, determine the root cause through artifact analysis and independent reproduction, and establish a single reproducible authoritative baseline for Phase 19.x.

## 2. Why reconciliation was necessary
The Phase 19.6 report stated a Recall of 70.03%, while the subsequent Phase 19.8 control run registered a Recall of 61.18% without intended detector or model logic changes. Accurate performance evaluation demands a mathematically sound understanding of exactly what caused this 9% recall collapse.

## 3. Phase 19.6 reported metrics
* Accuracy: 76.40%
* Precision: 96.74%
* Recall: 70.03%
* F1: 81.25%

## 4. Phase 19.8 reported metrics
* Accuracy: 69.94%
* Precision: 96.29%
* Recall: 61.18%
* F1: 74.82%

## 5. Phase 19.9 reported metrics
* Accuracy: 74.42%
* Precision: 96.62%
* Recall: 67.32%
* F1: 79.35%

## 6. Artifact inventory
All raw prediction artifacts were independently validated in `datasets/benchmark/results/v1.0.0/`:
- **Phase 19.6** (`20260904_031339`): `intfloat/multilingual-e5-base`, `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
- **Phase 19.8** (`20260904_041519`): Added `taxonomy_version: v19_8`
- **Phase 19.9** (`20260904_044844`): Deterministic rules adjusted.

## 7. Benchmark identity verification
The `samples.jsonl` fingerprint is exactly consistent across all evaluation runs. 
- 5,000 Total Samples (IDs intact)

## 8. Independently reproduced metrics
Using a raw counting script directly over `predictions.jsonl`:

| Run          | TP | TN | FP | FN | Accuracy | Precision | Recall | F1 |
| ------------ | -: | -: | -: | -: | -------: | --------: | -----: | -: |
| 19.6         | 2556 | 1264 |   86 | 1094 |    76.40% |     96.74% |  70.03% | 81.25% |
| 19.8 control | 2233 | 1264 |   86 | 1417 |    69.94% |     96.29% |  61.18% | 74.82% |
| 19.9         | 2457 | 1264 |   86 | 1193 |    74.42% |     96.62% |  67.32% | 79.35% |

*The independently calculated numbers perfectly match the reported historical results.*

## 9. Class-distribution verification
- 3,650 Malicious samples -> TP + FN
- 1,350 Benign samples -> TN + FP
- 100% agreement across all runs.

## 10. Sample-level transition analysis
Transitions from Phase 19.6 to Phase 19.8:
- **TP(19.6) -> FN(19.8)**: 332 regressions
- **FN(19.6) -> TP(19.8)**: 9 corrections (Semantic Hindi/SI drift captured)

Transitions from Phase 19.8 to Phase 19.9:
- **FN(19.8) -> TP(19.9)**: 229 corrections (Stored Injection contextual regex fix)
- **TP(19.8) -> FN(19.9)**: 5 regressions

## 11. Git/configuration comparison
- `detectors/engine.py`: Unchanged between 19.6 and 19.8.
- `semantic/knowledge_base.py`: Unchanged except loading logic.
- **Taxonomy (`v19_8`)**: Added 10 benign negative examples into the `negative_examples` array for *every* technique (total of 160 negatives).

## 12. Root cause of 19.6 -> 19.8 discrepancy
**Hypothesis Validated**: The drop from 70.03% to 61.18% was entirely caused by the taxonomy `negative_examples` injection acting on the ML classifier. 
1. In `semantic/classifier.py`, `negative_examples` are concatenated and labeled as the `SAFE` class. 
2. In Phase 19.8, 160 new benign security examples were injected into `negative_examples`.
3. This massive expansion of the `SAFE` decision boundary caused the Logistic Regression classifier to overwhelmingly classify boundary cases as `SAFE`.
4. In `semantic_engine.py::_detect_unified`, if `predicted_pt == "SAFE"`, it explicitly drops the candidate and returns `[]`. 
5. As a result, 332 attacks were discarded by the classifier entirely, resulting in a `0.0000` risk score (TP -> FN).

## 13. Phase 19.9 attribution analysis
Phase 19.9 intentionally avoided modifying the ML semantic pipeline and strictly updated the deterministic pattern matchers in `detectors/stored_injection_detector.py`. 
- 229 exact corrections occurred.
- Since deterministic matchers bypass the classifier and immediately fuse via `fusion.py`, this effectively overrode the classifier's `SAFE` hallucination specifically for Stored Injection.

## 14. Authoritative baseline table
**Authoritative Baseline (Phase 19.9)**:
* Accuracy: 74.42%
* Precision: 96.62%
* Recall: 67.32%
* F1: 79.35%

*Note*: This baseline inherently suffers from the over-weighted `SAFE` class boundary regression introduced in 19.8. The `v1` taxonomy (Phase 19.6) semantic recall of 70.03% remains technically superior on non-deterministic vectors, but Phase 19.9 represents the canonical deterministic remediation state. 

## 15. Security/regression analysis
False positives remained strictly at 86 across all phases. The regex expansions for stored injection produced zero new false positives on benign RAG/instruction boundaries. 

## 16. Phase 18 isolation
Confirmed zero state leak. `SELECT COUNT(*) FROM feedback` returned 0. 

## 17. Tests
All regression tests passing (Phase 16-19.10). `test_phase19_10_baseline_reconciliation.py` written and verified.

## 18. Historical metric discrepancies
The historical reporting was mathematically accurate. The regression was not an artifact bug, but a genuine classifier collapse caused by asymmetric negative class expansion in the taxonomy.

## 19. Final conclusion
The baseline discrepancy is fully resolved. Taxonomy negative examples act globally via the classifier, meaning blindly appending negative examples dilutes the detection boundary. Phase 19.9's deterministic fallback correctly masked this deficiency for stored injection, but the semantic classifier itself is currently nerfed.

## 20. Recommendation for the next phase
Proceed to Phase 20 (Production Optimization). In a future taxonomy release, negative examples should be handled via threshold adjustments or contrastive loss, rather than directly inflating a global `SAFE` class in a linear classifier. 
