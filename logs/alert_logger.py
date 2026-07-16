import json
import os
import uuid
from datetime import datetime, UTC

ALERT_FILE = "logs/alerts.json"
STATS_FILE = "logs/statistics.json"


def log_alert(prompt, detections, risk, action):

    if not os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "w") as f:
            json.dump([], f)

    with open(ALERT_FILE, "r") as f:
        alerts = json.load(f)

    new_alerts = []
    timestamp = datetime.now(UTC).isoformat()
    for d in detections:
        alert = {
            "alert_id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "prompt": prompt,
            "technique": d.get("technique"),
            "severity": d.get("severity"),
            "confidence": d.get("confidence", 1.0),
            "source": d.get("source", "unknown"),
            "detectors": d.get("detectors", []),
            "policy_decision": action,
            "risk_score": risk.get("score")
        }
        new_alerts.append(alert)

    alerts.extend(new_alerts)

    with open(ALERT_FILE, "w") as f:
        json.dump(alerts, f, indent=4)
        
    update_statistics(detections)


def update_statistics(detections):

    if not os.path.exists(STATS_FILE):

        with open(STATS_FILE, "w") as f:
            json.dump({"total_alerts": 0,"techniques": {},"severities": {} }, f, indent=4)

    with open(STATS_FILE, "r") as f:
        stats = json.load(f)

    stats["total_alerts"] += 1

    stats.setdefault("techniques", {})

    stats.setdefault("severities", {})

    for detection in detections:

        technique = detection["technique"]
        severity = detection["severity"]

        stats["techniques"][technique] = (
            stats["techniques"].get(
                technique,
                0
            ) + 1
        )

        stats["severities"][severity] = (
            stats["severities"].get(
                severity,
                0
            ) + 1
        )
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

