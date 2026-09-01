# Phase 17.1 — LLM Judge Architecture Audit

## 1. Existing Detection Pipeline
The actual runtime execution flow of PromptSentinel currently follows this path:
1. `app.py:scan_text()` receives the prompt.
2. `preprocessing/pipeline.py:preprocess_prompt()` creates the normalized prompt.
3. `detectors/engine.py:run_detectors()` orchestrates detection:
   - Evaluates a series of regex detectors (e.g., `detect_override`, `detect_dan`).
   - Invokes the semantic pipeline via `semantic_engine.py:detect_semantic()` (BGE -> Top 20 -> Cross Encoder -> Top 3 -> Classifier).
   - Fuses both signal sources together using `fusion.py:fuse_detections()`.
4. The resulting `detections` array is passed to `scoring/risk_engine.py:calculate_risk()`.
5. The `risk` dictionary determines the `action` via `policies/policy_engine.py:evaluate_policy()`.
6. Results are returned as a `ScanResponse` object and logged/broadcasted.

## 2. Existing LLM Infrastructure
**Result: None.**
A complete repository scan for `LLM`, `gemini`, `openai`, `API_KEY`, etc. verified that there are currently NO API clients, schemas, prompts, or provider classes. The keywords exist solely within taxonomy documentation (e.g., `attack_taxonomy.md`) and mock JSON dataset files used for testing.

## 3. Configuration
**Result: None.**
The existing `config.py` and `.env` handle PostgreSQL connection settings and semantic ML thresholds. There are currently no configuration variables for API keys or external models. 

## 4. Confidence Architecture (Uncertainty Boundary)
The current representation of "uncertainty" in the system is managed inside `fusion.py:fuse_detections()`.
The function computes a `score` (0-100) based on regex agreement, embedding similarity, cross-encoder scores, and classifier probabilities.
It maps this `score` into a discrete `confidence_level`:
- `Very High`: >= 90
- `High`: 75-89
- `Medium`: 50-74
- `Low`: < 50

**Conclusion:** The uncertainty boundary is natively represented by detection items assigned a `Medium` or `Low` `confidence_level`.

## 5. Recommended Insertion Point
The LLM Judge should be inserted into **`detectors/engine.py:run_detectors()`**, immediately *after* `fuse_detections(regex_detections, semantic_detections)` and *before* it returns to `app.py`.

**Why:**
- By evaluating the `detections` array returned by `fuse_detections`, the system can conditionally invoke the LLM Judge *only* if the fused detections present boundary confidence (e.g., all detections are `Medium` or `Low`, or if semantic and regex disagree).
- It prevents modifying the complex scoring and penalty logic inside `scoring/risk_engine.py`.
- It keeps the Phase 16 semantic pipeline completely pristine. 

## 6. Phase 16 Regression Safety
Because the LLM Judge will be inserted post-fusion, the semantic engine (`SemanticEngine.detect`) and the underlying BGE / Cross-Encoder / Classifier layers will be entirely bypassed by the LLM Judge code. Phase 16 will remain untouched and its regression tests will continue to pass.

## 7. Future Judge Input
The LLM Judge will require the minimum context necessary to make a second opinion:
- `original_prompt`
- `normalized_prompt` (if obfuscation was used)
- The current tentative `detections` array (which contains `technique`, `name`, `confidence_level`, and `matched_examples`).

## 8. Future Judge Output
The LLM Judge should output a structured JSON schema compatible with the existing list of detections so it can seamlessly replace or append to the `fuse_detections` output.
```json
{
    "technique": "PT-018",
    "name": "Roleplay & Persona Adoption",
    "detector": "llm_judge",
    "confidence_level": "High",
    "confidence": 0.95,
    "evidence": ["LLM evaluation: Explict persona adoption detected."]
}
```

## 9. Provider Architecture
We will implement a `BaseLLMProvider` interface that exposes an `evaluate(prompt, context)` method. 
Implementations (e.g., `GeminiProvider` and `OpenAIProvider`) will subclass this interface. A factory method will resolve the active provider based on a `.env` variable (e.g., `LLM_PROVIDER=gemini`).

## 10. Failure Handling
The LLM Judge must act as a **conditional escalation layer, not a single point of failure.**
If the LLM provider times out, returns malformed JSON, throws an authentication error, or exceeds rate limits:
1. The error will be caught via a broad `try/except` block.
2. The error will be logged.
3. The function will safely `return` the original `detections` array passed from `fuse_detections`. 
This guarantees the scan always completes.

## 11. Privacy & Security
**Privacy:** The `original_prompt` will leave the enterprise boundary and be transmitted to a third-party LLM provider. This implies potential PII/sensitive data leakage. 
**Security:** API Keys must be loaded dynamically via environment variables or secret managers, never hardcoded. 

## 12. Testing Plan
The Phase 17 tests will be isolated to a new directory: `tests/phase17/`
Proposed tests:
- `test_llm_judge.py`: Validates structured LLM parsing.
- `test_llm_fallback.py`: Validates that exceptions fall back safely to Phase 16 detections.
- `test_uncertainty_routing.py`: Validates the conditional trigger logic (only activating the judge for Medium/Low signals).
- `test_llm_provider.py`: Validates provider instantiation via interface.

*(Audit completed. No active code was modified.)*
