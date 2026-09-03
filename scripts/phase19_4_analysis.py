import json
import os
import glob
from collections import defaultdict

def safe_div(a, b):
    return a / b if b > 0 else 0.0

def f1_score(prec, rec):
    return 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

def compute_metrics(tp, tn, fp, fn):
    sup = tp + tn + fp + fn
    acc = safe_div(tp + tn, sup)
    prec = safe_div(tp, tp + fp)
    rec = safe_div(tp, tp + fn)
    f1 = f1_score(prec, rec)
    return {"support": sup, "tp": tp, "tn": tn, "fp": fp, "fn": fn, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "fn_rate": safe_div(fn, sup), "fp_rate": safe_div(fp, sup)}

def main():
    results_dir = "datasets/benchmark/results/v1.0.0/"
    runs = sorted([d for d in glob.glob(os.path.join(results_dir, "*")) if os.path.isdir(d) and os.path.basename(d) != "analysis"])
    if not runs:
        print("No runs found")
        return
        
    latest_run = runs[-1]
    preds_path = os.path.join(latest_run, "predictions.jsonl")
    dataset_path = "datasets/benchmark/v1/samples.jsonl"
    
    orig_samples = {}
    with open(dataset_path, "r") as f:
        for line in f:
            s = json.loads(line)
            orig_samples[s["id"]] = s
            
    preds = []
    with open(preds_path, "r") as f:
        for line in f:
            preds.append(json.loads(line))
            
    # Enrich predictions with dataset details
    for p in preds:
        orig = orig_samples[p["id"]]
        p["prompt"] = orig.get("prompt", "")
        p["language"] = orig.get("language", "en")
        p["technique_id"] = orig.get("technique_id", "unknown")
        p["technique_name"] = orig.get("technique_name", "unknown")
        p["subtype"] = orig.get("subtype", "unknown")
        obf = orig.get("obfuscation")
        if not obf:
            if "unicode" in p["attack_type"]:
                obf = "unicode"
            elif "typo" in p["attack_type"]:
                obf = "typo"
            else:
                obf = "none"
        p["obfuscation"] = obf

    # Create analysis dir
    analysis_dir = os.path.join(results_dir, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)
    
    # 1. FP and FN
    fns = []
    fps = []
    
    for p in preds:
        true_mal = (p["ground_truth"] == "malicious")
        pred_mal = p["is_malicious"]
        if true_mal and not pred_mal:
            fns.append(p)
        elif not true_mal and pred_mal:
            fps.append(p)
            
    with open(os.path.join(analysis_dir, "false_negatives.jsonl"), "w") as f:
        for fn in fns: f.write(json.dumps(fn) + "\n")
        
    with open(os.path.join(analysis_dir, "false_positives.jsonl"), "w") as f:
        for fp in fps: f.write(json.dumps(fp) + "\n")
        
    # Grouping helpers
    def group_analysis(key_func):
        stats = defaultdict(lambda: {"tp":0, "tn":0, "fp":0, "fn":0})
        for p in preds:
            true_mal = (p["ground_truth"] == "malicious")
            pred_mal = p["is_malicious"]
            k = key_func(p)
            if true_mal and pred_mal: stats[k]["tp"] += 1
            elif true_mal and not pred_mal: stats[k]["fn"] += 1
            elif not true_mal and pred_mal: stats[k]["fp"] += 1
            else: stats[k]["tn"] += 1
        
        out = {}
        for k, v in stats.items():
            out[k] = compute_metrics(**v)
        return dict(sorted(out.items(), key=lambda x: x[1]["recall"]))

    # 2. Category analysis
    cat_out = group_analysis(lambda p: p["attack_type"])
    with open(os.path.join(analysis_dir, "category_analysis.json"), "w") as f:
        json.dump(cat_out, f, indent=2)
        
    # 3. Difficulty analysis
    diff_out = group_analysis(lambda p: p["difficulty"])
    with open(os.path.join(analysis_dir, "difficulty_analysis.json"), "w") as f:
        json.dump(diff_out, f, indent=2)
        
    # 4. Language analysis
    lang_out = group_analysis(lambda p: p["language"])
    with open(os.path.join(analysis_dir, "language_analysis.json"), "w") as f:
        json.dump(lang_out, f, indent=2)
        
    # 5. Obfuscation analysis
    obf_out = group_analysis(lambda p: p["obfuscation"])
    with open(os.path.join(analysis_dir, "obfuscation_analysis.json"), "w") as f:
        json.dump(obf_out, f, indent=2)
        
    # 6. Technique analysis
    tech_out = group_analysis(lambda p: p["technique_id"])
    with open(os.path.join(analysis_dir, "technique_analysis.json"), "w") as f:
        json.dump(tech_out, f, indent=2)
        
    print(f"Analysis complete. FNs: {len(fns)}, FPs: {len(fps)}")

if __name__ == "__main__":
    main()
