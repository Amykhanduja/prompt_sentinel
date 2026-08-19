import uuid
import enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Float, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from database.base import Base

class CandidateType(str, enum.Enum):
    THRESHOLD_ADJUSTMENT = "THRESHOLD_ADJUSTMENT"
    DETECTOR_REVIEW = "DETECTOR_REVIEW"
    TECHNIQUE_REVIEW = "TECHNIQUE_REVIEW"
    CLASSIFIER_REVIEW = "CLASSIFIER_REVIEW"

class CandidateStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"

class CandidateConfidence(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INSUFFICIENT = "INSUFFICIENT"

# Association table for linking LearningCandidate to Feedback
candidate_evidence_table = Table(
    "candidate_evidence",
    Base.metadata,
    Column("candidate_id", PGUUID(as_uuid=True), ForeignKey("learning_candidates.id", ondelete="CASCADE"), primary_key=True),
    Column("feedback_id", PGUUID(as_uuid=True), ForeignKey("feedback.id", ondelete="CASCADE"), primary_key=True),
)

class LearningCandidate(Base):
    __tablename__ = "learning_candidates"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_type: Mapped[CandidateType] = mapped_column(Enum(CandidateType, name="candidatetype"), nullable=False)
    target: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g. detector name
    technique: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    detector: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    proposed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    false_positive_count: Mapped[int] = mapped_column(Integer, default=0)
    false_negative_count: Mapped[int] = mapped_column(Integer, default=0)
    
    confidence: Mapped[CandidateConfidence] = mapped_column(Enum(CandidateConfidence, name="candidateconfidence"), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[CandidateStatus] = mapped_column(Enum(CandidateStatus, name="candidatestatus"), default=CandidateStatus.PENDING, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    evidence_feedback = relationship("Feedback", secondary=candidate_evidence_table)
    reviewer = relationship("User")

class LearningCandidateReview(Base):
    __tablename__ = "learning_candidate_reviews"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_candidates.id", ondelete="CASCADE"), nullable=False, unique=True)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    decision: Mapped[CandidateStatus] = mapped_column(Enum(CandidateStatus, name="candidatestatus", create_type=False), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    candidate = relationship("LearningCandidate", backref="review")
    reviewer = relationship("User")


class ApplicationStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"

class LearningConfig(Base):
    __tablename__ = "learning_configs"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    active: Mapped[bool] = mapped_column(default=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    rules = relationship("LearningRule", back_populates="config", cascade="all, delete-orphan")
    applications = relationship("LearningApplication", back_populates="config")

class LearningRule(Base):
    __tablename__ = "learning_rules"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_candidates.id", ondelete="RESTRICT"), nullable=False)
    
    rule_type: Mapped[str] = mapped_column(String, nullable=False)
    target: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    config = relationship("LearningConfig", back_populates="rules")
    candidate = relationship("LearningCandidate")

class LearningApplication(Base):
    __tablename__ = "learning_applications"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_candidates.id", ondelete="RESTRICT"), nullable=False, unique=True)
    config_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_configs.id", ondelete="RESTRICT"), nullable=False)
    applied_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    change_type: Mapped[str] = mapped_column(String, nullable=False)
    target: Mapped[str] = mapped_column(String, nullable=False)
    previous_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    new_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus, name="applicationstatus"), default=ApplicationStatus.APPLIED, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rollback_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    candidate = relationship("LearningCandidate")
    config = relationship("LearningConfig", back_populates="applications")
    applicant = relationship("User")
