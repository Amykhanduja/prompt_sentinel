import json
import os
import glob
from collections import defaultdict

def calculate_metrics(preds_file):
    tp, tn, fp, fn = 0,0,0,0
    preds = {}
    with open(preds_file, 'r') as f:
        for line in f:
            d = json.loads(line)
            preds[d['id']] = d
            if d['ground_truth'] == 'malicious':
                if d['is_malicious']: tp += 1
                else: fn += 1
            else:
                if d['is_malicious']: fp += 1
                else: tn += 1
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1,
        'preds': preds
    }

def analyze():
    # Load samples
    samples = {}
    with open('datasets/benchmark/v1/samples.jsonl', 'r') as f:
        for line in f:
            s = json.loads(line)
            samples[s['id']] = s

    # Directories
    p19_6_dir = "datasets/benchmark/results/v1.0.0/20260904_031339"
    p19_8_dir = "datasets/benchmark/results/v1.0.0/20260904_041519"
    p19_9_dir = "datasets/benchmark/results/v1.0.0/20260904_044844"
    
    # Check if samples match
    with open(os.path.join(p19_6_dir, 'predictions.jsonl')) as f:
        p19_6_ids = {json.loads(x)['id'] for x in f}
    assert p19_6_ids == set(samples.keys()), "Sample mismatch!"
    
    res_19_6 = calculate_metrics(os.path.join(p19_6_dir, 'predictions.jsonl'))
    res_19_8 = calculate_metrics(os.path.join(p19_8_dir, 'predictions.jsonl'))
    res_19_9 = calculate_metrics(os.path.join(p19_9_dir, 'predictions.jsonl'))
    
    print(f"| Run          | TP | TN | FP | FN | Accuracy | Precision | Recall | F1 |")
    print(f"| ------------ | -: | -: | -: | -: | -------: | --------: | -----: | -: |")
    for name, r in [('19.6', res_19_6), ('19.8 control', res_19_8), ('19.9', res_19_9)]:
        print(f"| {name.ljust(12)} | {r['tp']:4} | {r['tn']:4} | {r['fp']:4} | {r['fn']:4} | {r['accuracy']*100:8.2f}% | {r['precision']*100:9.2f}% | {r['recall']*100:6.2f}% | {r['f1']*100:4.2f}% |")

    # Transitions 19.6 -> 19.8
    tp_fn = 0
    for sid in samples:
        if samples[sid]['label'] == 'malicious':
            pred6 = res_19_6['preds'][sid]['is_malicious']
            pred8 = res_19_8['preds'][sid]['is_malicious']
            if pred6 and not pred8:
                tp_fn += 1
                
    print(f"\nTP(19.6) -> FN(19.8) regressions: {tp_fn}")
    
    # Why did they regress? Let's check a few
    print("\nSample regressions 19.6 -> 19.8:")
    count = 0
    for sid in samples:
        if samples[sid]['label'] == 'malicious':
            pred6 = res_19_6['preds'][sid]['is_malicious']
            pred8 = res_19_8['preds'][sid]['is_malicious']
            if pred6 and not pred8:
                if count < 5:
                    s6 = res_19_6['preds'][sid]['raw_risk_score']
                    s8 = res_19_8['preds'][sid]['raw_risk_score']
                    print(f"ID {sid}: Score {s6:.4f} -> {s8:.4f} | Prompt: {samples[sid]['prompt'][:60]}")
                    count += 1
                
if __name__ == "__main__":
    analyze()
