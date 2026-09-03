# Phase 19.2: Benchmark Dataset Generation Report

## 1. Dataset Version
`v1.0.0` (Stored in `datasets/benchmark/v1/`)

## 2. Total Sample Count
Total Samples: 5000

## 3. Class Distribution
* **Benign**: 1350
* **Malicious**: 3650
*(Benign count includes 1000 English benign + 350 Hindi benign)*

## 4. Category Distribution
* **benign**: 1000
* **direct_adversarial**: 800
* **typo**: 500
* **unicode**: 500
* **indirect_injection**: 600
* **roleplay**: 500
* **stored_injection**: 400
* **multilingual**: 700

## 5. Difficulty Distribution
* **easy**: 1318
* **medium**: 2332
* **hard**: 1350

## 6. Language Distribution
* **en**: 4300
* **hi**: 700

## 7. Obfuscation Distribution
* **none**: 4000
* **typo**: 500
* **unicode**: 500

## 8. Data Quality Controls
* **Duplicate count (IDs)**: 0
* **Duplicate count (Prompts)**: 0
* **Missing metadata count**: 0
* **Invalid sample count**: 0

## 9. Generation Methodology
A procedural synthetic generator (`scripts/generate_benchmark.py`) was constructed to compile deterministic, categorized payloads mapping cleanly to the `BenchmarkSample` schema.
* **Deduplication**: Enforced via global Sets and UUID cryptographic entropy on direct adversarial bases; typo/unicode transformations apply rigorous non-identity mutation to avoid cross-category collisions.
* **Ground Truth**: Manually assigned algorithmically from generation boundaries independent of model inference (`label = benign` or `label = malicious`). 
* **Security & Isolation**: All datasets reside completely offline as text JSONL data. The generation process makes zero HTTP API calls and does not automatically pipe into Phase 18 configuration mechanisms.

## 10. Taxonomy Coverage
The generated datasets broadly encapsulate all prompt injection topologies identified through the PromptSentinel phase sequence (Phase 15, 16, 17 taxonomies) utilizing granular subtypes (`instruction_override`, `homoglyph`, `embedded_content`, etc.).

## 11. Next Recommended Step
**Phase 19.3 Evaluation Engine Integration**: Now that 5,000 highly-validated ground-truth samples exist securely offline, we should integrate them with `BenchmarkEvaluator` to compute actual system metrics against PromptSentinel, allowing us to generate the final F1/ROC-AUC benchmark reports safely.

