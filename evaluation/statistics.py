import copy

def analyze_false_positives(results):
    fps = []
    for res in results:
        expected = res["expected"]
        if "benign" in expected:
            detections = res.get("detections", [])
            for d in detections:
                fps.append({
                    "id": res.get("id", "unknown"),
                    "prompt": res["prompt"],
                    "detected_pt": d.get("technique"),
                    "confidence": d.get("confidence"),
                    "matched_example": d.get("matched_example", ""),
                    "reason": "Predicted as attack but expected benign"
                })
    return fps

def analyze_false_negatives(results):
    fns = []
    for res in results:
        expected = res["expected"]
        if "benign" not in expected:
            detections = res.get("detections", [])
            
            # Check if all expected PTs were missed
            detected_pts = [d.get("technique") for d in detections]
            missed = [pt for pt in expected if pt not in detected_pts]
            
            if missed:
                fns.append({
                    "id": res.get("id", "unknown"),
                    "prompt": res["prompt"],
                    "expected_pt": missed,
                    "confidence": None,
                    "nearest_semantic_match": None
                })
    return fns

def evaluate_robustness(dataset, evaluate_func):
    """
    Evaluates detection rates by disabling certain pipeline features 
    using monkeypatching.
    """
    from preprocessing.pipeline import _PIPELINE
    import semantic.semantic_engine
    
    orig_pipeline = copy.copy(_PIPELINE)
    orig_semantic = semantic.semantic_engine.SemanticEngine.detect
    
    # 1. Baseline (Full Pipeline)
    baseline_results = [evaluate_func(item["prompt"]) for item in dataset]
    baseline_detected = sum(1 for r in baseline_results if r["detections"])
    total = len(dataset)
    baseline_rate = baseline_detected / total if total > 0 else 0
    
    # 2. Before Normalization
    from preprocessing.pipeline import Normalizer
    _PIPELINE.remove(Normalizer)
    
    no_norm_results = [evaluate_func(item["prompt"]) for item in dataset]
    no_norm_detected = sum(1 for r in no_norm_results if r["detections"])
    no_norm_rate = no_norm_detected / total if total > 0 else 0
    
    _PIPELINE.append(Normalizer) # Restore (rough restore, order might be wrong, but we will fully restore later)
    
    # 3. Before Fuzzy
    from preprocessing.pipeline import FuzzyMatcher
    if FuzzyMatcher in _PIPELINE:
        _PIPELINE.remove(FuzzyMatcher)
        
    no_fuzzy_results = [evaluate_func(item["prompt"]) for item in dataset]
    no_fuzzy_detected = sum(1 for r in no_fuzzy_results if r["detections"])
    no_fuzzy_rate = no_fuzzy_detected / total if total > 0 else 0
    
    # 4. Before Semantic
    _PIPELINE.clear()
    for p in orig_pipeline:
        _PIPELINE.append(p)
        
    def mock_detect(*args, **kwargs):
        return []
    semantic.semantic_engine.SemanticEngine.detect = mock_detect
    
    no_sem_results = [evaluate_func(item["prompt"]) for item in dataset]
    no_sem_detected = sum(1 for r in no_sem_results if r["detections"])
    no_sem_rate = no_sem_detected / total if total > 0 else 0
    
    semantic.semantic_engine.SemanticEngine.detect = orig_semantic
    
    return {
        "normalization": {
            "before": no_norm_rate,
            "after": baseline_rate,
            "improvement": baseline_rate - no_norm_rate
        },
        "fuzzy": {
            "before": no_fuzzy_rate,
            "after": baseline_rate,
            "improvement": baseline_rate - no_fuzzy_rate
        },
        "semantic": {
            "before": no_sem_rate,
            "after": baseline_rate,
            "improvement": baseline_rate - no_sem_rate
        }
    }
