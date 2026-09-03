import json
import collections

def audit():
    with open("datasets/benchmark/v1/samples.jsonl") as f:
        samples = [json.loads(line) for line in f]
        
    print(f"Total count: {len(samples)}")
    
    benign = sum(1 for s in samples if s["label"] == "benign")
    malicious = sum(1 for s in samples if s["label"] == "malicious")
    print(f"Benign/malicious ratio: {benign} / {malicious}")
    
    categories = collections.Counter(s["attack_type"] for s in samples)
    print("\nCategory counts:")
    for k, v in categories.items():
        print(f"  {k}: {v}")
        
    difficulties = collections.Counter(s["difficulty"] for s in samples)
    print("\nDifficulty counts:")
    for k, v in difficulties.items():
        print(f"  {k}: {v}")
        
    languages = collections.Counter(s["language"] for s in samples)
    print("\nLanguage counts:")
    for k, v in languages.items():
        print(f"  {k}: {v}")
        
    obfuscations = collections.Counter(s["obfuscation"] for s in samples)
    print("\nObfuscation counts:")
    for k, v in obfuscations.items():
        print(f"  {k}: {v}")
        
    ids = set()
    prompts = set()
    dup_ids = 0
    dup_prompts = 0
    for s in samples:
        if s["id"] in ids: dup_ids += 1
        ids.add(s["id"])
        
        lower_p = s["prompt"].lower().strip()
        if lower_p in prompts: dup_prompts += 1
        prompts.add(lower_p)
        
    print(f"\nDuplicate count (IDs): {dup_ids}")
    print(f"Duplicate count (Prompts): {dup_prompts}")
    
    # Missing metadata
    missing = 0
    for s in samples:
        if not all(k in s for k in ["id", "prompt", "label", "attack_type", "difficulty"]):
            missing += 1
    print(f"Missing metadata count: {missing}")

if __name__ == "__main__":
    audit()
