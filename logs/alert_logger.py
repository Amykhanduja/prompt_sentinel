import json
import os
import uuid
from datetime import datetime, UTC

ALERT_FILE = "logs/alerts.json"
STATS_FILE = "logs/statistics.json"


def log_alert(prompt, detections, risk, action):

    alert = {
        "alert_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt": prompt,
        "detections": [d["technique"] for d in detections],
        "risk": {
            "score": risk["score"],
            "severity": risk["severity"],
            "summary": risk["summary"],
            "technique_count": risk["technique_count"],
            "average_confidence": risk["average_confidence"],
            "evidence_groups": risk["evidence_groups"],
            "breakdown": risk["breakdown"]
        },
        "severity": risk["severity"],
        "action": action
        }

    if not os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "w") as f:
            json.dump([], f)

    with open(ALERT_FILE, "r") as f:
        alerts = json.load(f)

    alerts.append(alert)

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

