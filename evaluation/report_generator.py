import json
import csv
import os
from datetime import datetime, UTC

def generate_reports(report_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    
    # JSON Report
    json_path = os.path.join(output_dir, f"report_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        report_copy = report_data.copy()
        if "raw_results" in report_copy:
            del report_copy["raw_results"]
        json.dump(report_copy, f, indent=4)
        
    # Markdown Report
    md_path = os.path.join(output_dir, f"report_{timestamp}.md")
    generate_markdown(report_data, md_path)
    
    # CSV Report
    csv_path = os.path.join(output_dir, f"report_{timestamp}.csv")
    generate_csv(report_data, csv_path)
    
    return json_path, md_path, csv_path

def generate_markdown(report_data, md_path):
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# PromptSentinel Evaluation Report\n\n")
        
        # Overall metrics
        f.write("## Overall Metrics\n")
        for k, v in report_data.get("overall_metrics", {}).items():
            f.write(f"- **{k}**: {v:.4f}\n")
            
        # Performance
        f.write("\n## Performance Metrics\n")
        for k, v in report_data.get("performance", {}).items():
            if isinstance(v, dict):
                f.write(f"- **{k}**: Avg: {v.get('average',0):.4f}, Min: {v.get('min',0):.4f}, Max: {v.get('max',0):.4f}\n")
            else:
                f.write(f"- **{k}**: {v:.4f}\n")
                
        # Per Technique
        f.write("\n## Per Technique Metrics\n")
        f.write("| Technique | F1 | Precision | Recall | Support |\n")
        f.write("|-----------|----|-----------|--------|---------|\n")
        
        per_tech = report_data.get("per_technique_metrics", {})
        sorted_tech = sorted(per_tech.items(), key=lambda x: x[1]["f1_score"], reverse=True)
        
        for t, m in sorted_tech:
            f.write(f"| {t} | {m['f1_score']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['support']} |\n")
            
        if sorted_tech:
            f.write("\n**Best Performing Techniques**:\n")
            for t, m in sorted_tech[:3]:
                f.write(f"- {t} (F1: {m['f1_score']:.4f})\n")
                
            f.write("\n**Worst Performing Techniques**:\n")
            for t, m in sorted_tech[-3:]:
                f.write(f"- {t} (F1: {m['f1_score']:.4f})\n")

        # Robustness
        if "robustness" in report_data:
            f.write("\n## Robustness Report\n")
            for k, v in report_data["robustness"].items():
                f.write(f"### {k.capitalize()}\n")
                f.write(f"- Before: {v['before']:.4f}\n")
                f.write(f"- After: {v['after']:.4f}\n")
                f.write(f"- Improvement: {v['improvement']:.4f}\n")

        # Top failures
        fps = report_data.get("false_positives", [])
        fns = report_data.get("false_negatives", [])
        
        f.write(f"\n## False Positives ({len(fps)})\n")
        for idx, fp in enumerate(fps[:10]):
            f.write(f"**{idx+1}. ID: {fp['id']}**\n")
            f.write(f"- Detected PT: {fp['detected_pt']} (Conf: {fp['confidence']})\n")
            f.write(f"- Prompt: `{fp['prompt'][:100]}...`\n")
            
        f.write(f"\n## False Negatives ({len(fns)})\n")
        for idx, fn in enumerate(fns[:10]):
            f.write(f"**{idx+1}. ID: {fn['id']}**\n")
            f.write(f"- Expected PT: {fn['expected_pt']}\n")
            f.write(f"- Prompt: `{fn['prompt'][:100]}...`\n")

def generate_csv(report_data, csv_path):
    per_tech = report_data.get("per_technique_metrics", {})
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Technique", "Accuracy", "Precision", "Recall", "F1", "Support"])
        for t, m in per_tech.items():
            writer.writerow([t, m.get("accuracy", 0), m.get("precision", 0), m.get("recall", 0), m.get("f1_score", 0), m.get("support", 0)])
