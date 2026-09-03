import pytest
import json
import os

def test_19_6_metric_reproduction():
    preds_path = "datasets/benchmark/results/v1.0.0/20260904_031339/predictions.jsonl"
    assert os.path.exists(preds_path), "19.6 benchmark predictions must exist"
    
    tp, tn, fp, fn = 0, 0, 0, 0
    with open(preds_path) as f:
        for line in f:
            p = json.loads(line)
            if p["ground_truth"] == "malicious":
                if p["is_malicious"]: tp += 1
                else: fn += 1
            else:
                if p["is_malicious"]: fp += 1
                else: tn += 1
                
    assert tp == 2556
    assert tn == 1264
    assert fp == 86
    assert fn == 1094
    
    acc = (tp + tn) / (tp + tn + fp + fn)
    assert abs(acc - 0.7640) < 0.001

def test_fn_confidence_distribution():
    preds_path = "datasets/benchmark/results/v1.0.0/20260904_031339/predictions.jsonl"
    with open(preds_path) as f:
        for line in f:
            p = json.loads(line)
            if p["ground_truth"] == "malicious" and not p["is_malicious"]:
                assert p["raw_risk_score"] == 0, "All remaining FNs have exactly 0 risk score"

def test_fp_persistence():
    preds_19_6 = "datasets/benchmark/results/v1.0.0/20260904_031339/predictions.jsonl"
    preds_19_5 = "datasets/benchmark/results/v1.0.0/20260903_190036/predictions.jsonl"
    preds_19_3 = "datasets/benchmark/results/v1.0.0/20260903_175723/predictions.jsonl"
    
    def get_fps(path):
        fps = set()
        with open(path) as f:
            for line in f:
                p = json.loads(line)
                if p["ground_truth"] == "benign" and p["is_malicious"]:
                    fps.add(p["id"])
        return fps
        
    fp6 = get_fps(preds_19_6)
    fp5 = get_fps(preds_19_5)
    fp3 = get_fps(preds_19_3)
    
    assert len(fp6) == 86
    assert fp6 == fp5, "FPs identical between 19.5 and 19.6"
    assert fp6 == fp3, "FPs identical between 19.3 and 19.6"
