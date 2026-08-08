import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from database.models.models import Scan, Detection, Alert, Statistics, ApiLog

def _normalize_confidence(raw_conf: Any) -> float:
    if isinstance(raw_conf, (int, float)):
        return float(raw_conf)
    if isinstance(raw_conf, str):
        s = raw_conf.strip()
        is_percent = s.endswith("%")
        try:
            val = float(s.strip("%"))
            if is_percent:
                return val / 100.0
            return val
        except ValueError:
            return 1.0
    return 1.0

class ScanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_scan(self, prompt: str, prompt_length: int, risk_score: int, severity: str, action: str, source: str, detections: List[Dict[str, Any]], risk_summary: dict = None, risk_breakdown: list = None, preprocessing_flags: dict = None) -> Scan:
        scan_id = uuid.uuid4()
        scan = Scan(
            id=scan_id,
            prompt=prompt,
            prompt_length=prompt_length,
            risk_score=risk_score,
            severity=severity,
            action=action,
            source=source,
            preprocessing_flags=preprocessing_flags,
            risk_summary=risk_summary,
            risk_breakdown=risk_breakdown
        )
        try:
            self.db.add(scan)
            for d in detections:
                detection = Detection(
                    scan_id=scan_id,
                    technique=d.get("technique"),
                    detector=d.get("detector"),
                    confidence=_normalize_confidence(d.get("confidence", 1.0)),
                    severity=d.get("severity", "low"),
                    evidence=d.get("evidence", [])
                )
                self.db.add(detection)
            self.db.commit()
            self.db.refresh(scan)
            return scan
        except Exception:
            self.db.rollback()
            raise
        
    def list_recent_scans(self, limit: int = 50) -> List[Scan]:
        stmt = select(Scan).order_by(desc(Scan.timestamp)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_alert(self, scan_id: uuid.UUID) -> Alert:
        try:
            alert = Alert(scan_id=scan_id)
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            return alert
        except Exception:
            self.db.rollback()
            raise

    def list_alerts(self, limit: int = 50) -> List[Alert]:
        stmt = select(Alert).order_by(desc(Alert.timestamp)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
        
    def get_all_alerts_with_scans(self) -> List[Alert]:
        # Helper for dashboard which needs all alerts for stats
        stmt = select(Alert).order_by(desc(Alert.timestamp))
        return list(self.db.execute(stmt).scalars().all())

class StatisticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_statistics(self) -> Statistics:
        try:
            stmt = select(Statistics).limit(1)
            stats = self.db.execute(stmt).scalars().first()
            if not stats:
                stats = Statistics(total_alerts=0, techniques={}, severities={})
                self.db.add(stats)
                self.db.commit()
                self.db.refresh(stats)
            return stats
        except Exception:
            self.db.rollback()
            raise

    def update_statistics(self, detections: List[Dict[str, Any]]) -> Statistics:
        stats = self.get_statistics()
        
        # update totals and dicts safely
        techniques = dict(stats.techniques) if stats.techniques else {}
        severities = dict(stats.severities) if stats.severities else {}
        
        stats.total_alerts += 1
        
        for detection in detections:
            technique = detection.get("technique")
            severity = detection.get("severity")
            
            if technique:
                techniques[technique] = techniques.get(technique, 0) + 1
            if severity:
                severities[severity] = severities.get(severity, 0) + 1
                
        try:
            stats.techniques = techniques
            stats.severities = severities
            
            self.db.commit()
            self.db.refresh(stats)
            return stats
        except Exception:
            self.db.rollback()
            raise

class ApiRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, endpoint: str, event: str, method: str = "GET", response_time: float = None, status_code: int = None, details: dict = None) -> ApiLog:
        try:
            log_entry = ApiLog(
                endpoint=endpoint,
                event=event,
                method=method,
                response_time=response_time,
                status_code=status_code,
                details=details
            )
            self.db.add(log_entry)
            self.db.commit()
            self.db.refresh(log_entry)
            return log_entry
        except Exception:
            self.db.rollback()
            raise
