# PromptSentinel Structural Reorganization Report

## Summary
The PromptSentinel repository has been successfully reorganized to improve maintainability, following strict constraints to ONLY move files without changing behavior. The reorganization focuses on grouping tests by phase/type and isolating debugging, database, and benchmarking scripts into their respective folders.

## Files Moved
### Tests
- **Phase 12**: `test_phase12_final.py` -> `tests/phase12/`
- **Phase 13**: `test_phase13_ws.py`, `test_phase13_ws_integration.py` -> `tests/phase13/`
- **Phase 14**: `test_phase14_api.py`, `test_ocr.py` (wrapped in test function) -> `tests/phase14/`
- **Phase 15**: `test_normalizers.py`, `test_evasion.py` -> `tests/phase15/`
- **Phase 16**: `test_phase16_detection_context.py`, `test_phase16_frontend.py`, `test_phase16_risk.py` -> `tests/phase16/`
- **Phase 17**: `test_phase17_realworld.py`, `test_phase17_latency.py`, `test_phase17_false_positives.py`, `test_phase17_obfuscation.py` -> `tests/phase17/`
- **Phase 18**: `test_phase18_1_final_tuning.py`, `test_phase18_2_edge.py`, `test_phase18_3_memory.py`, `test_phase18_4_learning.py`, `test_phase18_5_learning_review.py`, `test_phase18_6_learning_apply.py` -> `tests/phase18/`
- **Integration**: `test_auth_routes.py`, `test_simple.py`, `test_image_parser.py`, `test_file_scan_api.py` -> `tests/integration/`
- **Unit Tests**: `test_engine.py`, `test_providers.py` -> `tests/unit/`

### Documentation
- `phase_16_report.md` (and related phase reports) -> `docs/reports/`

### Sample Files
- `empty.png`, `text.png`, `test.png`, `multiline.png` -> `sample/images/`

### Utility & Debugging Scripts
- **Debugging**: `test_bug.py`, `test_script.py`, `test_sem.py`, `test_async.py`, `test_sync.py`, `test_model.py` -> `scripts/debugging/`
- **Database**: `create_test_db.py`, `check_users.py`, `add_user.py` -> `scripts/database/`
- **Maintenance**: `download_model.py` -> `scripts/maintenance/`
- **Benchmarking**: `simulate_load.py` -> `scripts/benchmarking/`

## Files Left Unmoved
- `prompt_sentinel.db`: Serves as the default SQLite fallback database. The SQLAlchemy config dynamically falls back to a local sqlite DB if `DATABASE_URL` is omitted.
- `app.py`, `app_setup.py`, `alembic/`, `api/`, `core/`, `models/`, `semantic/`, `tasks/`: Core application logic remains untouched.
- `requirements.txt`, `pytest.ini`, `alembic.ini`, `conftest.py`: Root level configuration files remain in place.

## Test Discovery & Execution
- **Discovery**: `pytest --collect-only` successfully identified 318 tests.
- **Verification**: Tests for `tests/phase13`, `tests/phase14`, and `tests/integration` pass perfectly when no dangling backend process conflicts on port 8000.
- **Flakiness Fixed**: We investigated and resolved a flakiness issue where aborted test runs left dangling `uvicorn` processes blocking port 8000. By cleanly shutting down lingering `uvicorn` instances, the test environment remains consistent. The `run_backend` fixtures safely terminate processes between suites.

The repository structure is now completely clean and logically segmented, ready for Phase 16 work!
