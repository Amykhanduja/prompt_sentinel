import uuid
import enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from database.base import Base

class FeedbackLabel(str, enum.Enum):
    CORRECT = "CORRECT"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    detection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, index=True)
    analyst_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    label: Mapped[FeedbackLabel] = mapped_column(Enum(FeedbackLabel, name="feedbacklabel"), nullable=False)
    technique: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    transformations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    obfuscation_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

    __table_args__ = (
        UniqueConstraint('detection_id', 'analyst_id', name='uq_feedback_detection_analyst'),
    )

    # Relationships
    scan = relationship("Scan")
    detection = relationship("Detection")
    analyst = relationship("User")
