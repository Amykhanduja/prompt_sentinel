# PromptSentinel: Engine Upgrade Documentation

This document outlines all the major architectural upgrades, new features, and security enhancements implemented into the **PromptSentinel** prompt injection detection engine. The goal of these upgrades was to drastically reduce false positives, catch obfuscated attacks, and provide enterprise-grade explainability.

---

## 1. Preprocessing & Normalization Pipeline Upgrades
To prevent attackers from bypassing the regex detectors using text obfuscation, we upgraded the preprocessing pipeline to automatically normalize malicious text before it reaches the detection engine.

- **OCR Normalization**: Corrects common Optical Character Recognition (OCR) style character replacements when confidence is high. For example, it normalizes `ign0re` to `ignore`, `pr0mpt` to `prompt`, `rn` to `m`, and `vv` to `w`.
- **Unicode Confusable Normalization**: Maps Unicode homoglyphs (characters that look identical but have different underlying byte values) to their standard ASCII equivalents. For example, replacing a Cyrillic `і` with a Latin `i`.
- **Spacing Normalization**: Cleans up spacing-based attacks, removing zero-width spaces and collapsing artificially spaced-out words (e.g., `i g n o r e` becomes `ignore`).

## 2. Fuzzy Matching Integration
We introduced a **Fuzzy Matcher** to act as a safety net for the Regex detectors, specifically targeting intentional spelling mistakes and typos that evade hardcoded rules.

- **Edit-Distance Matching**: Implemented `RapidFuzz` (Levenshtein distance) to calculate the similarity between user input and known injection keywords.
- **Catching Typos**: Successfully catches variations like `ignroe`, `ihnore`, `igonre`, and `ig-nore` mapping them all back to the root trigger word "ignore".
- **Graceful Fallback**: Integrated sequentially into the pipeline: `Regex -> Fuzzy -> Semantic`. If the regex engine fails to find a direct match, the fuzzy matcher sweeps the prompt before it is passed to the heavy AI models.

## 3. Pluggable Embedding Abstraction
We decoupled the semantic engine from its hardcoded embedding model (`all-MiniLM-L6-v2`) to allow enterprise users to easily upgrade to newer, more powerful AI models.

- **EmbeddingProvider Interface**: Built a modular abstraction layer supporting multiple embedding backends.
- **Model Support**: Added out-of-the-box support for modern models like `BAAI/bge-base-en-v1.5` and `gte-large`.
- **Automatic Indexing**: The engine automatically detects when the embedding model is changed in the configuration and seamlessly rebuilds the semantic knowledge base index on the fly.

## 4. Cross-Encoder Reranking
We overhauled the semantic search retrieval process to fix false positives caused by generic vector similarity.

- **Global Candidate Retrieval**: The embedding model now acts as a broad "first pass", fetching the Top-20 nearest examples globally across the entire knowledge base.
- **Cross-Encoder Scoring**: A heavy, highly accurate Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) takes those 20 candidates and reranks them.
- **Intent Evaluation**: Because Cross-Encoders evaluate the *logical relationship* and *topical intent* between two sentences (rather than just spatial distance), the engine easily distinguishes between a benign question (e.g., "What is prompt injection?") and an actual attack.

## 5. Multi-Class Semantic Classifier
We evolved the semantic detector from a simple "Nearest Neighbor" lookup tool into a true **Machine Learning Classifier**.

- **On-The-Fly Training**: The engine consumes the raw semantic knowledge base (JSON files containing canonical, paraphrased, typo, and aggressive examples) and trains a multi-class model in memory.
- **SAFE Class Decoupling**: All benign/negative examples across the system are collapsed into a generic "SAFE" class. If the model predicts "SAFE" as the Top-1 intent, it immediately halts the detection, drastically reducing false positives.
- **Model Configurability**: Built support for `logistic_regression`, `linear_svm`, and `mlp` (Multi-Layer Perceptron), hot-swappable via `config.py`.
- **Probability Noise Filtering**: Implemented a mathematical noise floor (16% probability minimum). Overlapping techniques (e.g., *Thought Simulation* vs *Roleplay Injection*) that pass this threshold are returned concurrently as parallel detections.

## 6. Calibrated Confidence & Evidence Fusion
We completely rewrote how the `Fusion` engine calculates and reports the severity of an attack, replacing raw float similarities with enterprise-grade deterministic explanations.

- **Percentage Scoring**: The engine now outputs a strict calibrated percentage (e.g., `92%`) alongside qualitative labels (`Very High`, `High`, `Medium`, `Low`).
- **Dynamic Factor Aggregation**: The final score mathematically aggregates:
  - Base Embedding Similarity
  - Cross-Encoder Reranked Score
  - ML Classifier Probability
  - Negative Similarity Deductions
- **Deterministic Agreement Bonuses**: If multiple engines catch the same attack, the Fusion engine applies algorithmic bonuses (e.g., `+20%` if the Regex engine agrees with the Semantic engine, `+10%` for Fuzzy agreement).
- **Machine-Readable Evidence**: Every detection now ships with an `evidence` array, detailing the exact metrics and mathematical logic the engine used to reach its conclusion.
- **Risk Engine Compatibility**: The downstream Risk Engine was patched to seamlessly parse these new percentage formats back into mathematical floats, ensuring the global severity dashboard remains fully functional.
