import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models.feedback import Feedback, FeedbackLabel

class FeedbackRepository:
    def create(self, db: Session, feedback: Feedback) -> Feedback:
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    def get_by_id(self, db: Session, feedback_id: uuid.UUID) -> Optional[Feedback]:
        return db.query(Feedback).filter(Feedback.id == feedback_id).first()

    def get_by_scan_id(self, db: Session, scan_id: uuid.UUID) -> List[Feedback]:
        return db.query(Feedback).filter(Feedback.scan_id == scan_id).all()

    def get_by_detection_id(self, db: Session, detection_id: uuid.UUID) -> List[Feedback]:
        return db.query(Feedback).filter(Feedback.detection_id == detection_id).all()

    def get_by_analyst_id(self, db: Session, analyst_id: uuid.UUID) -> List[Feedback]:
        return db.query(Feedback).filter(Feedback.analyst_id == analyst_id).all()

    def list_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
        return db.query(Feedback).offset(skip).limit(limit).all()

    def count_by_label(self, db: Session, label: FeedbackLabel) -> int:
        return db.query(Feedback).filter(Feedback.label == label).count()

feedback_repository = FeedbackRepository()
