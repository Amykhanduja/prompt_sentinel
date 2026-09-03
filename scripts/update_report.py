import json
import os
import glob

def update_report():
    # Find latest results
    results_dir = "datasets/benchmark/results/v1.0.0/"
    runs = sorted(glob.glob(os.path.join(results_dir, "*")))
    if not runs:
        print("No runs found")
        return
        
    latest_run = runs[-1]
    with open(os.path.join(latest_run, "manifest.json")) as f:
        manifest = json.load(f)
    with open(os.path.join(latest_run, "metrics.json")) as f:
        metrics = json.load(f)
        
    with open("docs/reports/phase_19_3_report.md", "r") as f:
        report = f.read()
        
    # Replace TBDs
    # Executive summary
    report = report.replace("**Successful Evaluations**: TBD", f"**Successful Evaluations**: {manifest['successful_count']}")
    report = report.replace("**Failures**: TBD", f"**Failures**: {manifest['failed_count']}")
    
    overall = metrics["overall"]
    report = report.replace("**Overall Accuracy**: TBD", f"**Overall Accuracy**: {overall['accuracy']:.4f}")
    report = report.replace("**Precision**: TBD", f"**Precision**: {overall['precision']:.4f}")
    report = report.replace("**Recall**: TBD", f"**Recall**: {overall['recall']:.4f}")
    report = report.replace("**F1**: TBD", f"**F1**: {overall['f1']:.4f}")
    roc = f"{overall['roc_auc']:.4f}" if overall['roc_auc'] else "N/A"
    report = report.replace("**ROC-AUC**: TBD", f"**ROC-AUC**: {roc}")
    
    # Confusion matrix
    report = report.replace("* TP: TBD", f"* TP: {overall['tp']}")
    report = report.replace("* TN: TBD", f"* TN: {overall['tn']}")
    report = report.replace("* FP: TBD", f"* FP: {overall['fp']}")
    report = report.replace("* FN: TBD", f"* FN: {overall['fn']}")
    
    # Categories
    for cat, data in metrics["by_category"].items():
        search = f"| {cat} | TBD | TBD | TBD | TBD | TBD |"
        replace = f"| {cat} | {data['tp']+data['tn']+data['fp']+data['fn']} | {data['accuracy']:.4f} | {data['precision']:.4f} | {data['recall']:.4f} | {data['f1']:.4f} |"
        report = report.replace(search, replace)
        
    # Difficulties
    for diff, data in metrics["by_difficulty"].items():
        search = f"| {diff} | TBD | TBD | TBD | TBD | TBD |"
        replace = f"| {diff} | {data['tp']+data['tn']+data['fp']+data['fn']} | {data['accuracy']:.4f} | {data['precision']:.4f} | {data['recall']:.4f} | {data['f1']:.4f} |"
        report = report.replace(search, replace)
        
    # Performance
    lat = manifest["latency"]
    report = report.replace("**Total Runtime**: TBD", f"**Total Runtime**: {manifest['runtime']:.2f}s")
    report = report.replace("**Throughput**: TBD", f"**Throughput**: {manifest['throughput']:.2f} samples/s")
    report = report.replace("Mean (TBD), Median (TBD), p95 (TBD), p99 (TBD)", f"Mean ({lat['mean']:.4f}s), Median ({lat['median']:.4f}s), p95 ({lat['p95']:.4f}s), p99 ({lat['p99']:.4f}s)")
    report = report.replace("**Warmup Duration**: TBD", f"**Warmup Duration**: ~117s")
    
    # Reproducibility
    report = report.replace("**Git Commit**: TBD", f"**Git Commit**: {manifest['git_commit']}")
    report = report.replace("**Semantic Model**: TBD", f"**Semantic Model**: {manifest['semantic_model']}")
    report = report.replace("**CrossEncoder Model**: TBD", f"**CrossEncoder Model**: {manifest['cross_encoder_model']}")
    
    # Write back
    with open("docs/reports/phase_19_3_report.md", "w") as f:
        f.write(report)
        
    print("Report updated.")

if __name__ == "__main__":
    update_report()
