import json
import os
import random

random.seed(42)

def main():
    dataset_path = "datasets/benchmark/v1/samples.jsonl"
    samples = []
    with open(dataset_path) as f:
        for line in f:
            samples.append(json.loads(line))
            
    # Pools
    en_benign = [s for s in samples if s.get("language") == "en" and s["label"] == "benign"]
    en_malicious = [s for s in samples if s.get("language") == "en" and s["label"] == "malicious"]
    hi_benign = [s for s in samples if s.get("language") == "hi" and s["label"] == "benign"]
    hi_malicious = [s for s in samples if s.get("language") == "hi" and s["label"] == "malicious"]
    
    typo = [s for s in samples if s["attack_type"] == "typo"]
    unicode = [s for s in samples if s["attack_type"] == "unicode"]
    stored = [s for s in samples if s["attack_type"] == "stored_injection"]
    
    subset = []
    subset.extend(random.sample(en_benign, 50))
    subset.extend(random.sample(en_malicious, 50))
    subset.extend(random.sample(hi_benign, 50))
    subset.extend(random.sample(hi_malicious, 50))
    subset.extend(random.sample(typo, 50))
    subset.extend(random.sample(unicode, 50))
    subset.extend(random.sample(stored, 50))
    
    # Deduplicate by ID
    unique_subset = {s["id"]: s for s in subset}
    final_subset = list(unique_subset.values())
    
    os.makedirs("datasets/benchmark/subset", exist_ok=True)
    with open("datasets/benchmark/subset/samples.jsonl", "w") as f:
        for s in final_subset:
            f.write(json.dumps(s) + "\n")
            
    # Dummy manifest for benchmark evaluator
    manifest = {
        "version": "1.0.0-subset",
        "generated_at": "2026-09-03T00:00:00Z",
        "description": "Subset for Phase 19.5 semantic testing",
        "total_samples": len(final_subset),
        "categories": {}
    }
    with open("datasets/benchmark/subset/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Subset created with {len(final_subset)} samples.")

if __name__ == "__main__":
    main()
