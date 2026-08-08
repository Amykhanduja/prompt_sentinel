import json
import logging
from datetime import datetime,UTC
from database.connection import SessionLocal
from database.repositories.repositories import ApiRepository

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
    
    db = SessionLocal()
    try:
        repo = ApiRepository(db)
        repo.log_event(
            endpoint="/api/v1/scan", # Approximation since we don't have it directly here
            event="scan_completed",
            details=event
        )
    except Exception as e:
        logger.error(f"Failed to log api event to db: {e}")
    finally:
        db.close()

def log_api_request(endpoint):
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "api_request",
        "endpoint": endpoint
    }
    logger.info(json.dumps(event))
    
    db = SessionLocal()
    try:
        repo = ApiRepository(db)
        repo.log_event(
            endpoint=endpoint,
            event="api_request"
        )
    except Exception as e:
        logger.error(f"Failed to log api event to db: {e}")
    finally:
        db.close()

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
    
    db = SessionLocal()
    try:
        repo = ApiRepository(db)
        repo.log_event(
            endpoint=endpoint,
            event="api_response",
            response_time=processing_time,
            status_code=status,
            details=event
        )
    except Exception as e:
        logger.error(f"Failed to log api event to db: {e}")
    finally:
        db.close()
