import math
from collections import defaultdict

def compute_classification_metrics(tp, fp, tn, fn):
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0 # TPR
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0 # TNR
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    balanced_accuracy = (recall + specificity) / 2
    
    # Matthews Correlation Coefficient
    mcc_num = (tp * tn) - (fp * fn)
    mcc_den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = mcc_num / mcc_den if mcc_den > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "specificity": specificity,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "true_positive_rate": recall,
        "true_negative_rate": specificity,
        "balanced_accuracy": balanced_accuracy,
        "mcc": mcc
    }

def compute_overall_metrics(results):
    """
    Computes overall system metrics (binary classification: benign vs attack).
    An attack is correctly detected if ANY detection is present (tp).
    If no detection is present but it's an attack (fn).
    If detection is present but it's benign (fp).
    If no detection and it's benign (tn).
    """
    tp = fp = tn = fn = 0
    
    for res in results:
        expected = res["expected"]
        predicted = [d.get("technique") for d in res.get("detections", [])]
        
        is_attack = "benign" not in expected
        has_detection = len(predicted) > 0
        
        if is_attack and has_detection:
            tp += 1
        elif is_attack and not has_detection:
            fn += 1
        elif not is_attack and has_detection:
            fp += 1
        else:
            tn += 1
            
    return compute_classification_metrics(tp, fp, tn, fn)

def compute_per_technique_metrics(results):
    technique_stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "support": 0})
    
    all_pts = set()
    for res in results:
        for pt in res["expected"]:
            if pt != "benign":
                all_pts.add(pt)
        for d in res.get("detections", []):
            if d.get("technique"):
                all_pts.add(d["technique"])
                
    for res in results:
        expected = set([p for p in res["expected"] if p != "benign"])
        predicted = set([d.get("technique") for d in res.get("detections", []) if d.get("technique")])
        
        for pt in all_pts:
            if pt in expected:
                technique_stats[pt]["support"] += 1
                
            if pt in expected and pt in predicted:
                technique_stats[pt]["tp"] += 1
            elif pt not in expected and pt in predicted:
                technique_stats[pt]["fp"] += 1
            elif pt in expected and pt not in predicted:
                technique_stats[pt]["fn"] += 1
            else:
                technique_stats[pt]["tn"] += 1
                
    per_technique = {}
    for pt, counts in technique_stats.items():
        metrics = compute_classification_metrics(counts["tp"], counts["fp"], counts["tn"], counts["fn"])
        metrics["support"] = counts["support"]
        per_technique[pt] = metrics
        
    return per_technique

def compute_performance_metrics(results):
    if not results:
        return {}
        
    metrics_keys = [
        "cpu_time", "total_latency", "peak_memory", 
        "embedding_time", "semantic_search_time", 
        "cross_encoder_time", "classifier_time", 
        "regex_time", "fusion_time", "preprocessing_time"
    ]
    
    perf = {}
    for k in metrics_keys:
        values = [r["metrics"][k] for r in results if k in r.get("metrics", {})]
        if not values:
            continue
            
        values.sort()
        n = len(values)
        
        perf[k] = {
            "average": sum(values) / n,
            "median": values[n//2] if n % 2 != 0 else (values[n//2 - 1] + values[n//2]) / 2,
            "max": values[-1],
            "min": values[0]
        }
        
    # Additional average risk score and confidence
    risk_scores = [r.get("risk_score", 0) for r in results]
    if risk_scores:
        perf["average_risk_score"] = sum(risk_scores) / len(risk_scores)
        
    confidences = []
    for r in results:
        for d in r.get("detections", []):
            if "confidence" in d:
                confidences.append(d["confidence"])
    if confidences:
        perf["average_confidence"] = sum(confidences) / len(confidences)
        
    return perf
