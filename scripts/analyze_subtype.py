import json
import glob

latest_dir = sorted(glob.glob("datasets/benchmark/results/v1.0.0/*"))[-1]
preds = [json.loads(line) for line in open(latest_dir + "/predictions.jsonl")]

orig_samples = {}
with open("datasets/benchmark/v1/samples.jsonl") as f:
    for line in f:
        s = json.loads(line)
        orig_samples[s["id"]] = s
        
stats = {}
for p in preds:
    orig = orig_samples[p["id"]]
    st = orig.get("subtype", "unknown")
    if st not in stats:
        stats[st] = {"tp":0, "tn":0, "fp":0, "fn":0}
        
    true_mal = p["ground_truth"] == "malicious"
    pred_mal = p["is_malicious"]
    
    if true_mal and pred_mal: stats[st]["tp"] += 1
    elif true_mal and not pred_mal: stats[st]["fn"] += 1
    elif not true_mal and pred_mal: stats[st]["fp"] += 1
    else: stats[st]["tn"] += 1
    
out = []
for st, v in stats.items():
    sup = v["tp"] + v["tn"] + v["fp"] + v["fn"]
    if v["tp"] + v["fn"] > 0: # Only malicious
        rec = v["tp"] / (v["tp"] + v["fn"])
        out.append((st, rec, v["fn"], sup))

out.sort(key=lambda x: x[1])
for st, rec, fn, sup in out[:15]:
    print(f"Subtype: {st}, Recall: {rec:.4f}, FN: {fn}, Support: {sup}")
