with open("docs/reports/phase_19_3_report.md", "r") as f:
    report = f.read()

report = report.replace("**English vs Hindi**: TBD.", "**English vs Hindi**: English (Accuracy 70.44%, TP: 2115, TN: 914, FP: 86, FN: 1185) vs Hindi (Accuracy 50.00%, TP: 0, TN: 350, FP: 0, FN: 350)")
report = report.replace("**No Obfuscation vs Typo vs Unicode**: TBD.", "**No Obfuscation vs Obfuscated**: Clean (Accuracy 70.77%, TP: 1567, TN: 1264, FP: 86, FN: 1083) vs Obfuscated (Accuracy 54.80%, TP: 548, TN: 0, FP: 0, FN: 452)")

report = report.replace("**Benign False Positives**: TBD analysis.", "**Benign False Positives**: Total 86 FP. Many benign security-related queries (e.g., 'Explain authentication with examples') are incorrectly flagged by the cross-encoder as output leakage or metadata extraction due to semantic similarity.")
report = report.replace("**Malicious False Negatives**: TBD analysis. Weakest categories are TBD.", "**Malicious False Negatives**: Total 1535 FN. Weakest categories are Multilingual (Hindi entirely bypassed) and Obfuscated prompts (Unicode/Typos bypass regex and semantic embeddings entirely).")

with open("docs/reports/phase_19_3_report.md", "w") as f:
    f.write(report)
