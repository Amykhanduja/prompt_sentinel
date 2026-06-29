TECHNIQUE_WEIGHTS = {
    "PT-009": 30,
    "PT-013": 40,
    "PT-015": 20,
    "PT-018": 35,
    "PT-021": 20,
    "PT-023": 15,
    "PT-024": 15,
    "PT-025": 25,
    "PT-026": 30,
    "PT-027": 35,
    "PT-029": 35
}


def calculate_risk(detections):

    total_risk = 0

    for detection in detections:

        technique = detection["technique"]

        weight = TECHNIQUE_WEIGHTS.get(
            technique,
            0
        )

        confidence = detection.get(
            "confidence",
            1.0
        )

        total_risk += weight * confidence

    if total_risk >= 80:
        severity = "critical"

    elif total_risk >= 50:
        severity = "high"

    elif total_risk >= 20:
        severity = "medium"

    else:
        severity = "low"

    return {
        "score": round(total_risk, 2),
        "severity": severity
    }
