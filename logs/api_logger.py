import json
import logging
from datetime import datetime

logger = logging.getLogger("promptsentinel")


def log_scan_event(
    prompt_length,
    detections,
    risk_score,
    severity,
    action
):

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "scan_completed",
        "prompt_length": prompt_length,
        "detections": len(detections),
        "risk_score": risk_score,
        "severity": severity,
        "action": action
    }

    logger.info(json.dumps(event))

