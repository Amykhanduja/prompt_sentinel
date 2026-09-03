import math
from typing import List, Dict, Any
from collections import defaultdict
from evaluation.benchmark_schema import BenchmarkSample, BenchmarkLabel, BenchmarkDifficulty

def compute_confusion_matrix(y_true: List[bool], y_pred: List[bool]) -> Dict[str, float]:
    tp = fp = tn = fn = 0
    for true, pred in zip(y_true, y_pred):
        if true and pred:
            tp += 1
        elif true and not pred:
            fn += 1
        elif not true and pred:
            fp += 1
        else:
            tn += 1
            
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": total
    }

def compute_roc_auc(y_true: List[bool], y_scores: List[float]) -> float:
    """
    Computes ROC-AUC. 
    Assumes binary classification where True is positive (malicious) and False is negative (benign).
    Uses sklearn if available, otherwise returns None indicating graceful fallback.
    """
    try:
        from sklearn.metrics import roc_auc_score
        if len(set(y_true)) < 2:
            return None # ROC-AUC is undefined if only one class is present
        return roc_auc_score(y_true, y_scores)
    except ImportError:
        return None

class BenchmarkEvaluator:
    def __init__(self, dataset_version: str, evaluator_version: str = "1.0", system_version: str = "latest"):
        self.dataset_version = dataset_version
        self.evaluator_version = evaluator_version
        self.system_version = system_version
        
    def evaluate(self, samples: List[BenchmarkSample], predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        predictions: list of dicts with 'is_malicious' (bool) and optionally 'confidence_score' (float)
        """
        assert len(samples) == len(predictions), "Predictions length must match samples length"
        
        y_true = [s.label == BenchmarkLabel.MALICIOUS for s in samples]
        y_pred = [p.get("is_malicious", False) for p in predictions]
        y_scores = [p.get("confidence_score", float(p.get("is_malicious", 0.0))) for p in predictions]
        
        overall = compute_confusion_matrix(y_true, y_pred)
        overall["roc_auc"] = compute_roc_auc(y_true, y_scores)
        
        # By category
        by_category = defaultdict(list)
        for i, s in enumerate(samples):
            by_category[s.attack_type].append(i)
            
        category_metrics = {}
        for cat, indices in by_category.items():
            cat_y_true = [y_true[i] for i in indices]
            cat_y_pred = [y_pred[i] for i in indices]
            cat_y_scores = [y_scores[i] for i in indices]
            cat_metrics = compute_confusion_matrix(cat_y_true, cat_y_pred)
            cat_metrics["roc_auc"] = compute_roc_auc(cat_y_true, cat_y_scores)
            category_metrics[cat] = cat_metrics
            
        # By difficulty
        by_difficulty = defaultdict(list)
        for i, s in enumerate(samples):
            by_difficulty[s.difficulty.value].append(i)
            
        difficulty_metrics = {}
        for diff, indices in by_difficulty.items():
            diff_y_true = [y_true[i] for i in indices]
            diff_y_pred = [y_pred[i] for i in indices]
            diff_metrics = compute_confusion_matrix(diff_y_true, diff_y_pred)
            difficulty_metrics[diff] = diff_metrics
            
        return {
            "metadata": {
                "dataset_version": self.dataset_version,
                "evaluator_version": self.evaluator_version,
                "system_version": self.system_version,
                "total_samples": len(samples)
            },
            "overall": overall,
            "by_category": category_metrics,
            "by_difficulty": difficulty_metrics
        }
