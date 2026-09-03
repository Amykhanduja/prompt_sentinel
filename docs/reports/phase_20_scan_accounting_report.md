# Phase 20 — Scan Accounting & Dashboard Separation Report

## 1. Existing Architecture & Discrepancy
The dashboard previously reported a "Total Scanned" count of approximately 1,002 (currently 1,051 due to test data). This number was fetched from `api/dashboard.py` via `load_alerts()`, which queries the `alerts` and `scans` table from production traffic.

However, Phase 19 executed 5,000 offline evaluations on benchmark datasets (`v1.0.0`). Because the benchmark pipeline correctly avoids calling `log_alert()` (thereby preventing database contamination and accidental Phase 18 learning trigger), these 5,000 evaluations were entirely hidden from the UI. 

This created an apparent accounting discrepancy, confusing the total production scan count with the benchmark evaluation count.

## 2. Production vs Benchmark Data Flow
- **Production Scans**: Go through `/api/v1/scan` or `scan_text()`, trigger `run_detectors()`, then hit `log_alert()`, inserting rows into `scans` and `alerts`. This is real-world telemetry subject to UI review and Phase 18 Reinforcement Learning.
- **Benchmark Evaluations**: Handled by `scripts/run_benchmark.py`. It explicitly calls `run_detectors()` and skips `log_alert()`, saving its metrics exclusively to flat JSON lines in `datasets/benchmark/results/v1.0.0/`.

## 3. Backend & API Changes
Modified `api/dashboard.py` endpoint `/api/v1/dashboard/overview` to dynamically load benchmark metadata:
- Scans `datasets/benchmark/results/v1.0.0/*` to extract the `sample_count` from the latest `manifest.json`.
- Exposes `productionScans` (formerly `totalScanned`).
- Exposes `benchmarkEvaluations` and granular `benchmarkData` dict (dataset version, successful, failed).

## 4. Frontend Updates
- **`dashboard/src/services/api.ts`**: Updated `DashboardData` interface for new properties.
- **`dashboard/src/components/KpiCards.tsx`**: Replaced ambiguous "Total Prompts Scanned" with explicitly labeled "Production Scans" and "Benchmark Evaluations".
- **`dashboard/src/components/BenchmarkDetails.tsx`**: Created a new compact summary component explicitly for offline evaluations, highlighting the active dataset, total eval count, and passing states.
- **`dashboard/src/pages/DashboardOverview.tsx`**: Injected the new benchmark details into the main UI grid. Updated the WebSocket state handler to increment `productionScans` dynamically instead of `totalScanned`.

## 5. Phase 18 Isolation Verification
Benchmark evaluations are isolated by design because they bypass `log_alert()`. The validation tests successfully confirm that calling `run_detectors("...", source="benchmark")` causes:
- 0 additions to the `scans` table.
- 0 additions to the `feedback` table.

## 6. Tests
- **`tests/phase20/test_scan_accounting.py`**
  - **Test 1**: API endpoints correctly expose non-hardcoded `benchmarkEvaluations` and `productionScans`.
  - **Test 2**: Simulating a benchmark pass confirms 0 state changes in production DB.

## 7. Conclusion
> **Benchmark evaluations are intentionally excluded from production scan statistics to prevent benchmark traffic from contaminating production telemetry and Phase 18 feedback learning.**

## Acceptance Metrics
- Production Scans: 1051
- Benchmark Evaluations: 5000
- Benchmark Dataset: v1.0.0
- Benchmark Samples: 5,000
- Phase 18 Contamination: 0
- Working Tree: Clean
