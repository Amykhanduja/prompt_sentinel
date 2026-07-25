def generate_overall_confusion_matrix(results):
    """
    Generates a confusion matrix mapping Expected -> Predicted techniques.
    """
    matrix = {}
    for res in results:
        expected = res["expected"]
        predicted = [d.get("technique") for d in res.get("detections", []) if d.get("technique")]
        
        for exp in expected:
            if exp not in matrix:
                matrix[exp] = {}
            
            if not predicted:
                matrix[exp]["Unknown"] = matrix[exp].get("Unknown", 0) + 1
            else:
                for pred in predicted:
                    matrix[exp][pred] = matrix[exp].get(pred, 0) + 1
                    
    # Also handle false positives (benign predicting attacks)
    for res in results:
        expected = res["expected"]
        predicted = [d.get("technique") for d in res.get("detections", []) if d.get("technique")]
        
        if "benign" in expected:
            for pred in predicted:
                if "benign" not in matrix:
                    matrix["benign"] = {}
                matrix["benign"][pred] = matrix["benign"].get(pred, 0) + 1
                    
    return matrix

def generate_binary_confusion_matrix(results):
    """
    Overall TP, FP, TN, FN matrix
    """
    tp = fp = tn = fn = 0
    for res in results:
        is_attack = "benign" not in res["expected"]
        has_detection = len(res.get("detections", [])) > 0
        
        if is_attack and has_detection:
            tp += 1
        elif is_attack and not has_detection:
            fn += 1
        elif not is_attack and has_detection:
            fp += 1
        else:
            tn += 1
            
    return {
        "True Positive": tp,
        "False Positive": fp,
        "True Negative": tn,
        "False Negative": fn
    }
