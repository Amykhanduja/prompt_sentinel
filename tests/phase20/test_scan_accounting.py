import pytest
import os
import glob
import json
from database.connection import SessionLocal
from database.models.models import Scan
from database.models.feedback import Feedback

def test_api_statistics_returns_distinct_counts(auth_client):
    res = auth_client.get("/api/v1/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    
    kpis = data.get("kpis", {})
    assert "productionScans" in kpis
    assert "benchmarkEvaluations" in kpis
    assert "benchmarkData" in kpis
    
    # Test 6: No hardcoded benchmark count
    runs = sorted([d for d in glob.glob("datasets/benchmark/results/v1.0.0/*") if os.path.isdir(d) and not d.endswith("analysis")])
    if runs:
        with open(os.path.join(runs[-1], "manifest.json")) as f:
            manifest = json.load(f)
            expected_evals = manifest.get("sample_count", 0)
    else:
        expected_evals = 0
        
    assert kpis["benchmarkEvaluations"] == expected_evals
    
    # Just asserting it exists and is int (production could be 0 in test db initially)
    assert isinstance(kpis["productionScans"], int)

def test_benchmark_isolation():
    # Test 2 & 4: Benchmark execution does not contaminate DB
    db = SessionLocal()
    initial_scans = db.query(Scan).count()
    initial_feedback = db.query(Feedback).count()
    
    # Simulate a benchmark evaluation call directly
    from detectors.engine import run_detectors
    detections = run_detectors("This is a benchmark test prompt", source="benchmark")
    
    final_scans = db.query(Scan).count()
    final_feedback = db.query(Feedback).count()
    
    assert initial_scans == final_scans, "Benchmark run contaminated Scan table!"
    assert initial_feedback == final_feedback, "Benchmark run contaminated Feedback table!"
