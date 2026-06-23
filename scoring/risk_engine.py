TECHNIQUE_WEIGHTS = {
    "PT-009": 30,  # Instruction Override
    "PT-013": 40,  # System Prompt Extraction
    "PT-018": 35,  # DAN Jailbreak
    "PT-023": 15,  # Unicode Obfuscation
    "PT-024": 15   # Base64 Obfuscation
}

def calculate_risk(detections):

    total_risk = 0

    for detection in detections:

        technique = detection["technique"]

        total_risk += TECHNIQUE_WEIGHTS.get(
            technique,
            0
        )

    if total_risk >= 80:
        severity = "critical"

    elif total_risk >= 50:
        severity = "high"

    elif total_risk >= 20:
        severity = "medium"

    else:
        severity = "low"

    return {
        "score": total_risk,
        "severity": severity
    }
