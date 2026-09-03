## Objective
LLM Judge observability and decision quality tracking.

## Architecture
```text
Deterministic Detection
        ↓
Confidence
        ↓
Conditional Judge
        ↓
Judge Outcome
        ↓
Final Detection
```

## Judge Outcomes
```text
NOT_INVOKED
CONFIRMED
OVERRIDDEN
ESCALATED
FALLBACK
```

## Security Guarantees
Strong deterministic evidence remains protected. High-confidence detections bypass the judge, and failures in the judge default to safe fallback.

## Observability
- provider
- model
- decision
- confidence
- technique
- outcome
- latency

## Testing
- Phase 17 tests: Passed
- Phase 16 tests: Passed
- full regression suite: Passed
