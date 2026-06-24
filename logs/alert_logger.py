import json
import os
import uuid
from datetime import datetime

ALERT_FILE = "logs/alerts.json"


def log_alert(prompt, detections, risk, action):

    alert = {
        "alert_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "detections": [d["technique"] for d in detections],
        "risk_score": risk["score"],
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
