def create_scan_result(prompt: str):
    return {
        "prompt": prompt,
        "normalized_prompt": prompt,
        "detections": [],
        "risk_score": 0,
        "action": "allow"
    }
