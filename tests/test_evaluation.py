import pytest
import os
import tempfile
import json

from evaluation.dataset_loader import validate_dataset, load_dataset, merge_datasets
from evaluation.metrics import (
    compute_classification_metrics,
    compute_overall_metrics,
    compute_per_technique_metrics,
    compute_performance_metrics
)
from evaluation.confusion_matrix import (
    generate_overall_confusion_matrix,
    generate_binary_confusion_matrix
)
from evaluation.statistics import analyze_false_positives, analyze_false_negatives
from evaluation.report_generator import generate_reports

# ----------------- Dataset Validation Tests ----------------- #

def test_validate_dataset_valid():
    data = [
        {"id": "1", "prompt": "test", "expected": ["PT-009"], "severity": "high"},
        {"id": "2", "prompt": "benign test", "expected": ["benign"], "severity": "low"}
    ]
    assert validate_dataset(data) == True

def test_validate_dataset_missing_field():
    data = [
        {"id": "1", "prompt": "test", "expected": ["PT-009"]}
    ]
    with pytest.raises(ValueError, match="Missing required field"):
        validate_dataset(data)

def test_validate_dataset_duplicate_id():
    data = [
        {"id": "1", "prompt": "test1", "expected": ["PT-009"], "severity": "high"},
        {"id": "1", "prompt": "test2", "expected": ["PT-012"], "severity": "high"}
    ]
    with pytest.raises(ValueError, match="Duplicate id"):
        validate_dataset(data)

def test_validate_dataset_invalid_pt():
    data = [
        {"id": "1", "prompt": "test", "expected": ["INVALID"], "severity": "high"}
    ]
    with pytest.raises(ValueError, match="Invalid PT number"):
        validate_dataset(data)

# ----------------- Metrics Tests ----------------- #

def test_compute_classification_metrics():
    res = compute_classification_metrics(tp=10, fp=2, tn=20, fn=3)
    assert res["accuracy"] == (10 + 20) / 35
    assert res["precision"] == 10 / 12
    assert res["recall"] == 10 / 13
    assert "f1_score" in res

def test_compute_overall_metrics():
    results = [
        {"expected": ["PT-009"], "detections": [{"technique": "PT-009"}]}, # TP
        {"expected": ["benign"], "detections": [{"technique": "PT-012"}]}, # FP
        {"expected": ["PT-012"], "detections": []},                        # FN
        {"expected": ["benign"], "detections": []}                         # TN
    ]
    metrics = compute_overall_metrics(results)
    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5

def test_compute_per_technique_metrics():
    results = [
        {"expected": ["PT-009"], "detections": [{"technique": "PT-009"}]}, # TP PT-009
        {"expected": ["benign"], "detections": [{"technique": "PT-012"}]}, # FP PT-012
        {"expected": ["PT-012"], "detections": []}                         # FN PT-012
    ]
    metrics = compute_per_technique_metrics(results)
    
    assert "PT-009" in metrics
    assert metrics["PT-009"]["support"] == 1
    assert metrics["PT-009"]["true_positive_rate"] == 1.0
    
    assert "PT-012" in metrics
    assert metrics["PT-012"]["support"] == 1
    assert metrics["PT-012"]["false_positive_rate"] > 0

# ----------------- Confusion Matrix Tests ----------------- #

def test_confusion_matrix_generation():
    results = [
        {"expected": ["PT-009"], "detections": [{"technique": "PT-009"}]}, 
        {"expected": ["PT-009"], "detections": [{"technique": "PT-012"}]}, 
        {"expected": ["PT-012"], "detections": []}                         
    ]
    cm = generate_overall_confusion_matrix(results)
    assert cm["PT-009"]["PT-009"] == 1
    assert cm["PT-009"]["PT-012"] == 1
    assert cm["PT-012"]["Unknown"] == 1

# ----------------- False Pos/Neg Tests ----------------- #

def test_analyze_false_positives():
    results = [
        {"id": "1", "prompt": "Hello", "expected": ["benign"], "detections": [{"technique": "PT-012", "confidence": 0.9}]},
        {"id": "2", "prompt": "Bad", "expected": ["PT-009"], "detections": [{"technique": "PT-009", "confidence": 0.9}]}
    ]
    fps = analyze_false_positives(results)
    assert len(fps) == 1
    assert fps[0]["id"] == "1"
    assert fps[0]["detected_pt"] == "PT-012"

# ----------------- Report Generation Tests ----------------- #

def test_report_generation():
    report_data = {
        "overall_metrics": {"accuracy": 0.9},
        "per_technique_metrics": {"PT-009": {"f1_score": 0.9, "precision": 0.9, "recall": 0.9, "support": 10}},
        "false_positives": [{"id": "1", "prompt": "hello", "detected_pt": "PT-012", "confidence": 0.9}],
        "false_negatives": []
    }
    with tempfile.TemporaryDirectory() as tmpdirname:
        j, m, c = generate_reports(report_data, tmpdirname)
        assert os.path.exists(j)
        assert os.path.exists(m)
        assert os.path.exists(c)
        
        with open(j, 'r') as f:
            d = json.load(f)
            assert d["overall_metrics"]["accuracy"] == 0.9
