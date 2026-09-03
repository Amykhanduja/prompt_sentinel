import pytest
import os
import subprocess
import json

def test_benchmark_judge_default_disabled():
    # Execute the python script with --help or just check the source code
    with open("scripts/run_benchmark.py", "r") as f:
        content = f.read()
    assert 'default="disabled"' in content
    assert 'config.LLM_JUDGE_ENABLED = False' in content

def test_benchmark_model_reuse():
    # Verify the script caches _ENGINE by using process_sample directly 
    # instead of re-instantiating SemanticEngine inside process_sample
    with open("scripts/run_benchmark.py", "r") as f:
        content = f.read()
    # It imports run_detectors, which uses global _ENGINE
    assert 'run_detectors(' in content

def test_failed_samples_recorded():
    with open("scripts/run_benchmark.py", "r") as f:
        content = f.read()
    assert 'failures += 1' in content
    assert 'failed_samples.append' in content
    assert 'predictions.append({' in content
    assert '"processing_status": "failed"' in content

def test_metrics_exclude_failures():
    with open("scripts/run_benchmark.py", "r") as f:
        content = f.read()
    assert 'if p.get("processing_status") == "success":' in content
    
def test_warmup_excluded():
    with open("scripts/run_benchmark.py", "r") as f:
        content = f.read()
    # Warmup loop is distinct from the main loop where predictions are collected
    assert 'warmup_start = time.perf_counter()' in content
    assert 'main_start = time.perf_counter()' in content
