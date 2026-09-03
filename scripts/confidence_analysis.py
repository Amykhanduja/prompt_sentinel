import json, glob, os
import numpy as np
runs = [d for d in glob.glob("datasets/benchmark/results/v1.0.0/*") if os.path.basename(d) != "analysis"]
latest_dir = sorted(runs)[-1]
preds = [json.loads(line) for line in open(latest_dir + "/predictions.jsonl")]
    
groups = {"tp": [], "tn": [], "fp": [], "fn": []}

for p in preds:
    true_mal = (p["ground_truth"] == "malicious")
    pred_mal = p["is_malicious"]
    score = p.get("confidence_score", 0.0)
    
    if true_mal and pred_mal: groups["tp"].append(score)
    elif true_mal and not pred_mal: groups["fn"].append(score)
    elif not true_mal and pred_mal: groups["fp"].append(score)
    else: groups["tn"].append(score)
    
for g, scores in groups.items():
    if not scores:
        print(f"{g.upper()}: No samples")
        continue
    scores = np.array(scores)
    print(f"{g.upper()}: Mean={np.mean(scores):.4f}, Median={np.median(scores):.4f}, p25={np.percentile(scores, 25):.4f}, p75={np.percentile(scores, 75):.4f}")
    
    # Ranges
    vh = np.sum(scores >= 0.8)
    h = np.sum((scores >= 0.6) & (scores < 0.8))
    m = np.sum((scores >= 0.4) & (scores < 0.6))
    l = np.sum(scores < 0.4)
    print(f"  Very High: {vh}, High: {h}, Medium: {m}, Low: {l}")
