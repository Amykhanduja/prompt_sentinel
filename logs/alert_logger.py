import json
import logging
import uuid
from datetime import datetime, UTC
from database.connection import SessionLocal
from database.repositories.repositories import ScanRepository, StatisticsRepository, AlertRepository

logger = logging.getLogger("promptsentinel")

def log_alert(prompt, detections, risk, action):
    # Log archival
    archival_alert = {
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt": prompt,
        "detections": detections,
        "risk_score": risk.get("score"),
        "action": action
    }
    logger.info(json.dumps(archival_alert))
    
    db = SessionLocal()
    try:
        # Use repository to save to database
        scan_repo = ScanRepository(db)
        alert_repo = AlertRepository(db)
        
        # We need prompt length. In legacy it wasn't here, we'll calculate
        prompt_length = len(prompt) if prompt else 0
        
        scan = scan_repo.create_scan(
            prompt=prompt,
            prompt_length=prompt_length,
            risk_score=risk.get("score", 0),
            severity=risk.get("severity", "low"),
            action=action,
            source="User",
            detections=detections,
            risk_summary=risk.get("summary"),
            risk_breakdown=risk.get("breakdown")
        )
        
        # Save Alert
        alert_repo.save_alert(scan.id)
        
        # Update statistics
        update_statistics(detections, db)
        
    except Exception as e:
        logger.error(f"Failed to persist alert to database: {e}")
    finally:
        db.close()

def update_statistics(detections, db):
    try:
        stats_repo = StatisticsRepository(db)
        stats_repo.update_statistics(detections)
    except Exception as e:
        logger.error(f"Failed to update statistics in database: {e}")

