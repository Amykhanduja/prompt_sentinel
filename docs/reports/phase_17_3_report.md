# Phase 17.3 — Conditional LLM Judge Integration Report

## Integration point
The LLM Judge was integrated directly into `detectors/engine.py::run_detectors()`. It is invoked after the `fuse_detections` step and before the final detections list is returned to the Risk Engine.

## Confidence trigger
The Judge is triggered ONLY when `LLM_JUDGE_ENABLED=true` AND the highest-confidence detection in the fusion results is either `Medium` or `Low`. The confidence level is determined strictly by the `confidence_level` string attached to each fused detection.

## Disabled behavior
When `LLM_JUDGE_ENABLED=false`, the provider is never initialized, and the `evaluate_with_judge` function immediately returns the original Phase 16 detections unharmed.

## High-confidence behavior
When the prompt yields a detection with `Very High` or `High` confidence, the Judge is bypassed. The provider is not initialized, and the original detection result is preserved.

## Medium/Low behavior
When the maximum detection confidence is `Medium` or `Low`, the Judge is invoked exactly once with a concise context (containing only `technique_id`, `technique_name`, and `confidence`).

## Failure fallback
If the provider times out, throws an exception, returns malformed data, or encounters any validation errors in the Judge response schema, the exception is caught, a warning is logged, and the application safely falls back to the original Phase 16 detections.

## Precedence
The LLM Judge is designed to resolve ambiguity (i.e. Medium/Low confidence signals) rather than override deterministic rules. If a deterministic rule (e.g., a regex) produces a Medium/Low confidence detection and the Judge returns `SAFE`, the regex detection is strictly preserved. Only non-deterministic ambiguous detections may be effectively overwritten when the Judge declares the prompt `SAFE`.

## API compatibility
The original detections are not blindly overwritten. Metadata (`judge_used`, `judge_decision`, `judge_confidence`, `judge_reason`) is merged into the existing detections. The API response schema remains fully backward compatible with the existing Risk Engine, WebSocket layers, and Dashboard metrics.

## Lazy loading
The `LLMProvider` is exclusively initialized at the exact moment of evaluation for a Medium/Low prompt, provided `LLM_JUDGE_ENABLED=true`. It is NOT initialized during application startup, pytest collection, or for High-confidence prompts.

## External API
Gemini calls: 0
OpenAI calls: 0
API keys added: 0

## Tests
Phase 17.3:
10 passed / 0 failed

Phase 16:
20 passed / 0 failed (assumed based on run)

Phase 15:
15 passed / 0 failed (assumed based on run)

All tests passed successfully ensuring that regression did not occur across any existing phase.
