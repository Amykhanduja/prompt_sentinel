import time
import tracemalloc
from context.source import ScanSource
from preprocessing.pipeline import preprocess_prompt
import detectors.engine
import semantic.semantic_engine
import semantic.embeddings
try:
    import semantic.classifier
except ImportError:
    pass
try:
    import semantic.cross_encoder
except ImportError:
    pass
import fusion
from scoring.risk_engine import calculate_risk
from policies.policy_engine import evaluate_policy

def evaluate_prompt(prompt: str, source: str = ScanSource.USER):
    metrics = {
        "preprocessing_time": 0.0,
        "regex_time": 0.0,
        "semantic_time": 0.0,
        "fusion_time": 0.0,
        "embedding_time": 0.0,
        "semantic_search_time": 0.0,
        "cross_encoder_time": 0.0,
        "classifier_time": 0.0,
        "total_latency": 0.0,
        "cpu_time": 0.0,
        "peak_memory": 0
    }
    
    tracemalloc.start()
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    
    # 1. Preprocessing
    t0 = time.perf_counter()
    processed = preprocess_prompt(prompt)
    metrics["preprocessing_time"] = time.perf_counter() - t0
    
    processed_prompt = processed["prompt"]
    
    # We will use monkeypatching to get component times.
    orig_semantic = semantic.semantic_engine.detect_semantic
    orig_fuse = fusion.fuse_detections
    orig_get_embedding = semantic.embeddings.get_embedding
    
    orig_predict = None
    if hasattr(semantic, 'classifier') and hasattr(semantic.classifier, 'predict'):
        orig_predict = semantic.classifier.predict
        
    orig_predict_scores = None
    if hasattr(semantic, 'cross_encoder') and hasattr(semantic.cross_encoder, 'predict_scores'):
        orig_predict_scores = semantic.cross_encoder.predict_scores
    
    try:
        def patched_semantic(*args, **kwargs):
            ts = time.perf_counter()
            res = orig_semantic(*args, **kwargs)
            metrics["semantic_time"] = time.perf_counter() - ts
            return res
            
        def patched_fuse(*args, **kwargs):
            tf = time.perf_counter()
            res = orig_fuse(*args, **kwargs)
            metrics["fusion_time"] = time.perf_counter() - tf
            return res
            
        def patched_get_embedding(*args, **kwargs):
            te = time.perf_counter()
            res = orig_get_embedding(*args, **kwargs)
            metrics["embedding_time"] = time.perf_counter() - te
            return res
            
        if orig_predict:
            def patched_predict(*args, **kwargs):
                tp = time.perf_counter()
                res = orig_predict(*args, **kwargs)
                metrics["classifier_time"] = time.perf_counter() - tp
                return res
            semantic.classifier.predict = patched_predict
            
        if orig_predict_scores:
            def patched_predict_scores(*args, **kwargs):
                tc = time.perf_counter()
                res = orig_predict_scores(*args, **kwargs)
                metrics["cross_encoder_time"] = time.perf_counter() - tc
                return res
            semantic.cross_encoder.predict_scores = patched_predict_scores
            
        semantic.semantic_engine.detect_semantic = patched_semantic
        fusion.fuse_detections = patched_fuse
        semantic.embeddings.get_embedding = patched_get_embedding
        
        # We need to make sure detectors.engine uses the patched versions
        # Usually they are imported directly, so let's patch detectors.engine
        orig_engine_semantic = detectors.engine.detect_semantic
        orig_engine_fuse = detectors.engine.fuse_detections
        
        detectors.engine.detect_semantic = patched_semantic
        detectors.engine.fuse_detections = patched_fuse
        
        tr_start = time.perf_counter()
        detections = detectors.engine.run_detectors(processed_prompt, source)
        tr_end = time.perf_counter()
        
        metrics["regex_time"] = max(0.0, (tr_end - tr_start) - metrics["semantic_time"] - metrics["fusion_time"])
        
    finally:
        # Restore
        semantic.semantic_engine.detect_semantic = orig_semantic
        fusion.fuse_detections = orig_fuse
        semantic.embeddings.get_embedding = orig_get_embedding
        detectors.engine.detect_semantic = orig_engine_semantic
        detectors.engine.fuse_detections = orig_engine_fuse
        
        if orig_predict:
            semantic.classifier.predict = orig_predict
        if orig_predict_scores:
            semantic.cross_encoder.predict_scores = orig_predict_scores

    # Calculate semantic search time (the rest of semantic time)
    metrics["semantic_search_time"] = max(0.0, metrics["semantic_time"] - metrics["embedding_time"] - metrics["cross_encoder_time"] - metrics["classifier_time"])

    risk = calculate_risk(detections)
    policy = evaluate_policy(risk)
    
    metrics["total_latency"] = time.perf_counter() - start_wall
    metrics["cpu_time"] = time.process_time() - start_cpu
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metrics["peak_memory"] = peak
    
    return {
        "prompt": prompt,
        "processed_prompt": processed_prompt,
        "detections": detections,
        "risk_score": risk["score"],
        "severity": risk["severity"],
        "action": policy["action"],
        "metrics": metrics
    }
