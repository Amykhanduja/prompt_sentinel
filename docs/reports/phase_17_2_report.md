# Phase 17.2 — LLM Judge Provider Abstraction Report

## 1. Provider Architecture
We established a provider-neutral interface in `llm/provider.py` featuring the `BaseLLMProvider` contract. This interface mandates two core async methods: `initialize()` (for deferred setup) and `evaluate(prompt: str)` (for inference). A provider factory getter `get_llm_provider()` is used to instantiate the specified provider dynamically, allowing for different backends (e.g., Gemini, OpenAI) in the future. We also created `llm/mock_provider.py` containing `MockProvider` and `ExceptionProvider` for robust isolated testing. The judge logic is housed in `llm/judge.py`, which validates output and wraps execution.

## 2. Configuration
The LLM Judge system leverages `os.getenv` for configuration within `config.py`. The following variables are supported:
- `LLM_JUDGE_ENABLED`: Toggles the judge component (`true` or `false`).
- `LLM_JUDGE_PROVIDER`: Identifies which provider implementation to load (e.g., `mock`).
- `LLM_JUDGE_TIMEOUT`: Configures the maximum timeout for the provider request.

## 3. Default Behavior
By default, the LLM Judge is **DISABLED** (`LLM_JUDGE_ENABLED=false`). When disabled, the judge safely falls back to returning the initial Phase 16 detections un-modified. 

## 4. Failure Behavior
In `llm/judge.py`, the `evaluate_with_judge()` method wraps the provider's execution in a broad `try-except` block. If the provider raises an exception (e.g., timeouts, missing configuration, internal errors), the judge emits a warning and safely returns the original detections, bypassing the Judge layer and falling back securely to the Phase 16 baseline.

## 5. Validation
The `validate_provider_output` function rigorously scrutinizes the dictionary returned by the provider. It validates:
- The `action` field matches `SAFE`, `MALICIOUS`, or `UNCERTAIN`.
- Malicious responses include both `technique_id` and `reasoning`.
- The `technique_id` maps to a known taxonomy technique, verifying that `tech_meta.get("name") != "Unknown Technique"` to prevent hallucinatory bypasses of the static dictionary generator in `taxonomy.techniques`.

## 6. Lazy Loading
The provider is strictly lazy-loaded. It is not initialized during Python import, FastAPI startup, or Pytest collection. The `get_llm_provider()` is invoked only within the context of execution, ensuring we do not establish network connections or incur initialization overhead unnecessarily.

## 7. Tests
Comprehensive unit tests have been written in `tests/phase17/test_llm_provider.py`. The suite tests:
- Provider evaluation and dictionary output structure.
- Output validation rules (validating taxonomy, catching bad structures).
- Fallback exception behavior.
- Configuration switch (`LLM_JUDGE_ENABLED`).
Baseline Phase 12-16 tests (specifically `test_semantic.py`, `test_engine.py`, `test_phase15_integration.py`, and `tests/phase16/`) were fully executed using the isolated test database, confirming backwards compatibility.

## 8. External API Confirmation
NO external LLM API calls, clients, SDKs (such as Gemini or OpenAI packages), or API keys have been integrated into this phase. The implementation focuses strictly on the internal provider abstraction interface and uses mocked providers for validation.
