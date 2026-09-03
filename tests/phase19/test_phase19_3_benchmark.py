import pytest
import json
import os
import time
from unittest.mock import patch, MagicMock
from evaluation.benchmark_schema import BenchmarkSample, BenchmarkDatasetVersion, BenchmarkLabel
from evaluation.benchmark_metrics import BenchmarkEvaluator

# Fixture dataset version
@pytest.fixture
def dummy_dataset_version():
    return BenchmarkDatasetVersion(
        dataset_name="test_ds",
        dataset_version="v1.0.0",
        description="test",
        samples=[
            BenchmarkSample(id="1", prompt="test", label=BenchmarkLabel.MALICIOUS, attack_type="direct_adversarial", difficulty="easy", source="s", expected_behavior="e"),
            BenchmarkSample(id="2", prompt="test2", label=BenchmarkLabel.BENIGN, attack_type="benign", difficulty="easy", source="s", expected_behavior="e"),
        ]
    )

def test_prediction_mapping():
    evaluator = BenchmarkEvaluator("v1.0.0")
    samples = [
        BenchmarkSample(id="1", prompt="", label=BenchmarkLabel.MALICIOUS, attack_type="direct_adversarial", difficulty="easy", source="s", expected_behavior="e"),
    ]
    predictions = [
        {"is_malicious": True, "confidence_score": 0.8}
    ]
    res = evaluator.evaluate(samples, predictions)
    assert res["overall"]["tp"] == 1
    
def test_batch_evaluation(dummy_dataset_version):
    evaluator = BenchmarkEvaluator("v1.0.0")
    predictions = [
        {"is_malicious": True, "confidence_score": 0.9},
        {"is_malicious": False, "confidence_score": 0.1},
    ]
    res = evaluator.evaluate(dummy_dataset_version.samples, predictions)
    assert res["overall"]["accuracy"] == 1.0

def test_per_category_metrics(dummy_dataset_version):
    evaluator = BenchmarkEvaluator("v1.0.0")
    predictions = [{"is_malicious": True}, {"is_malicious": False}]
    res = evaluator.evaluate(dummy_dataset_version.samples, predictions)
    assert "direct_adversarial" in res["by_category"]
    assert res["by_category"]["direct_adversarial"]["tp"] == 1

def test_per_difficulty_metrics(dummy_dataset_version):
    evaluator = BenchmarkEvaluator("v1.0.0")
    predictions = [{"is_malicious": True}, {"is_malicious": False}]
    res = evaluator.evaluate(dummy_dataset_version.samples, predictions)
    assert "easy" in res["by_difficulty"]
    assert res["by_difficulty"]["easy"]["accuracy"] == 1.0

def test_roc_auc_integration(dummy_dataset_version):
    evaluator = BenchmarkEvaluator("v1.0.0")
    predictions = [{"is_malicious": True, "confidence_score": 0.9}, {"is_malicious": False, "confidence_score": 0.2}]
    res = evaluator.evaluate(dummy_dataset_version.samples, predictions)
    assert res["overall"]["roc_auc"] is not None

def test_failed_sample_handling():
    # If a sample fails, it should be excluded from evaluation (the runner handles this)
    # The runner creates N predictions for N successful samples
    evaluator = BenchmarkEvaluator("v1.0.0")
    samples = [BenchmarkSample(id="1", prompt="", label=BenchmarkLabel.MALICIOUS, attack_type="direct", difficulty="easy", source="s", expected_behavior="e")]
    predictions = [{"is_malicious": True}]
    res = evaluator.evaluate(samples, predictions)
    assert res["metadata"]["total_samples"] == 1

def test_reproducibility_metadata(dummy_dataset_version):
    evaluator = BenchmarkEvaluator("v1.0.0", system_version="commit123")
    res = evaluator.evaluate(dummy_dataset_version.samples, [{"is_malicious": True}, {"is_malicious": False}])
    assert res["metadata"]["system_version"] == "commit123"

def test_phase_18_isolation():
    # Verify no dependencies import sqlalchemy models unexpectedly
    from evaluation import benchmark_schema
    assert not hasattr(benchmark_schema, "LearningCandidate")

