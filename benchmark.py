import argparse
import sys
import os
import time

# Ensure we can import prompt_sentinel modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.dataset_loader import load_directory, merge_datasets
from evaluation.evaluator import evaluate_prompt
from evaluation.metrics import (
    compute_overall_metrics,
    compute_per_technique_metrics,
    compute_performance_metrics
)
from evaluation.confusion_matrix import (
    generate_overall_confusion_matrix,
    generate_binary_confusion_matrix
)
from evaluation.statistics import (
    analyze_false_positives,
    analyze_false_negatives,
    evaluate_robustness
)
from evaluation.report_generator import generate_reports
from evaluation.charts import generate_charts

def run_benchmark(dataset, is_adversarial=False):
    print(f"Loaded {len(dataset)} examples. Starting evaluation...")
    
    results = []
    
    for i, item in enumerate(dataset):
        if (i+1) % 10 == 0:
            print(f"Evaluated {i+1}/{len(dataset)}...")
            
        res = evaluate_prompt(item["prompt"])
        res["id"] = item["id"]
        res["expected"] = item["expected"]
        results.append(res)
        
    print("Evaluation completed. Computing metrics...")
    
    report_data = {
        "overall_metrics": compute_overall_metrics(results),
        "per_technique_metrics": compute_per_technique_metrics(results),
        "performance": compute_performance_metrics(results),
        "confusion_matrix": generate_overall_confusion_matrix(results),
        "binary_confusion_matrix": generate_binary_confusion_matrix(results),
        "false_positives": analyze_false_positives(results),
        "false_negatives": analyze_false_negatives(results),
        "raw_results": results
    }
    
    if is_adversarial:
        print("Computing robustness metrics on adversarial dataset...")
        robustness = evaluate_robustness(dataset, evaluate_prompt)
        report_data["robustness"] = robustness
        
    return report_data

def main():
    parser = argparse.ArgumentParser(description="PromptSentinel Benchmark Engine")
    parser.add_argument("--dataset", type=str, help="Path to the dataset directory to evaluate")
    parser.add_argument("--all", action="store_true", help="Evaluate all datasets in datasets/ directory")
    parser.add_argument("--out", type=str, default="reports", help="Output directory for reports")
    
    args = parser.parse_args()
    
    datasets = []
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets'))
    
    if args.all:
        print(f"Loading all datasets from {base_dir}...")
        benign = load_directory(os.path.join(base_dir, 'benign'))
        attacks = load_directory(os.path.join(base_dir, 'attacks'))
        adversarial = load_directory(os.path.join(base_dir, 'adversarial'))
        datasets.append(("All", merge_datasets([benign, attacks, adversarial])))
    elif args.dataset:
        path = os.path.abspath(args.dataset)
        print(f"Loading dataset from {path}...")
        ds = load_directory(path)
        datasets.append((os.path.basename(path), ds))
    else:
        # Default behavior if nothing specified?
        print("No dataset specified. Use --dataset <path> or --all.")
        sys.exit(1)
        
    for name, ds in datasets:
        if not ds:
            print(f"No dataset found for {name}. Skipping.")
            continue
            
        print(f"\n--- Running benchmark for: {name} ---")
        is_adv = "adversarial" in name.lower() or "all" in name.lower()
        report_data = run_benchmark(ds, is_adv)
        
        output_dir = os.path.join(args.out, f"{name}_{int(time.time())}")
        print(f"Generating reports in {output_dir}...")
        
        json_p, md_p, csv_p = generate_reports(report_data, output_dir)
        generate_charts(report_data, output_dir)
        
        print(f"Done! Reports saved:\n- {json_p}\n- {md_p}\n- {csv_p}")

if __name__ == "__main__":
    main()
