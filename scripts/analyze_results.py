import json
import os
import glob
from collections import defaultdict

def main():
    results_dir = "datasets/benchmark/results/v1.0.0/"
    runs = sorted(glob.glob(os.path.join(results_dir, "*")))
    if not runs:
        print("No runs found")
        return
        
    latest_run = runs[-1]
    preds_path = os.path.join(latest_run, "predictions.jsonl")
    
    samples = []
    with open(preds_path, "r") as f:
        for line in f:
            samples.append(json.loads(line))
            
    # Language analysis (using language from the sample dict directly if available, wait, run_benchmark didn't inject language into preds.jsonl)
    # We need to fetch from the original dataset.
    dataset_path = "datasets/benchmark/v1/samples.jsonl"
    orig_samples = {}
    with open(dataset_path, "r") as f:
        for line in f:
            s = json.loads(line)
            orig_samples[s["id"]] = s
            
    # Combine
    for p in samples:
        orig = orig_samples[p["id"]]
        p["language"] = orig.get("language", "en")
        p["obfuscation"] = "yes" if "unicode" in orig.get("attack_type", "") or "typo" in orig.get("attack_type", "") else "no"
        p["prompt"] = orig.get("prompt", "")
        
    lang_stats = defaultdict(lambda: {"tp":0, "fp":0, "tn":0, "fn":0})
    obf_stats = defaultdict(lambda: {"tp":0, "fp":0, "tn":0, "fn":0})
    
    fps = []
    fns = []
    
    for p in samples:
        if p.get("processing_status") == "failed": continue
        
        true_mal = (p["ground_truth"] == "malicious")
        pred_mal = p["is_malicious"]
        
        l = p["language"]
        o = p["obfuscation"]
        
        if true_mal and pred_mal:
            lang_stats[l]["tp"] += 1
            obf_stats[o]["tp"] += 1
        elif true_mal and not pred_mal:
            lang_stats[l]["fn"] += 1
            obf_stats[o]["fn"] += 1
            fns.append(p)
        elif not true_mal and pred_mal:
            lang_stats[l]["fp"] += 1
            obf_stats[o]["fp"] += 1
            fps.append(p)
        else:
            lang_stats[l]["tn"] += 1
            obf_stats[o]["tn"] += 1
            
    # Compute accuracy for lang/obf
    for d in [lang_stats, obf_stats]:
        for k, v in d.items():
            tot = v["tp"]+v["fp"]+v["tn"]+v["fn"]
            v["acc"] = (v["tp"]+v["tn"])/tot if tot > 0 else 0
            
    print("### Language Breakdown ###")
    for k, v in lang_stats.items():
        print(f"{k}: ACC={v['acc']:.4f} (TP={v['tp']} TN={v['tn']} FP={v['fp']} FN={v['fn']})")
        
    print("\n### Obfuscation Breakdown ###")
    for k, v in obf_stats.items():
        print(f"{k}: ACC={v['acc']:.4f} (TP={v['tp']} TN={v['tn']} FP={v['fp']} FN={v['fn']})")
        
    print(f"\nTotal False Positives: {len(fps)}")
    if fps:
        print("Example FP:", fps[0]["id"], fps[0]["prompt"][:50], "Risk:", fps[0].get("raw_risk_score"))
        
    print(f"\nTotal False Negatives: {len(fns)}")
    if fns:
        print("Example FN:", fns[0]["id"], fns[0]["attack_type"], fns[0]["prompt"][:50])
        
if __name__ == "__main__":
    main()
