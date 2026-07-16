import json
import logging
from datetime import datetime,UTC

logger = logging.getLogger("promptsentinel")


def log_scan_event(
    prompt_length,
    detections,
    risk_score,
    severity,
    action
):

    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "scan_completed",
        "prompt_length": prompt_length,
        "detections": len(detections),
        "risk_score": risk_score,
        "severity": severity,
        "action": action
    }

    logger.info(json.dumps(event))


def log_api_request(endpoint):

    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "api_request",
        "endpoint": endpoint
    }

    logger.info(json.dumps(event))


def log_api_response(endpoint, processing_time, status, scan_result=None):

    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "api_response",
        "endpoint": endpoint,
        "processing_time": round(processing_time, 4),
        "status": status
    }

    if scan_result:
        event["scan_result_action"] = scan_result.get("action")
        event["scan_result_risk"] = scan_result.get("risk_score")
        event["scan_result_severity"] = scan_result.get("severity")

    logger.info(json.dumps(event))
