import os
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

def generate_charts(report_data, output_dir):
    if plt is None:
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    overall = report_data.get("overall_metrics", {})
    per_tech = report_data.get("per_technique_metrics", {})
    results = report_data.get("raw_results", [])
    
    # Technique frequency
    techs = list(per_tech.keys())
    support = [per_tech[t]["support"] for t in techs]
    
    plt.figure(figsize=(10, 6))
    plt.bar(techs, support, color='skyblue')
    plt.title('Technique Frequency in Dataset')
    plt.xlabel('Techniques')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'technique_frequency.png'))
    plt.close()
    
    # Precision, Recall, F1 by PT
    precisions = [per_tech[t]["precision"] for t in techs]
    recalls = [per_tech[t]["recall"] for t in techs]
    f1s = [per_tech[t]["f1_score"] for t in techs]
    
    x = range(len(techs))
    width = 0.25
    
    plt.figure(figsize=(12, 6))
    plt.bar([i - width for i in x], precisions, width, label='Precision')
    plt.bar(x, recalls, width, label='Recall')
    plt.bar([i + width for i in x], f1s, width, label='F1 Score')
    plt.title('Metrics by Technique')
    plt.xlabel('Techniques')
    plt.ylabel('Score')
    plt.xticks(x, techs, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'metrics_by_pt.png'))
    plt.close()
    
    # False Positives / False Negatives by PT
    fps = [per_tech[t]["false_positive_rate"] for t in techs]
    fns = [per_tech[t]["false_negative_rate"] for t in techs]
    
    plt.figure(figsize=(12, 6))
    plt.bar([i - width/2 for i in x], fps, width, label='False Positive Rate', color='red')
    plt.bar([i + width/2 for i in x], fns, width, label='False Negative Rate', color='orange')
    plt.title('FP and FN Rates by Technique')
    plt.xlabel('Techniques')
    plt.ylabel('Rate')
    plt.xticks(x, techs, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'errors_by_pt.png'))
    plt.close()

    # Latency histogram
    latencies = [r["metrics"]["total_latency"] for r in results if "metrics" in r and "total_latency" in r["metrics"]]
    if latencies:
        plt.figure(figsize=(8, 5))
        plt.hist(latencies, bins=20, color='purple', edgecolor='black')
        plt.title('Total Latency Histogram')
        plt.xlabel('Latency (s)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'latency_histogram.png'))
        plt.close()
        
    # Risk Score histogram
    risk_scores = [r.get("risk_score", 0) for r in results]
    if risk_scores:
        plt.figure(figsize=(8, 5))
        plt.hist(risk_scores, bins=20, color='darkred', edgecolor='black')
        plt.title('Risk Score Histogram')
        plt.xlabel('Risk Score')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'risk_score_histogram.png'))
        plt.close()
        
    # Confidence histogram
    confidences = []
    for r in results:
        for d in r.get("detections", []):
            if "confidence" in d:
                confidences.append(d["confidence"])
    if confidences:
        plt.figure(figsize=(8, 5))
        plt.hist(confidences, bins=20, color='green', edgecolor='black')
        plt.title('Confidence Histogram')
        plt.xlabel('Confidence')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'confidence_histogram.png'))
        plt.close()
