import json
import glob
import os
from collections import defaultdict

def safe_div(a, b): return a / b if b > 0 else 0.0

def load_run(run_dir):
    preds_path = os.path.join(run_dir, "predictions.jsonl")
    manifest_path = os.path.join(run_dir, "manifest.json")
    
    with open(preds_path) as f:
        preds = [json.loads(x) for x in f]
    with open(manifest_path) as f:
        manifest = json.load(f)
        
    return preds, manifest

def analyze_preds(preds, samples):
    # Enrich
    for p in preds:
        orig = samples[p["id"]]
        p["language"] = orig.get("language", "en")
        p["attack_type"] = orig.get("attack_type")
        obf = orig.get("obfuscation", "none")
        if "unicode" in p["attack_type"]: obf = "unicode"
        elif "typo" in p["attack_type"]: obf = "typo"
        p["obf_mapped"] = obf
        
    res = defaultdict(lambda: {"tp":0, "tn":0, "fp":0, "fn":0})
    for p in preds:
        true_mal = (p["ground_truth"] == "malicious")
        pred_mal = p["is_malicious"]
        
        # Keys
        keys = ["overall"]
        keys.append(f"lang_{p['language']}")
        keys.append(f"obf_{p['obf_mapped']}")
        if p["attack_type"] == "stored_injection": keys.append("stored_injection")
        
        for k in keys:
            if true_mal and pred_mal: res[k]["tp"] += 1
            elif true_mal and not pred_mal: res[k]["fn"] += 1
            elif not true_mal and pred_mal: res[k]["fp"] += 1
            else: res[k]["tn"] += 1
            
    out = {}
    for k, v in res.items():
        rec = safe_div(v["tp"], v["tp"] + v["fn"])
        prec = safe_div(v["tp"], v["tp"] + v["fp"])
        acc = safe_div(v["tp"] + v["tn"], v["tp"] + v["tn"] + v["fp"] + v["fn"])
        out[k] = {"recall": rec, "precision": prec, "acc": acc, "tp": v["tp"], "fn": v["fn"], "fp": v["fp"], "tn": v["tn"]}
    return out

def main():
    subset_results = sorted(glob.glob("datasets/benchmark/results/1.0.0-subset/*"))
    
    samples = {}
    with open("datasets/benchmark/subset/samples.jsonl") as f:
        for line in f:
            s = json.loads(line)
            samples[s["id"]] = s
            
    for d in subset_results:
        preds, manifest = load_run(d)
        res = analyze_preds(preds, samples)
        print(f"\n=== MODEL: {manifest['semantic_model']} ===")
        print(f"Timestamp: {os.path.basename(d)}")
        for k, v in res.items():
            print(f"  {k}: Recall={v['recall']:.4f}, Prec={v['precision']:.4f} (TP={v['tp']}, FN={v['fn']}, FP={v['fp']})")

if __name__ == "__main__":
    main()
