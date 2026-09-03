import pytest
import os
import glob
import json

def test_benchmark_identity_and_class_distribution():
    with open('datasets/benchmark/v1/samples.jsonl') as f:
        samples = [json.loads(line) for line in f]
    assert len(samples) == 5000
    
    malicious = [s for s in samples if s['label'] == 'malicious']
    benign = [s for s in samples if s['label'] == 'benign']
    assert len(malicious) == 3650
    assert len(benign) == 1350

def test_artifacts_exist():
    runs = sorted([d for d in glob.glob("datasets/benchmark/results/v1.0.0/*") if os.path.isdir(d) and not d.endswith("analysis")])
    assert len(runs) >= 3, "Missing required baseline runs"

def test_phase18_isolation():
    from sqlalchemy import create_engine, text
    engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel_test")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM feedback")).scalar() == 0

def test_reconciliation_math():
    runs = sorted([d for d in glob.glob("datasets/benchmark/results/v1.0.0/*") if os.path.isdir(d) and not d.endswith("analysis")])
    run_19_9 = runs[-1]
    
    tp, tn, fp, fn = 0, 0, 0, 0
    with open(os.path.join(run_19_9, 'predictions.jsonl')) as f:
        for line in f:
            d = json.loads(line)
            if d['ground_truth'] == 'malicious':
                if d['is_malicious']: tp += 1
                else: fn += 1
            else:
                if d['is_malicious']: fp += 1
                else: tn += 1
    
    assert tp + fn == 3650
    assert tn + fp == 1350
