import argparse
import json
import sys
import os
import time
from datetime import datetime, UTC

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
    
    from preprocessing.advanced import AdvancedPreprocessor
    from preprocessing.pipeline import preprocess_prompt
    from detectors.engine import run_detectors
    from scoring.risk_engine import calculate_risk
    
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
    parser.add_argument("--judge-mode", type=str, default="disabled", choices=["enabled", "disabled"])
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--embedding-model", type=str, default=None)
    parser.add_argument("--cross-encoder-model", type=str, default=None)
    parser.add_argument("--taxonomy-version", type=str, default=None)
    args = parser.parse_args()
    
    if args.taxonomy_version:
        config.TAXONOMY_VERSION = args.taxonomy_version

    if args.cross_encoder_model:
        config.CROSS_ENCODER_MODEL = args.cross_encoder_model

    if args.embedding_model:
        config.EMBEDDING_MODEL = args.embedding_model

    if args.judge_mode == "disabled":
        config.LLM_JUDGE_ENABLED = False
    
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
    
    import logging
    logging.getLogger("promptsentinel").setLevel(logging.CRITICAL)
    
    # WARMUP
    if args.warmup > 0:
        print(f"Running warmup for {args.warmup} samples...")
        warmup_start = time.perf_counter()
        for i in range(min(args.warmup, len(samples))):
            process_sample(samples[i])
        warmup_duration = time.perf_counter() - warmup_start
        print(f"Warmup completed in {warmup_duration:.2f}s")
    
    predictions = []
    failures = 0
    failed_samples = []
    
    main_start = time.perf_counter()
    
    for i, s in enumerate(samples):
        if (i+1) % 100 == 0:
            print(f"Processed {i+1}/{len(samples)}...", flush=True)
        try:
            pred = process_sample(s)
            pred["processing_status"] = "success"
            predictions.append(pred)
        except Exception as e:
            print(f"Failure on {s['id']}: {e}")
            failures += 1
            predictions.append({
                "is_malicious": False,
                "confidence_score": 0.0,
                "processing_status": "failed",
                "error": str(e),
                "total_latency": 0.0
            })
            failed_samples.append({"id": s["id"], "error": str(e)})
            
    main_duration = time.perf_counter() - main_start
    print(f"Finished processing. Success: {len(samples)-failures}, Failures: {failures}, Runtime: {main_duration:.2f}s")
    
    if failures == 0 or len(predictions) == len(samples):
        from evaluation.benchmark_schema import BenchmarkSample
        from evaluation.benchmark_metrics import BenchmarkEvaluator
        sample_objs = [BenchmarkSample(**s) for s in samples]
        
        # Only evaluate successful predictions? The runner filters them out if we want, or we keep them mapped to original
        # Let's map properly to what BenchmarkEvaluator expects. We need to pass the same length list.
        
        evaluator = BenchmarkEvaluator(dataset_version=manifest["dataset_version"], system_version=get_git_commit())
        
        # We might need to filter failed ones out before passing to evaluator
        successful_samples = []
        successful_preds = []
        for s, p in zip(sample_objs, predictions):
            if p.get("processing_status") == "success":
                successful_samples.append(s)
                successful_preds.append(p)
                
        metrics = evaluator.evaluate(successful_samples, successful_preds)
        
        out_dir = os.path.join(dataset_dir, "..", "results", manifest["dataset_version"], datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(out_dir, exist_ok=True)
        
        latencies = [p["total_latency"] for p in successful_preds]
        latencies.sort()
        mean_lat = sum(latencies)/len(latencies) if latencies else 0
        p50 = latencies[len(latencies)//2] if latencies else 0
        p95 = latencies[int(len(latencies)*0.95)] if latencies else 0
        p99 = latencies[int(len(latencies)*0.99)] if latencies else 0
        min_lat = latencies[0] if latencies else 0
        max_lat = latencies[-1] if latencies else 0
        throughput = len(successful_preds) / main_duration if main_duration > 0 else 0
        
        manifest_out = {
            "dataset_version": manifest["dataset_version"],
            "benchmark_runner_version": "v1.0.0",
            "git_commit": get_git_commit(),
            "timestamp": datetime.now(UTC).isoformat(),
            "judge_mode": args.judge_mode,
            "semantic_model": config.EMBEDDING_MODEL,
            "cross_encoder_model": config.CROSS_ENCODER_MODEL,
            "taxonomy_version": getattr(config, "TAXONOMY_VERSION", "v1"),
            "sample_count": len(samples),
            "successful_count": len(successful_preds),
            "failed_count": failures,
            "runtime": main_duration,
            "throughput": throughput,
            "latency": {
                "mean": mean_lat,
                "median": p50,
                "p95": p95,
                "p99": p99,
                "min": min_lat,
                "max": max_lat
            }
        }
        
        with open(os.path.join(out_dir, "manifest.json"), "w") as f:
            json.dump(manifest_out, f, indent=2)
            
        with open(os.path.join(out_dir, "metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
            
        with open(os.path.join(out_dir, "predictions.jsonl"), "w") as f:
            for s, p in zip(samples, predictions):
                rec = {"id": s["id"], "ground_truth": s["label"], "attack_type": s["attack_type"], "difficulty": s["difficulty"], **p}
                f.write(json.dumps(rec) + "\n")
                
        print(f"Results saved to {out_dir}")
        print(f"Accuracy: {metrics['overall']['accuracy']}")
        print(f"F1: {metrics['overall']['f1']}")
        print(f"Throughput: {throughput:.2f} samples/s")

if __name__ == "__main__":
    main()
