import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models.feedback import Feedback, FeedbackLabel
from database.models.models import Detection, Scan
from database.repositories.feedback_repository import feedback_repository

class FeedbackService:
    def create_feedback(
        self, 
        db: Session, 
        analyst_id: uuid.UUID, 
        detection_id: uuid.UUID, 
        label_str: str
    ) -> Feedback:
        # Validate label
        try:
            label = FeedbackLabel(label_str)
        except ValueError:
            raise ValueError(f"Invalid feedback label: {label_str}")

        # Fetch detection
        detection = db.query(Detection).filter(Detection.id == detection_id).first()
        if not detection:
            raise ValueError(f"Detection {detection_id} not found")

        # Fetch scan
        scan = db.query(Scan).filter(Scan.id == detection.scan_id).first()
        if not scan:
            raise ValueError(f"Scan for detection {detection_id} not found")

        # Extract values at feedback time
        technique = detection.technique
        risk_score = scan.risk_score
        severity = detection.severity
        transformations = scan.preprocessing_flags.get("transformations", []) if scan.preprocessing_flags else []
        
        # Check obfuscation
        obfuscation_detected = False
        if scan.risk_summary and scan.risk_summary.get("obfuscated") is True:
            obfuscation_detected = True

        feedback = Feedback(
            scan_id=scan.id,
            detection_id=detection.id,
            analyst_id=analyst_id,
            label=label,
            technique=technique,
            risk_score=risk_score,
            severity=severity,
            transformations=transformations,
            obfuscation_detected=obfuscation_detected
        )

        return feedback_repository.create(db, feedback)

feedback_service = FeedbackService()
