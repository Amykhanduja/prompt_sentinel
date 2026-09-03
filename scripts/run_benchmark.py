import argparse
import json
import sys
import os
import time
from datetime import datetime, UTC

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from preprocessing.advanced import AdvancedPreprocessor
from preprocessing.pipeline import preprocess_prompt
from detectors.engine import run_detectors
from scoring.risk_engine import calculate_risk
from evaluation.benchmark_metrics import BenchmarkEvaluator
import config

def get_git_commit():
    import subprocess
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"

def process_sample(sample):
    start_time = time.perf_counter()
    prompt = sample["prompt"]
    
    advanced_preprocessor = AdvancedPreprocessor()
    advanced_result = advanced_preprocessor.process(prompt)
    processed = preprocess_prompt(advanced_result.normalized_text)
    processed_prompt = processed["prompt"]
    is_normalized = len(advanced_result.transformations) > 0
    
    judge_info = {}
    
    detections = run_detectors(processed_prompt, source="benchmark", judge_info=judge_info)
    
    obfuscation_detected = is_normalized and len(detections) > 0
    detection_context = {
        "normalized": is_normalized,
        "obfuscation_detected": obfuscation_detected,
        "transformations": advanced_result.transformations
    }
    
    risk = calculate_risk(detections, detection_context)
    
    end_time = time.perf_counter()
    
    # Map to BenchmarkLabel: if risk_score > 0, MALICIOUS
    is_malicious = risk["score"] > 0
    confidence_score = float(risk["score"]) / 100.0 if "score" in risk else 0.0
    
    judge_metadata = judge_info.get("judge", {})
    
    return {
        "is_malicious": is_malicious,
        "confidence_score": confidence_score,
        "raw_risk_score": risk.get("score"),
        "severity": risk.get("severity"),
        "judge_used": judge_metadata.get("judge_used", False) if isinstance(judge_metadata, dict) else False,
        "judge_decision": judge_metadata.get("decision") if isinstance(judge_metadata, dict) else None,
        "judge_latency": judge_metadata.get("latency") if isinstance(judge_metadata, dict) else None,
        "total_latency": end_time - start_time
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    
    dataset_dir = args.dataset
    manifest_path = os.path.join(dataset_dir, "manifest.json")
    samples_path = os.path.join(dataset_dir, "samples.jsonl")
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    samples = []
    with open(samples_path, "r") as f:
        for line in f:
            samples.append(json.loads(line))
            
    if args.limit:
        samples = samples[:args.limit]
        
    print(f"Loaded {len(samples)} samples. Judge Enabled: {config.LLM_JUDGE_ENABLED}")
    
    predictions = []
    failures = 0
    failed_samples = []
    
    import logging
    logging.getLogger("promptsentinel").setLevel(logging.CRITICAL)
    
    for i, s in enumerate(samples):
        if (i+1) % 100 == 0:
            print(f"Processed {i+1}/{len(samples)}...")
        try:
            pred = process_sample(s)
            predictions.append(pred)
        except Exception as e:
            print(f"Failure on {s['id']}: {e}")
            failures += 1
            failed_samples.append({"id": s["id"], "error": str(e)})
            
    print(f"Finished processing. Success: {len(predictions)}, Failures: {failures}")
    
    if len(predictions) != len(samples):
        print("Mismatched counts! Handled failures silently?")
        
    # Evaluate if all succeeded (or evaluate what succeeded)
    if failures == 0:
        # We need actual objects for the evaluator
        from evaluation.benchmark_schema import BenchmarkSample
        sample_objs = [BenchmarkSample(**s) for s in samples]
        
        evaluator = BenchmarkEvaluator(dataset_version=manifest["dataset_version"], system_version=get_git_commit())
        metrics = evaluator.evaluate(sample_objs, predictions)
        
        out_dir = os.path.join(dataset_dir, "..", "results", manifest["dataset_version"], datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(out_dir, exist_ok=True)
        
        with open(os.path.join(out_dir, "metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
            
        with open(os.path.join(out_dir, "predictions.jsonl"), "w") as f:
            for s, p in zip(samples, predictions):
                rec = {"id": s["id"], "ground_truth": s["label"], "attack_type": s["attack_type"], "difficulty": s["difficulty"], **p}
                f.write(json.dumps(rec) + "\n")
                
        print(f"Results saved to {out_dir}")
        print(f"Accuracy: {metrics['overall']['accuracy']}")
        print(f"F1: {metrics['overall']['f1']}")

if __name__ == "__main__":
    main()
